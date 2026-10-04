package com.cdp.codpattern.adapter.neoforge.network;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.network.handling.IPayloadHandler;
import net.neoforged.neoforge.network.registration.PayloadRegistrar;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.BiConsumer;
import java.util.function.Function;
import java.util.function.Supplier;

/**
 * Forge {@code SimpleChannel} 在 1.21.1 / NeoForge 上的替代实现。
 * <p>
 * 上游 8 个 registrar 用 {@code CHANNEL.messageBuilder(...).decoder(...).encoder(...)
 * .consumerMainThread(...).add()} 流式注册（实测 59 处，形态 100% 统一）。NeoForge 1.21
 * 删除了 {@code SimpleChannel}/{@code NetworkRegistry}/{@code NetworkDirection}，改为在
 * {@code RegisterPayloadHandlersEvent} 里用 {@link PayloadRegistrar} 声明式注册
 * {@code CustomPacketPayload} + {@code StreamCodec}。
 * <p>
 * 策略：完全保留旧的链式调用面，内部把旧协议包装成 NeoForge 新协议
 * （见 {@link PayloadEnvelope}）——因此 8 个 registrar 与 57 个包类都只需改 import。
 */
public final class SimpleChannel {

    private final ResourceLocation channelName;
    private final Map<Class<?>, Entry<?>> byClass = new ConcurrentHashMap<>();

    /** 注册器由 {@code RegisterPayloadHandlersEvent} 提供，在事件回调期间绑定。 */
    private PayloadRegistrar registrar;

    public SimpleChannel(ResourceLocation channelName) {
        this.channelName = channelName;
    }

    public ResourceLocation name() {
        return channelName;
    }

    /** 在 {@code RegisterPayloadHandlersEvent} 回调里绑定注册器。 */
    public void bind(PayloadRegistrar registrar) {
        this.registrar = registrar;
    }

    public <MSG> MessageBuilder<MSG> messageBuilder(Class<MSG> packetClass, int id, NetworkDirection direction) {
        return new MessageBuilder<>(this, packetClass, id, direction);
    }

    <MSG> void complete(MessageBuilder<MSG> builder) {
        PayloadRegistrar bound = this.registrar;
        if (bound == null) {
            throw new IllegalStateException("SimpleChannel.bind() must be called inside "
                    + "RegisterPayloadHandlersEvent before registering packets");
        }
        Entry<MSG> entry = new Entry<>(channelName, builder.packetClass, builder.id, builder.direction,
                builder.decoder, builder.encoder, builder.handler);
        byClass.put(builder.packetClass, entry);
        entry.register(bound);
    }

    @SuppressWarnings("unchecked")
    private <MSG> Entry<MSG> entryFor(MSG message) {
        Entry<?> entry = byClass.get(message.getClass());
        if (entry == null) {
            throw new IllegalStateException("Packet class not registered: " + message.getClass().getName());
        }
        return (Entry<MSG>) entry;
    }

    public <MSG> void sendToServer(MSG message) {
        Entry<MSG> entry = entryFor(message);
        PacketDistributor.sendToServer(entry.wrap(message));
    }

    public <MSG> void sendToPlayer(ServerPlayer player, MSG message) {
        Entry<MSG> entry = entryFor(message);
        PacketDistributor.sendToPlayer(player, entry.wrap(message));
    }

    /** 流式注册链：与上游 Forge 的 {@code SimpleChannel.messageBuilder(...)} 逐字同形。 */
    public static final class MessageBuilder<MSG> {

        private final SimpleChannel channel;
        private final Class<MSG> packetClass;
        private final int id;
        private final NetworkDirection direction;
        private Function<FriendlyByteBuf, MSG> decoder;
        private BiConsumer<MSG, FriendlyByteBuf> encoder;
        private BiConsumer<MSG, Supplier<NetworkEvent.Context>> handler;

        MessageBuilder(SimpleChannel channel, Class<MSG> packetClass, int id, NetworkDirection direction) {
            this.channel = channel;
            this.packetClass = packetClass;
            this.id = id;
            this.direction = direction;
        }

        public MessageBuilder<MSG> decoder(Function<FriendlyByteBuf, MSG> decoder) {
            this.decoder = decoder;
            return this;
        }

        public MessageBuilder<MSG> encoder(BiConsumer<MSG, FriendlyByteBuf> encoder) {
            this.encoder = encoder;
            return this;
        }

        public MessageBuilder<MSG> consumerMainThread(BiConsumer<MSG, Supplier<NetworkEvent.Context>> handler) {
            this.handler = handler;
            return this;
        }

        public void add() {
            if (decoder == null || encoder == null || handler == null) {
                throw new IllegalStateException("Incomplete packet registration for " + packetClass.getName());
            }
            channel.complete(this);
        }
    }

    /** 单个包类的注册信息 + 编解码转发。 */
    private static final class Entry<MSG> {

        private final NetworkDirection direction;
        private final Function<FriendlyByteBuf, MSG> decoder;
        private final BiConsumer<MSG, FriendlyByteBuf> encoder;
        private final BiConsumer<MSG, Supplier<NetworkEvent.Context>> handler;
        private final CustomPacketPayload.Type<PayloadEnvelope> type;

        Entry(ResourceLocation channelName, Class<MSG> packetClass, int id, NetworkDirection direction,
              Function<FriendlyByteBuf, MSG> decoder,
              BiConsumer<MSG, FriendlyByteBuf> encoder,
              BiConsumer<MSG, Supplier<NetworkEvent.Context>> handler) {
            this.direction = direction;
            this.decoder = decoder;
            this.encoder = encoder;
            this.handler = handler;
            this.type = new CustomPacketPayload.Type<>(
                    ResourceLocation.fromNamespaceAndPath(channelName.getNamespace(),
                            channelName.getPath() + "/" + id));
        }

        PayloadEnvelope wrap(MSG message) {
            return new PayloadEnvelope(type, message);
        }

        void register(PayloadRegistrar registrar) {
            StreamCodec<RegistryFriendlyByteBuf, PayloadEnvelope> codec = new StreamCodec<>() {
                @Override
                public PayloadEnvelope decode(RegistryFriendlyByteBuf buffer) {
                    return new PayloadEnvelope(type, decoder.apply(buffer));
                }

                @Override
                @SuppressWarnings("unchecked")
                public void encode(RegistryFriendlyByteBuf buffer, PayloadEnvelope value) {
                    encoder.accept((MSG) value.body(), buffer);
                }
            };
            IPayloadHandler<PayloadEnvelope> neoHandler = (payload, context) -> {
                @SuppressWarnings("unchecked")
                MSG message = (MSG) payload.body();
                handler.accept(message, () -> new NetworkEvent.Context(context));
            };
            switch (direction) {
                case PLAY_TO_SERVER -> registrar.playToServer(type, codec, neoHandler);
                case PLAY_TO_CLIENT -> registrar.playToClient(type, codec, neoHandler);
            }
        }
    }
}
