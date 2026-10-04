package com.cdp.codpattern.event.client;

import com.cdp.codpattern.CodPatternConstants;
import com.cdp.codpattern.client.ClientTdmState;
import com.cdp.codpattern.client.TdmCombatMarkerTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.world.entity.player.Player;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.neoforge.client.event.RenderNameTagEvent;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.Mod;

import java.util.UUID;
import net.neoforged.fml.common.EventBusSubscriber;

@EventBusSubscriber(modid = CodPatternConstants.MOD_ID, value = Dist.CLIENT, bus = EventBusSubscriber.Bus.GAME)
public final class TdmNameTagVisibilityHandler {
    private TdmNameTagVisibilityHandler() {
    }

    @SubscribeEvent
    public static void onRenderNameTag(RenderNameTagEvent event) {
        if (!(event.getEntity() instanceof Player trackedPlayer)) {
            return;
        }

        String phase = ClientTdmState.currentPhase();
        if (!"WARMUP".equals(phase) && !"PLAYING".equals(phase)) {
            return;
        }

        Minecraft minecraft = Minecraft.getInstance();
        LocalPlayer localPlayer = minecraft.player;
        ClientLevel level = minecraft.level;
        if (localPlayer == null || level == null) {
            return;
        }

        TdmCombatMarkerTracker.TeamVisionSnapshot snapshot = TdmCombatMarkerTracker.INSTANCE.snapshot();
        if (!snapshot.hasLocalTeam()
                || snapshot.localPlayerId() == null
                || !snapshot.localPlayerId().equals(localPlayer.getUUID())) {
            return;
        }

        UUID trackedPlayerId = trackedPlayer.getUUID();
        if (trackedPlayerId.equals(localPlayer.getUUID())
                || !snapshot.teamByPlayer().containsKey(trackedPlayerId)) {
            return;
        }

        event.setCanRender(net.neoforged.neoforge.common.util.TriState.FALSE);
    }
}
