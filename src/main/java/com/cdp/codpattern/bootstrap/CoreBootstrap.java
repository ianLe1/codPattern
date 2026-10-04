package com.cdp.codpattern.bootstrap;

import com.cdp.codpattern.adapter.forge.network.ModNetworkChannel;
import com.cdp.codpattern.app.match.ModeModules;
import com.cdp.codpattern.app.tdm.TdmModeModule;
import com.cdp.codpattern.client.bootstrap.CoreClientBootstrap;
import com.cdp.codpattern.command.CommandRegistration;
import com.cdp.codpattern.core.throwable.ThrowableInventoryCapability;
import com.cdp.codpattern.config.tdm.CodTdmConfig;
import com.phasetranscrystal.fpsmatch.common.item.FPSMCreativeModeTabRegister;
import com.phasetranscrystal.fpsmatch.common.item.FPSMItemRegister;
import com.cdp.codpattern.adapter.neoforge.nbt.ItemNbt;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.server.ServerStartingEvent;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;

import java.util.concurrent.atomic.AtomicBoolean;

/** Future-main bootstrap with no installed-mode implementation dependencies. */
public final class CoreBootstrap {
    private static final AtomicBoolean INSTALLED = new AtomicBoolean();

    private CoreBootstrap() {
    }

    public static void install(IEventBus modEventBus) {
        if (!INSTALLED.compareAndSet(false, true)) {
            return;
        }
        ModeModules.contribute(TdmModeModule.INSTANCE);
        if (FMLEnvironment.dist == Dist.CLIENT) {
            CoreClientBootstrap.install();
        }

        modEventBus.addListener(CoreBootstrap::onCommonSetup);
        // NeoForge 1.21：负载注册必须在 mod bus 的 RegisterPayloadHandlersEvent 阶段完成。
        modEventBus.addListener(ModNetworkChannel::onRegisterPayloadHandlers);
        modEventBus.addListener(FPSMItemRegister::onBuildCreativeModeTabContents);
        FPSMCreativeModeTabRegister.CREATIVE_MODE_TABS.register(modEventBus);
        FPSMItemRegister.ITEMS.register(modEventBus);
        ThrowableInventoryCapability.ATTACHMENT_TYPES.register(modEventBus);

        NeoForge.EVENT_BUS.addListener(CoreBootstrap::onServerStarting);
        NeoForge.EVENT_BUS.addListener(CoreBootstrap::onRegisterCommands);
    }

    private static void onCommonSetup(FMLCommonSetupEvent event) {
        event.enqueueWork(ModeModules::freeze);
    }

    private static void onServerStarting(ServerStartingEvent event) {
        CodTdmConfig.load(event.getServer());
    }

    private static void onRegisterCommands(RegisterCommandsEvent event) {
        CommandRegistration.register(event.getDispatcher());
    }
}
