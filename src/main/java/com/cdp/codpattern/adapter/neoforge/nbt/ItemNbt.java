package com.cdp.codpattern.adapter.neoforge.nbt;

import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;

import java.util.function.Consumer;

/**
 * 1.20.1 的 {@code ItemStack#getTag/hasTag/setTag/getOrCreateTag} 在 1.21.1 被
 * {@link DataComponents#CUSTOM_DATA} 取代，这里保留原语义词，减少调用点改动面。
 */
public final class ItemNbt {
    private ItemNbt() {
    }

    /** 等价 {@code getTag()}：无自定义数据时返回 {@code null}。返回的是副本，改动不回写。 */
    public static CompoundTag get(ItemStack stack) {
        CustomData data = stack.get(DataComponents.CUSTOM_DATA);
        return data == null ? null : data.copyTag();
    }

    /** 等价 {@code hasTag()}。 */
    public static boolean has(ItemStack stack) {
        return stack.has(DataComponents.CUSTOM_DATA);
    }

    /** 等价 {@code setTag(tag)}：{@code null} 或空 tag 会清除组件（与上游 setTag(null) 同义）。 */
    public static void set(ItemStack stack, CompoundTag tag) {
        if (tag == null || tag.isEmpty()) {
            stack.remove(DataComponents.CUSTOM_DATA);
        } else {
            stack.set(DataComponents.CUSTOM_DATA, CustomData.of(tag));
        }
    }

    /** 等价 {@code getOrCreateTag()} 的就地修改语义：回调内可直接改 tag，结束时写回。 */
    public static void update(ItemStack stack, Consumer<CompoundTag> mutator) {
        CustomData.update(DataComponents.CUSTOM_DATA, stack, mutator);
    }
}
