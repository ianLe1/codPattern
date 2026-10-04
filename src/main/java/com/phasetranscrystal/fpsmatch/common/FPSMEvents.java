package com.phasetranscrystal.fpsmatch.common;

import com.cdp.codpattern.app.match.runtime.tool.ModeHeldToolPreviewContributors;
import com.phasetranscrystal.fpsmatch.FPSMatch;
import com.phasetranscrystal.fpsmatch.common.item.tool.ToolAccessHelper;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.common.EventBusSubscriber;

@EventBusSubscriber(modid = FPSMatch.MODID, bus = EventBusSubscriber.Bus.GAME)
public final class FPSMEvents {
    private FPSMEvents() {
    }

    @SubscribeEvent
    public static void onPlayerTickEvent(PlayerTickEvent.Post event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }

        ItemStack stack = player.getMainHandItem();
        ModeHeldToolPreviewContributors.route(player, stack, ToolAccessHelper.hasAdminAccess(player));
    }
}
