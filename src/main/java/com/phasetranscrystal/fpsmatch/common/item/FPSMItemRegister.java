package com.phasetranscrystal.fpsmatch.common.item;

import com.phasetranscrystal.fpsmatch.FPSMatch;
import com.cdp.codpattern.adapter.neoforge.nbt.ItemNbt;
import net.minecraft.world.item.Item;
import net.neoforged.neoforge.event.BuildCreativeModeTabContentsEvent;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.minecraft.core.registries.Registries;
import net.neoforged.neoforge.registries.DeferredHolder;

public final class FPSMItemRegister {
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(Registries.ITEM, FPSMatch.MODID);

    public static final DeferredHolder<Item, MapManagementTool> MAP_MANAGEMENT_TOOL = ITEMS.register(
            "map_management_tool",
            () -> new MapManagementTool(new Item.Properties().stacksTo(1))
    );

    public static final DeferredHolder<Item, MapCreatorTool> MAP_CREATOR_TOOL = ITEMS.register(
            "map_creator_tool",
            () -> new MapCreatorTool(new Item.Properties().stacksTo(1))
    );

    public static final DeferredHolder<Item, SpawnPointTool> SPAWN_POINT_TOOL = ITEMS.register(
            "spawn_point_tool",
            () -> new SpawnPointTool(new Item.Properties().stacksTo(1))
    );

    private FPSMItemRegister() {
    }

    public static void onBuildCreativeModeTabContents(BuildCreativeModeTabContentsEvent event) {
        if (FPSMCreativeModeTabRegister.CODPATTERN_TOOLS_AND_ITEMS_KEY.equals(event.getTabKey())) {
            event.accept(MAP_MANAGEMENT_TOOL.get());
            event.accept(MAP_CREATOR_TOOL.get());
            event.accept(SPAWN_POINT_TOOL.get());
        }
    }
}
