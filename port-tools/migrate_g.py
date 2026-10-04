#!/usr/bin/env python3
"""批 G1: 1.21.1 ItemStack NBT-tag API -> DataComponents.CUSTOM_DATA (CustomData).

只做精确字面替换, 每处断言命中次数, 未命中即报错退出。
"""
import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / 'upstream' / 'src' / 'main' / 'java'

EDITS = [
    # ---------------- FPSMToolItem ----------------
    ('com/phasetranscrystal/fpsmatch/common/item/tool/FPSMToolItem.java', 1,
     'import net.minecraft.world.item.Item;',
     'import net.minecraft.core.component.DataComponents;\nimport net.minecraft.world.item.Item;'),
    ('com/phasetranscrystal/fpsmatch/common/item/tool/FPSMToolItem.java', 1,
     'import net.minecraft.world.item.ItemStack;',
     'import net.minecraft.world.item.ItemStack;\nimport net.minecraft.world.item.component.CustomData;'),
    ('com/phasetranscrystal/fpsmatch/common/item/tool/FPSMToolItem.java', 1,
     '        stack.getOrCreateTag().putString(key, value == null ? "" : value);',
     '        CustomData.update(DataComponents.CUSTOM_DATA, stack,\n'
     '                tag -> tag.putString(key, value == null ? "" : value));'),
    ('com/phasetranscrystal/fpsmatch/common/item/tool/FPSMToolItem.java', 1,
     '        CompoundTag tag = stack.getTag();\n'
     '        return tag == null ? "" : tag.getString(key);',
     '        CustomData data = stack.get(DataComponents.CUSTOM_DATA);\n'
     '        return data == null ? "" : data.copyTag().getString(key);'),
    ('com/phasetranscrystal/fpsmatch/common/item/tool/FPSMToolItem.java', 1,
     '        stack.getOrCreateTag().remove(key);',
     '        CustomData.update(DataComponents.CUSTOM_DATA, stack, tag -> tag.remove(key));'),

    # ---------------- MapCreatorTool ----------------
    ('com/phasetranscrystal/fpsmatch/common/item/MapCreatorTool.java', 1,
     'import net.minecraft.core.BlockPos;',
     'import net.minecraft.core.BlockPos;\nimport net.minecraft.core.component.DataComponents;'),
    ('com/phasetranscrystal/fpsmatch/common/item/MapCreatorTool.java', 1,
     'import net.minecraft.world.item.ItemStack;',
     'import net.minecraft.world.item.Item;\nimport net.minecraft.world.item.ItemStack;\n'
     'import net.minecraft.world.item.component.CustomData;'),
    ('com/phasetranscrystal/fpsmatch/common/item/MapCreatorTool.java', 1,
     '        CompoundTag compoundTag = stack.getOrCreateTag();\n'
     '        if (pos == null) {\n'
     '            compoundTag.remove(tag);\n'
     '            return;\n'
     '        }\n'
     '        compoundTag.putLong(tag, pos.asLong());',
     '        CustomData.update(DataComponents.CUSTOM_DATA, stack, compoundTag -> {\n'
     '            if (pos == null) {\n'
     '                compoundTag.remove(tag);\n'
     '                return;\n'
     '            }\n'
     '            compoundTag.putLong(tag, pos.asLong());\n'
     '        });'),
    ('com/phasetranscrystal/fpsmatch/common/item/MapCreatorTool.java', 1,
     '        CompoundTag compoundTag = stack.getTag();\n'
     '        if (compoundTag == null || !compoundTag.contains(tag, Tag.TAG_LONG)) {',
     '        CustomData data = stack.get(DataComponents.CUSTOM_DATA);\n'
     '        if (data == null) {\n'
     '            return null;\n'
     '        }\n'
     '        CompoundTag compoundTag = data.copyTag();\n'
     '        if (!compoundTag.contains(tag, Tag.TAG_LONG)) {'),
    ('com/phasetranscrystal/fpsmatch/common/item/MapCreatorTool.java', 1,
     '    public void appendHoverText(ItemStack stack, Level level, List<Component> tooltip, TooltipFlag isAdvanced) {',
     '    public void appendHoverText(ItemStack stack, Item.TooltipContext level, List<Component> tooltip,\n'
     '            TooltipFlag isAdvanced) {'),

    # ---------------- SpawnPointTool ----------------
    ('com/phasetranscrystal/fpsmatch/common/item/SpawnPointTool.java', 1,
     'import net.minecraft.core.BlockPos;',
     'import net.minecraft.core.BlockPos;\nimport net.minecraft.core.component.DataComponents;'),
    ('com/phasetranscrystal/fpsmatch/common/item/SpawnPointTool.java', 1,
     'import net.minecraft.world.item.ItemStack;',
     'import net.minecraft.world.item.Item;\nimport net.minecraft.world.item.ItemStack;\n'
     'import net.minecraft.world.item.component.CustomData;'),
    ('com/phasetranscrystal/fpsmatch/common/item/SpawnPointTool.java', 1,
     '        CompoundTag compoundTag = stack.getOrCreateTag();\n'
     '        if (pos == null) {\n'
     '            compoundTag.remove(tag);\n'
     '            return;\n'
     '        }\n'
     '        compoundTag.putLong(tag, pos.asLong());',
     '        CustomData.update(DataComponents.CUSTOM_DATA, stack, compoundTag -> {\n'
     '            if (pos == null) {\n'
     '                compoundTag.remove(tag);\n'
     '                return;\n'
     '            }\n'
     '            compoundTag.putLong(tag, pos.asLong());\n'
     '        });'),
    ('com/phasetranscrystal/fpsmatch/common/item/SpawnPointTool.java', 1,
     '        CompoundTag compoundTag = stack.getTag();\n'
     '        if (compoundTag == null || !compoundTag.contains(tag, Tag.TAG_LONG)) {',
     '        CustomData data = stack.get(DataComponents.CUSTOM_DATA);\n'
     '        if (data == null) {\n'
     '            return null;\n'
     '        }\n'
     '        CompoundTag compoundTag = data.copyTag();\n'
     '        if (!compoundTag.contains(tag, Tag.TAG_LONG)) {'),
    ('com/phasetranscrystal/fpsmatch/common/item/SpawnPointTool.java', 1,
     '    public void appendHoverText(ItemStack stack, Level level, List<Component> tooltip, TooltipFlag isAdvanced) {',
     '    public void appendHoverText(ItemStack stack, Item.TooltipContext level, List<Component> tooltip,\n'
     '            TooltipFlag isAdvanced) {'),
]


def main():
    cache, bad = {}, []
    for rel, want, old, new in EDITS:
        p = ROOT / rel
        if rel not in cache:
            cache[rel] = p.read_text(encoding='utf-8')
        txt = cache[rel]
        n = txt.count(old)
        if n != want:
            bad.append(f'{rel}: 期望 {want} 处, 实际 {n} 处 -> {old[:70]!r}')
            continue
        cache[rel] = txt.replace(old, new, want)
        print(f'OK  {rel}  x{want}  {old[:60]!r}')
    if bad:
        print('\n'.join(['', '!!! 失败:'] + bad), file=sys.stderr)
        return 1
    for rel, txt in cache.items():
        (ROOT / rel).write_text(txt, encoding='utf-8')
    print(f'\n写入 {len(cache)} 个文件')
    return 0


if __name__ == '__main__':
    sys.exit(main())
