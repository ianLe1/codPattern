package com.cdp.codpattern.event;

import com.cdp.codpattern.CodPatternConstants;
import com.cdp.codpattern.app.tdm.service.RoomFoodLockService;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.event.entity.living.LivingHealEvent;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.common.EventBusSubscriber;

@EventBusSubscriber(modid = CodPatternConstants.MOD_ID, bus = EventBusSubscriber.Bus.GAME)
public final class RoomFoodLockEventHandler {
    private RoomFoodLockEventHandler() {
    }

    @SubscribeEvent
    public static void onPlayerTick(PlayerTickEvent.Post event) {
        if (event.getEntity().level().isClientSide
                || !(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        if (!RoomFoodLockService.isRoomPlayer(player)) {
            return;
        }
        RoomFoodLockService.enforce(player);
    }

    @SubscribeEvent(priority = EventPriority.HIGHEST)
    public static void onLivingHeal(LivingHealEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        if (RoomFoodLockService.shouldBlockHeal(player)) {
            event.setCanceled(true);
        }
    }
}
