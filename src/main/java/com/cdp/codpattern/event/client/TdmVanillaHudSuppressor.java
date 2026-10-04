package com.cdp.codpattern.event.client;

import com.cdp.codpattern.CodPatternConstants;
import com.cdp.codpattern.client.runtime.ModeHudReplacementPolicies;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.neoforge.client.event.RenderGuiLayerEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.Mod;

import java.util.Set;
import net.neoforged.fml.common.EventBusSubscriber;

@EventBusSubscriber(modid = CodPatternConstants.MOD_ID, value = Dist.CLIENT, bus = EventBusSubscriber.Bus.GAME)
public final class TdmVanillaHudSuppressor {
    private static final Set<ResourceLocation> SUPPRESSED_OVERLAY_IDS = Set.of(
            VanillaGuiLayers.HOTBAR,
            VanillaGuiLayers.PLAYER_HEALTH,
            VanillaGuiLayers.EXPERIENCE_BAR,
            VanillaGuiLayers.FOOD_LEVEL);

    private TdmVanillaHudSuppressor() {
    }

    @SubscribeEvent
    public static void onRenderGuiLayer(RenderGuiLayerEvent.Pre event) {
        if (!ModeHudReplacementPolicies.shouldReplaceVanillaPlayerHud()) {
            return;
        }
        if (SUPPRESSED_OVERLAY_IDS.contains(event.getName())) {
            event.setCanceled(true);
        }
    }
}
