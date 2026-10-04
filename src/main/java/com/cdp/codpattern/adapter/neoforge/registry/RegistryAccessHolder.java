package com.cdp.codpattern.adapter.neoforge.registry;

import net.minecraft.core.HolderLookup;
import net.minecraft.server.MinecraftServer;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.server.ServerLifecycleHooks;

/**
 * 1.20.1 -> 1.21.1 port shim: resolves a {@link HolderLookup.Provider} for item (de)serialization.
 *
 * <p>In 1.20.1 {@code ItemStack#save(CompoundTag)} / {@code ItemStack#of(CompoundTag)} carried no
 * registry context; 1.21.1 requires a provider holding the item and data-component registries.
 * This is an engineering shim, not domain logic: it prefers the running server and falls back to
 * the client level on a physical client. {@link ClientRegistryAccess} is only touched inside a
 * {@code Dist.CLIENT} guard so a dedicated server never loads a class referencing client types.</p>
 */
public final class RegistryAccessHolder {
    private RegistryAccessHolder() {
    }

    public static HolderLookup.Provider get() {
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        if (server != null) {
            return server.registryAccess();
        }
        if (FMLEnvironment.dist == Dist.CLIENT) {
            HolderLookup.Provider provider = ClientRegistryAccess.get();
            if (provider != null) {
                return provider;
            }
        }
        throw new IllegalStateException("No registry access available for item serialization");
    }
}
