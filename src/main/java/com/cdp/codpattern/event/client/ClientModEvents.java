package com.cdp.codpattern.event.client;

import com.cdp.codpattern.client.network.ClientPacketBridgeInstaller;
import com.cdp.codpattern.client.runtime.ModeGuiOverlayContributors;
import com.mojang.logging.LogUtils;
import net.minecraft.client.Minecraft;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLClientSetupEvent;
import org.slf4j.Logger;
import net.neoforged.fml.common.EventBusSubscriber;

@EventBusSubscriber(modid = "codpattern", bus = EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public class ClientModEvents {

    private static final Logger LOGGER = LogUtils.getLogger();

    @SubscribeEvent
    public static void onClientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            ClientPacketBridgeInstaller.install();
            LOGGER.info("MINECRAFT NAME >> {}", Minecraft.getInstance().getUser().getName());
        });
    }

    @SubscribeEvent
    public static void registerGuiOverlays(net.neoforged.neoforge.client.event.RegisterGuiLayersEvent event) {
        ModeGuiOverlayContributors.registerAll(event);
    }
}
