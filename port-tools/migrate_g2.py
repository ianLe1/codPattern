#!/usr/bin/env python3
"""批 G2: 其余 ItemStack tag 站点 + FPSMItemRegister.accept(.get()) + CoreBootstrap 漏 import。

统一走 `com.cdp.codpattern.adapter.neoforge.nbt.ItemNbt` 垫片（等价 getTag/hasTag/setTag/getOrCreateTag）。
"""
import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / 'upstream' / 'src' / 'main' / 'java'
IMPORT = 'import com.cdp.codpattern.adapter.neoforge.nbt.ItemNbt;\n'

EDITS = [
    # ---------------- TaczAddonRefitCompat ----------------
    ('com/cdp/codpattern/compat/taczaddon/TaczAddonRefitCompat.java', 1,
     '        CompoundTag tag = gunStack.getTag();\n'
     '        if (tag == null || !tag.contains(COMBINED_ITEMS_TAG, Tag.TAG_LIST)) {\n'
     '            return;\n'
     '        }\n'
     '        tag.remove(COMBINED_ITEMS_TAG);\n'
     '        if (tag.isEmpty()) {\n'
     '            gunStack.setTag(null);\n'
     '        }',
     '        CompoundTag tag = ItemNbt.get(gunStack);\n'
     '        if (tag == null || !tag.contains(COMBINED_ITEMS_TAG, Tag.TAG_LIST)) {\n'
     '            return;\n'
     '        }\n'
     '        tag.remove(COMBINED_ITEMS_TAG);\n'
     '        ItemNbt.set(gunStack, tag.isEmpty() ? null : tag);'),

    # ---------------- 工厂 / 预设服务 ----------------
    ('com/cdp/codpattern/config/backpack/BackpackItemStackFactory.java', 1,
     '                stack.setTag(TagParser.parseTag(nbt));',
     '                ItemNbt.set(stack, TagParser.parseTag(nbt));'),
    ('com/cdp/codpattern/app/refit/service/AttachmentPresetRequestService.java', 1,
     '                stack.setTag(TagParser.parseTag(nbt));',
     '                ItemNbt.set(stack, TagParser.parseTag(nbt));'),
    ('com/cdp/codpattern/app/backpack/service/UpdateWeaponService.java', 1,
     '            candidateStack.setTag(nbtTag.copy());',
     '            ItemNbt.set(candidateStack, nbtTag.copy());'),

    # ---------------- 读出整包 NBT 转字符串 ----------------
    ('com/cdp/codpattern/app/refit/service/AttachmentPresetSaveService.java', 1,
     'String nbtString = gunStack.hasTag() ? gunStack.getTag().toString() : "";',
     'String nbtString = ItemNbt.has(gunStack) ? ItemNbt.get(gunStack).toString() : "";'),
    ('com/cdp/codpattern/client/refit/AttachmentRefitClientState.java', 1,
     'String nbtString = gunStack.hasTag() ? gunStack.getTag().toString() : "";',
     'String nbtString = ItemNbt.has(gunStack) ? ItemNbt.get(gunStack).toString() : "";'),
    ('com/cdp/codpattern/client/gui/screen/WeaponScreen.java', 1,
     'String nbt = weapon.hasTag() ? weapon.getTag().toString() : "";',
     'String nbt = ItemNbt.has(weapon) ? ItemNbt.get(weapon).toString() : "";'),

    # ---------------- isSameItemSameTags -> isSameItemSameComponents ----------------
    ('com/cdp/codpattern/client/gui/refit/FlatColorButton.java', 1,
     'ItemStack.isSameItemSameTags(weapon, lastWeaponSnapshot)',
     'ItemStack.isSameItemSameComponents(weapon, lastWeaponSnapshot)'),

    # ---------------- FPSMItemRegister: accept 只吃 ItemLike ----------------
    ('com/phasetranscrystal/fpsmatch/common/item/FPSMItemRegister.java', 1,
     '            event.accept(MAP_MANAGEMENT_TOOL);\n'
     '            event.accept(MAP_CREATOR_TOOL);\n'
     '            event.accept(SPAWN_POINT_TOOL);',
     '            event.accept(MAP_MANAGEMENT_TOOL.get());\n'
     '            event.accept(MAP_CREATOR_TOOL.get());\n'
     '            event.accept(SPAWN_POINT_TOOL.get());'),

    # ---------------- CoreBootstrap: 批 C 漏掉的 import ----------------
    ('com/cdp/codpattern/bootstrap/CoreBootstrap.java', 1,
     'import com.cdp.codpattern.command.CommandRegistration;',
     'import com.cdp.codpattern.command.CommandRegistration;\n'
     'import com.cdp.codpattern.core.throwable.ThrowableInventoryCapability;'),
]

# MapToolGameTests: stack.getTag() 全量替换（7 处）
GAMETEST = 'com/cdp/codpattern/app/match/gametest/MapToolGameTests.java'


def insert_import(txt, line):
    if line in txt:
        return txt
    lines = txt.split('\n')
    for i, l in enumerate(lines):
        if l.startswith('import net.'):
            lines.insert(i, line.rstrip('\n'))
            return '\n'.join(lines)
    raise AssertionError('未找到 import net. 锚点')


def main():
    cache, bad = {}, []
    for rel, want, old, new in EDITS:
        p = ROOT / rel
        if rel not in cache:
            cache[rel] = p.read_text(encoding='utf-8')
        n = cache[rel].count(old)
        if n != want:
            bad.append(f'{rel}: 期望 {want} 处, 实际 {n} 处 -> {old[:80]!r}')
            continue
        cache[rel] = cache[rel].replace(old, new, want)
        print(f'OK  {rel}  x{want}  {old.strip()[:70]!r}')
    # MapToolGameTests
    if GAMETEST not in cache:
        cache[GAMETEST] = (ROOT / GAMETEST).read_text(encoding='utf-8')
    n = cache[GAMETEST].count('stack.getTag()')
    if n != 7:
        bad.append(f'{GAMETEST}: 期望 7 处 stack.getTag(), 实际 {n} 处')
    else:
        cache[GAMETEST] = cache[GAMETEST].replace('stack.getTag()', 'ItemNbt.get(stack)')
        print(f'OK  {GAMETEST}  x7  stack.getTag() -> ItemNbt.get(stack)')
    if bad:
        print('\n'.join(['', '!!! 失败:'] + bad), file=sys.stderr)
        return 1
    for rel, txt in cache.items():
        (ROOT / rel).write_text(insert_import(txt, IMPORT), encoding='utf-8')
    print(f'\n写入 {len(cache)} 个文件 (含 ItemNbt import 补插)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
