package com.cdp.codpattern.client.extension;

import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;

/** Client-only overlay registration contribution. */
public interface ModeGuiOverlayContributor {
    String id();

    default int order() {
        return 0;
    }

    void register(RegisterGuiLayersEvent event);
}
