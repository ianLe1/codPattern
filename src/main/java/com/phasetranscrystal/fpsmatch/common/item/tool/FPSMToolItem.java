package com.phasetranscrystal.fpsmatch.common.item.tool;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.core.component.DataComponents;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;

public abstract class FPSMToolItem extends Item {
    public static final String TYPE_TAG = "SelectedType";
    public static final String MAP_TAG = "SelectedMap";
    public static final String TEAM_TAG = "SelectedTeam";

    protected FPSMToolItem(Properties properties) {
        super(properties);
    }

    protected static void setStringTag(ItemStack stack, String key, String value) {
        CustomData.update(DataComponents.CUSTOM_DATA, stack,
                tag -> tag.putString(key, value == null ? "" : value));
    }

    protected static String getStringTag(ItemStack stack, String key) {
        CustomData data = stack.get(DataComponents.CUSTOM_DATA);
        return data == null ? "" : data.copyTag().getString(key);
    }

    protected static void removeTag(ItemStack stack, String key) {
        CustomData.update(DataComponents.CUSTOM_DATA, stack, tag -> tag.remove(key));
    }
}
