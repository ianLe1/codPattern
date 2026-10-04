package com.cdp.codpattern.event.client;

import com.cdp.codpattern.CodPatternConstants;
import com.cdp.codpattern.client.ClientTdmState;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.world.phys.Vec3;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.neoforge.client.event.MovementInputUpdateEvent;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.common.EventBusSubscriber;

@EventBusSubscriber(modid = CodPatternConstants.MOD_ID, value = Dist.CLIENT, bus = EventBusSubscriber.Bus.GAME)
public final class TdmWarmupMovementLockHandler {
    private TdmWarmupMovementLockHandler() {
    }

    @SubscribeEvent
    public static void onMovementInput(MovementInputUpdateEvent event) {
        if (!(event.getEntity() instanceof LocalPlayer player)) {
            return;
        }
        if (!shouldLockMovement()) {
            return;
        }

        event.getInput().leftImpulse = 0.0f;
        event.getInput().forwardImpulse = 0.0f;
        event.getInput().up = false;
        event.getInput().down = false;
        event.getInput().left = false;
        event.getInput().right = false;
        event.getInput().jumping = false;
        event.getInput().shiftKeyDown = false;
        player.setSprinting(false);
        player.setDeltaMovement(Vec3.ZERO);
    }

    private static boolean shouldLockMovement() {
        if (ClientTdmState.isDead()) {
            return true;
        }
        return ClientTdmState.hasRoomContext() && "WARMUP".equals(ClientTdmState.currentPhase());
    }
}
