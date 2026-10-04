package com.cdp.codpattern.event.client;

import com.cdp.codpattern.CodPatternConstants;
import com.cdp.codpattern.client.ClientTdmState;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.contents.TranslatableContents;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.neoforge.client.event.ClientChatReceivedEvent;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.common.EventBusSubscriber;

@EventBusSubscriber(modid = CodPatternConstants.MOD_ID, value = Dist.CLIENT, bus = EventBusSubscriber.Bus.GAME)
public final class ClientDeathMessageFilterHandler {
    private ClientDeathMessageFilterHandler() {
    }

    @SubscribeEvent
    public static void onSystemChatReceived(ClientChatReceivedEvent.System event) {
        if (event == null || event.isOverlay() || !ClientTdmState.hasRoomContext()) {
            return;
        }
        if (isVanillaDeathMessage(event.getMessage())) {
            event.setCanceled(true);
        }
    }

    private static boolean isVanillaDeathMessage(Component message) {
        if (message == null) {
            return false;
        }

        if (message.getContents() instanceof TranslatableContents translatableContents
                && translatableContents.getKey().startsWith("death.")) {
            return true;
        }

        for (Component sibling : message.getSiblings()) {
            if (isVanillaDeathMessage(sibling)) {
                return true;
            }
        }

        return false;
    }
}
