package com.cdp.codpattern.client.input;

import com.cdp.codpattern.CodPatternConstants;
import com.cdp.codpattern.core.throwable.ThrowableInventoryService;
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.minecraft.network.chat.Component;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.neoforge.client.event.RegisterKeyMappingsEvent;
import net.neoforged.neoforge.client.settings.KeyConflictContext;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.common.EventBusSubscriber;

@EventBusSubscriber(modid = CodPatternConstants.MOD_ID, bus = EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class ThrowableKeyMappings {
    private static final String CATEGORY = "key.categories.codpattern";

    public static final KeyMapping THROWABLE_SLOT_ONE = new KeyMapping(
            "key.codpattern.throwable.slot_1",
            KeyConflictContext.IN_GAME,
            InputConstants.UNKNOWN,
            CATEGORY);
    public static final KeyMapping THROWABLE_SLOT_TWO = new KeyMapping(
            "key.codpattern.throwable.slot_2",
            KeyConflictContext.IN_GAME,
            InputConstants.UNKNOWN,
            CATEGORY);

    private ThrowableKeyMappings() {
    }

    @SubscribeEvent
    public static void onRegisterKeyMappings(RegisterKeyMappingsEvent event) {
        event.register(THROWABLE_SLOT_ONE);
        event.register(THROWABLE_SLOT_TWO);
    }

    public static KeyMapping get(int slotIndex) {
        return slotIndex == ThrowableInventoryService.SLOT_ONE ? THROWABLE_SLOT_ONE : THROWABLE_SLOT_TWO;
    }

    public static Component getBoundLabel(int slotIndex) {
        KeyMapping mapping = get(slotIndex);
        return mapping.isUnbound()
                ? Component.translatable("common.codpattern.unbound")
                : mapping.getTranslatedKeyMessage();
    }
}
