package com.cdp.codpattern.event;

import com.cdp.codpattern.CodPatternConstants;
import com.cdp.codpattern.core.refit.AttachmentEditSessionManager;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.server.ServerLifecycleHooks;
import net.neoforged.fml.common.EventBusSubscriber;

@EventBusSubscriber(modid = CodPatternConstants.MOD_ID, bus = EventBusSubscriber.Bus.GAME)
public class AttachmentEditSessionServerEvents {

    @SubscribeEvent
    public static void onServerTick(ServerTickEvent.Post event) {
        if (ServerLifecycleHooks.getCurrentServer() == null) {
            return;
        }
        AttachmentEditSessionManager.tickTimeouts(ServerLifecycleHooks.getCurrentServer());
    }

    @SubscribeEvent
    public static void onPlayerLoggedOut(PlayerEvent.PlayerLoggedOutEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || event.getEntity().level().isClientSide) {
            return;
        }
        AttachmentEditSessionManager.abortSession(player, "logout", false);
    }

    @SubscribeEvent
    public static void onPlayerChangedDimension(PlayerEvent.PlayerChangedDimensionEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || event.getEntity().level().isClientSide) {
            return;
        }
        AttachmentEditSessionManager.abortSession(player, "dimension_changed");
    }

    @SubscribeEvent
    public static void onPlayerDeath(LivingDeathEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || event.getEntity().level().isClientSide) {
            return;
        }
        AttachmentEditSessionManager.abortSession(player, "death");
    }
}
