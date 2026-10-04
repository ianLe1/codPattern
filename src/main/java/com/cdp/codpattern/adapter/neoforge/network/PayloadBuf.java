package com.cdp.codpattern.adapter.neoforge.network;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.ComponentSerialization;
import net.minecraft.world.item.ItemStack;

/**
 * 1.20.1 {@code FriendlyByteBuf#writeComponent/readComponent/writeItem/readItem}
 * 在 1.21.1 均被删除，这里给出等价替身。
 */
public final class PayloadBuf {
    private PayloadBuf() {
    }

    /** 文本组件走「无需 registry 上下文」的可信流编解码器。 */
    public static void writeComponent(FriendlyByteBuf buf, Component component) {
        ComponentSerialization.TRUSTED_CONTEXT_FREE_STREAM_CODEC.encode(buf, component);
    }

    public static Component readComponent(FriendlyByteBuf buf) {
        return ComponentSerialization.TRUSTED_CONTEXT_FREE_STREAM_CODEC.decode(buf);
    }

    /**
     * 本 mod 的全部负载都经 {@link SimpleChannel} 注册，其 StreamCodec 绑定在
     * {@link RegistryFriendlyByteBuf} 上，因此运行时这里的强转恒成立（不成立即说明有第三方
     * 直接调用了包体的 encode/decode，属于编程错误，直接抛错比静默写脏数据好）。
     */
    private static RegistryFriendlyByteBuf registry(FriendlyByteBuf buf) {
        if (buf instanceof RegistryFriendlyByteBuf registryBuf) {
            return registryBuf;
        }
        throw new IllegalStateException("expected RegistryFriendlyByteBuf, got " + buf.getClass().getName());
    }

    public static void writeItem(FriendlyByteBuf buf, ItemStack stack) {
        ItemStack.OPTIONAL_STREAM_CODEC.encode(registry(buf), stack);
    }

    public static ItemStack readItem(FriendlyByteBuf buf) {
        return ItemStack.OPTIONAL_STREAM_CODEC.decode(registry(buf));
    }
}
