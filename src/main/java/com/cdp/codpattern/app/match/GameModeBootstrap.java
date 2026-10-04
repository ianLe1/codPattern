package com.cdp.codpattern.app.match;

import com.phasetranscrystal.fpsmatch.core.event.RegisterFPSMapEvent;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.common.EventBusSubscriber;

/** The single FPSMatch game-type registration bridge for every installed mode. */
@EventBusSubscriber(modid = "codpattern", bus = EventBusSubscriber.Bus.GAME)
public final class GameModeBootstrap {
    private GameModeBootstrap() {
    }

    @SubscribeEvent
    public static void onRegisterFPSMap(RegisterFPSMapEvent event) {
        ModeModules.catalog().runtimeProviders().forEach(provider ->
                event.registerGameType(provider.gameType(), provider::createMap));
    }
}
