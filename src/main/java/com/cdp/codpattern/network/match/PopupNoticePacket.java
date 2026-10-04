package com.cdp.codpattern.network.match;

import com.cdp.codpattern.network.handler.ClientPacketBridge;
import com.cdp.codpattern.adapter.neoforge.network.PayloadBuf;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import com.cdp.codpattern.adapter.neoforge.network.NetworkEvent;

import java.util.function.Supplier;

public class PopupNoticePacket {
    private final Component title;
    private final Component message;

    public PopupNoticePacket(Component title, Component message) {
        this.title = title == null ? Component.translatable("screen.codpattern.popup.title") : title;
        this.message = message == null ? Component.empty() : message;
    }

    public PopupNoticePacket(FriendlyByteBuf buf) {
        this.title = PayloadBuf.readComponent(buf);
        this.message = PayloadBuf.readComponent(buf);
    }

    public void encode(FriendlyByteBuf buf) {
        PayloadBuf.writeComponent(buf, title);
        PayloadBuf.writeComponent(buf, message);
    }

    public static PopupNoticePacket decode(FriendlyByteBuf buf) {
        return new PopupNoticePacket(buf);
    }

    public void handle(Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() -> ClientPacketBridge.popupNotice(title, message));
        ctx.get().setPacketHandled(true);
    }
}
