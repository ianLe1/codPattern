package com.cdp.codpattern.adapter.forge.network;

import com.cdp.codpattern.adapter.neoforge.network.SimpleChannel;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import net.neoforged.neoforge.network.registration.PayloadRegistrar;

public final class ModNetworkChannel {
    /** 协议版本号，沿用上游 "14"；现在作为 {@code PayloadRegistrar} 的通道版本。 */
    private static final String PROTOCOL_VERSION = "14";

    /** 通道名沿用上游 "codpattern:main"；实现换成 1.21.1 的垫片（见 adapter.neoforge.network）。 */
    static final SimpleChannel CHANNEL =
            new SimpleChannel(ResourceLocation.fromNamespaceAndPath("codpattern", "main"));

    private static int packetId = 0;

    private ModNetworkChannel() {
    }

    public static int nextMessageId() {
        return packetId++;
    }

    public static SimpleChannel channel() {
        return CHANNEL;
    }

    /**
     * NeoForge 1.21 起，负载注册必须发生在这个 mod bus 事件回调内（不再是 FMLCommonSetupEvent）。
     * 由 {@code CoreBootstrap} 以 {@code modEventBus.addListener(ModNetworkChannel::onRegisterPayloadHandlers)} 挂载。
     */
    public static void onRegisterPayloadHandlers(RegisterPayloadHandlersEvent event) {
        PayloadRegistrar registrar = event.registrar(PROTOCOL_VERSION);
        CHANNEL.bind(registrar);
        register();
    }

    public static void register() {
        BackpackPacketRegistrar.register();
        ThrowablePacketRegistrar.register();
        RefitPacketRegistrar.register();
        ModeRoomPacketRegistrar.registerInitialRoomPackets();
        ModeRoomPacketRegistrar.registerRoomFeedbackPackets();
        ModeRuntimePacketRegistrar.register();
        ModeRoomPacketRegistrar.registerLateRoomPackets();
        FpsmPacketRegistrar.register();
        MapAdminPacketRegistrar.register();
    }

    public static <MSG> void sendToServer(MSG message) {
        CHANNEL.sendToServer(message);
    }

    public static <MSG> void sendToPlayer(MSG message, ServerPlayer player) {
        CHANNEL.sendToPlayer(player, message);
    }
}
