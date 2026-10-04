package com.cdp.codpattern.adapter.neoforge.network;

import net.minecraft.network.protocol.common.custom.CustomPacketPayload;

/**
 * 把上游那些「裸 POJO」包类（实例 {@code encode(FriendlyByteBuf)}、静态 {@code decode}、
 * 实例 {@code handle(Supplier<NetworkEvent.Context>)}）包装成 NeoForge 1.21 要求的
 * {@link CustomPacketPayload}。
 * <p>
 * 之所以能做到「零改包体」：上游的 encode/decode 方法体在 1.21.1 上原本就能编译通过
 * （只动 import），因此这里只在外面套一层壳，把字节流原样转发，不重新编解码。
 */
public final class PayloadEnvelope implements CustomPacketPayload {

    private final Type<PayloadEnvelope> type;
    private final Object body;

    public PayloadEnvelope(Type<PayloadEnvelope> type, Object body) {
        this.type = type;
        this.body = body;
    }

    /** 实际承载的上游包对象。 */
    public Object body() {
        return body;
    }

    @Override
    public Type<PayloadEnvelope> type() {
        return type;
    }
}
