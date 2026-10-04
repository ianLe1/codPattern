package com.cdp.codpattern.adapter.neoforge.registry;

import net.minecraft.client.Minecraft;
import net.minecraft.core.HolderLookup;

/**
 * Client-only half of {@link RegistryAccessHolder}: never load this class on a dedicated server.
 */
public final class ClientRegistryAccess {
    private ClientRegistryAccess() {
    }

    public static HolderLookup.Provider get() {
        Minecraft minecraft = Minecraft.getInstance();
        if (minecraft.level != null) {
            return minecraft.level.registryAccess();
        }
        if (minecraft.getConnection() != null) {
            return minecraft.getConnection().registryAccess();
        }
        return null;
    }
}
