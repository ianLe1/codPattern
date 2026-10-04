package com.cdp.codpattern;

import com.cdp.codpattern.bootstrap.CoreBootstrap;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;

@Mod(CodPatternConstants.MOD_ID)
public class CodPattern {
    public static final String MODID = CodPatternConstants.MOD_ID;

    public CodPattern(IEventBus modEventBus) {
        CoreBootstrap.install(modEventBus);
    }
}
