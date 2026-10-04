package com.cdp.codpattern.adapter.neoforge.network;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/**
 * Forge {@code NetworkEvent.Context} 在 1.21.1 / NeoForge 上的等价垫片。
 * <p>
 * 上游 57 个包类的 {@code handle(Supplier<NetworkEvent.Context>)} 里实际只用到三个成员：
 * {@code enqueueWork(Runnable)}、{@code setPacketHandled(boolean)}、{@code getSender()}。
 * NeoForge 1.21 删除了 {@code SimpleChannel}/{@code NetworkEvent}，改用
 * {@code CustomPacketPayload} + {@link IPayloadContext}。
 * <p>
 * 这里保留旧调用面，让包类只需替换一行 import 即可，不必逐个重写。
 */
public final class NetworkEvent {

    private NetworkEvent() {
    }

    public static final class Context {

        private final IPayloadContext neoContext;

        public Context(IPayloadContext neoContext) {
            this.neoContext = neoContext;
        }

        /** 在主线程执行；语义与 Forge 的 {@code Context#enqueueWork} 一致。 */
        public void enqueueWork(Runnable work) {
            neoContext.enqueueWork(work);
        }

        /**
         * 兼容旧代码的空实现。
         * <p>
         * Forge 需要显式声明「已处理」以阻止分发器继续走默认逻辑；NeoForge 的载荷分发器
         * 自行管理完成状态，无需（也不支持）手动设置。
         */
        public void setPacketHandled(boolean handled) {
            // no-op：NeoForge 自动接管
        }

        /** C2S 包返回发送者；在客户端（S2C 包）上返回 {@code null}，与旧行为一致。 */
        public ServerPlayer getSender() {
            Player player = neoContext.player();
            return player instanceof ServerPlayer serverPlayer ? serverPlayer : null;
        }
    }
}
