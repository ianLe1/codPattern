package com.cdp.codpattern.event.client;

import com.cdp.codpattern.CodPatternConstants;
import com.cdp.codpattern.client.ClientTdmState;
import com.cdp.codpattern.config.backpack.BackpackClientCache;
import com.cdp.codpattern.config.weaponfilter.WeaponFilterClientCache;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.neoforge.client.event.ClientPlayerNetworkEvent;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.common.EventBusSubscriber;

@EventBusSubscriber(modid = CodPatternConstants.MOD_ID, value = Dist.CLIENT, bus = EventBusSubscriber.Bus.GAME)
public final class ClientConnectionStateHandler {
    private ClientConnectionStateHandler() {
    }

    @SubscribeEvent
    public static void onClientLogout(ClientPlayerNetworkEvent.LoggingOut event) {
        ClientTdmState.resetMatchState();
        BackpackClientCache.clear();
        WeaponFilterClientCache.clear();
        ThrowableClientInputHandler.reset();
    }
}
