package com.cdp.codpattern.app.tdm.service;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

public final class WarmupMovementLockService {
    private static final ResourceLocation MOVEMENT_LOCK_ID =
            ResourceLocation.fromNamespaceAndPath("codpattern", "warmup_movement_lock");
    private static final AttributeModifier MOVEMENT_LOCK = new AttributeModifier(
            MOVEMENT_LOCK_ID,
            -1.0D,
            AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);

    private WarmupMovementLockService() {
    }

    public static void lock(ServerPlayer player) {
        if (player == null) {
            return;
        }
        AttributeInstance movementSpeed = player.getAttribute(Attributes.MOVEMENT_SPEED);
        if (movementSpeed == null || movementSpeed.hasModifier(MOVEMENT_LOCK_ID)) {
            return;
        }
        movementSpeed.addTransientModifier(MOVEMENT_LOCK);
        player.setSprinting(false);
    }

    public static void unlock(ServerPlayer player) {
        if (player == null) {
            return;
        }
        AttributeInstance movementSpeed = player.getAttribute(Attributes.MOVEMENT_SPEED);
        if (movementSpeed == null) {
            return;
        }
        movementSpeed.removeModifier(MOVEMENT_LOCK_ID);
    }
}
