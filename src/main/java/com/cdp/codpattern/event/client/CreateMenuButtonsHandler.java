package com.cdp.codpattern.event.client;

import com.cdp.codpattern.client.gui.refit.BackpackButton;
import com.cdp.codpattern.client.gui.refit.ModeRoomButton;
import net.minecraft.client.gui.screens.PauseScreen;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.neoforge.client.event.ScreenEvent;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.common.EventBusSubscriber;

@EventBusSubscriber(modid = "codpattern", value = Dist.CLIENT, bus = EventBusSubscriber.Bus.GAME)
public class CreateMenuButtonsHandler {

    @SubscribeEvent
    public static void addButtononPauseScreen(ScreenEvent.Init.Post event) {
        var screen = event.getScreen();
        if (!(screen instanceof PauseScreen))
            return;

        // 添加背包按键
        event.addListener(BackpackButton.create(screen.width / 2 - 102, screen.height - 24, 204, 16));

        // 添加模式房间按键
        event.addListener(ModeRoomButton.create(screen.width / 2 - 102, screen.height - 48, 204, 16));
    }
}
