package com.cdp.codpattern.core.throwable;

import com.cdp.codpattern.CodPatternConstants;
import net.minecraft.world.entity.player.Player;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

import java.util.Optional;

/**
 * Player-held throwable inventory, stored as a NeoForge data attachment.
 *
 * <p>NeoForge 1.21.1 removed the old capability model ({@code Capability},
 * {@code CapabilityManager}, {@code ICapabilityProvider}, {@code LazyOptional},
 * {@code AttachCapabilitiesEvent}). Data attachments are the replacement, and the
 * public accessor below keeps its original shape so callers are unaffected.</p>
 */
public final class ThrowableInventoryCapability {
    public static final DeferredRegister<AttachmentType<?>> ATTACHMENT_TYPES =
            DeferredRegister.create(NeoForgeRegistries.Keys.ATTACHMENT_TYPES, CodPatternConstants.MOD_ID);

    public static final DeferredHolder<AttachmentType<?>, AttachmentType<ThrowableInventoryState>> THROWABLE_INVENTORY =
            ATTACHMENT_TYPES.register("throwable_inventory",
                    () -> AttachmentType.serializable(ThrowableInventoryState::new).build());

    private ThrowableInventoryCapability() {
    }

    public static Optional<ThrowableInventoryState> get(Player player) {
        if (player == null) {
            return Optional.empty();
        }
        return Optional.of(player.getData(THROWABLE_INVENTORY));
    }
}
