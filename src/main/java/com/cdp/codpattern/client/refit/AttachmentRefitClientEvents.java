package com.cdp.codpattern.client.refit;

import com.cdp.codpattern.CodPatternConstants;
import com.cdp.codpattern.compat.tacz.client.CodGunRefitScreen;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.neoforge.client.event.ScreenEvent;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.common.EventBusSubscriber;

@EventBusSubscriber(modid = CodPatternConstants.MOD_ID, value = Dist.CLIENT)
public class AttachmentRefitClientEvents {

    @SubscribeEvent
    public static void onClientTick(ClientTickEvent.Post event) {
        AttachmentRefitClientState.tryOpenIfReady();
    }

    @SubscribeEvent
    public static void onScreenClosing(ScreenEvent.Closing event) {
        if (event.getScreen() instanceof CodGunRefitScreen) {
            AttachmentRefitClientState.onRefitScreenClosed();
        }
    }
}
