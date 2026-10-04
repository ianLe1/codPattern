package com.cdp.codpattern.client.bootstrap;

import com.cdp.codpattern.CodPatternConstants;
import com.cdp.codpattern.client.extension.ModeGuiOverlayContributor;
import com.cdp.codpattern.client.extension.ModeHudReplacementPolicy;
import com.cdp.codpattern.client.gui.overlay.TdmHudOverlay;
import com.cdp.codpattern.client.runtime.ModeGuiOverlayContributors;
import com.cdp.codpattern.client.runtime.ModeHudReplacementPolicies;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;

import java.util.concurrent.atomic.AtomicBoolean;

/** Client-only core contributions installed during combined mod construction. */
public final class CoreClientBootstrap {
    private static final AtomicBoolean INSTALLED = new AtomicBoolean();

    private CoreClientBootstrap() {
    }

    public static void install() {
        if (!INSTALLED.compareAndSet(false, true)) {
            return;
        }
        ModeGuiOverlayContributors.register(new ModeGuiOverlayContributor() {
            @Override
            public String id() {
                return "tdm_hud";
            }

            @Override
            public int order() {
                return 10;
            }

            @Override
            public void register(RegisterGuiLayersEvent event) {
                event.registerAboveAll(
                        ResourceLocation.fromNamespaceAndPath(CodPatternConstants.MOD_ID, "tdm_hud"),
                        TdmHudOverlay.INSTANCE);
            }
        });
        ModeHudReplacementPolicies.register(new ModeHudReplacementPolicy() {
            @Override
            public String id() {
                return "tdm";
            }

            @Override
            public int order() {
                return 10;
            }

            @Override
            public boolean shouldReplaceVanillaPlayerHud() {
                return TdmHudOverlay.shouldReplaceVanillaPlayerHud();
            }
        });
    }
}
