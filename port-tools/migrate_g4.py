#!/usr/bin/env python3
"""批 G4: ResourceLocation 构造器 / AttributeModifier record / NbtIo / DataResult / ServerPlayer 构造器。"""
import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / 'upstream' / 'src' / 'main' / 'java'

APP = 'com/cdp/codpattern/app/'
CI = 'net.minecraft.server.level.ClientInformation.createDefault()'

EDITS = [
    # ---- ResourceLocation(ns, path) -> fromNamespaceAndPath ----
    (APP + 'match/model/ClientModePresentation.java', 1,
     'new ResourceLocation("codpattern", previewTexturePath)',
     'ResourceLocation.fromNamespaceAndPath("codpattern", previewTexturePath)'),
    ('com/cdp/codpattern/app/tdm/TdmModeModule.java', 1,
     'new ResourceLocation("codpattern", "team_modes")',
     'ResourceLocation.fromNamespaceAndPath("codpattern", "team_modes")'),
    ('com/cdp/codpattern/app/tdm/model/TdmClientModePresentations.java', 1,
     'new ResourceLocation("codpattern", "textures/gui/modes/frontline_preview.png")',
     'ResourceLocation.fromNamespaceAndPath("codpattern", "textures/gui/modes/frontline_preview.png")'),
    ('com/cdp/codpattern/app/tdm/model/TdmClientModePresentations.java', 1,
     'new ResourceLocation("codpattern", "textures/gui/modes/team_death_match_preview.png")',
     'ResourceLocation.fromNamespaceAndPath("codpattern", "textures/gui/modes/team_death_match_preview.png")'),
    ('com/cdp/codpattern/client/gui/screen/match/ModePreviewPanel.java', 1,
     'new ResourceLocation("codpattern", "textures/gui/modes/shared_preview.png")',
     'ResourceLocation.fromNamespaceAndPath("codpattern", "textures/gui/modes/shared_preview.png")'),
    # ---- ResourceLocation(String) -> parse ----
    (APP + 'match/runtime/termination/PlayerRecoveryExecutor.java', 1,
     'new ResourceLocation(attribute.getValue().attribute())',
     'ResourceLocation.parse(attribute.getValue().attribute())'),
    (APP + 'match/runtime/termination/PlayerRecoveryExecutor.java', 1,
     'new ResourceLocation(id)', 'ResourceLocation.parse(id)'),

    # ---- AttributeModifier 变 record ----
    (APP + 'match/gametest/RoomTerminationGameTests.java', 1,
     'new AttributeModifier(UUID.randomUUID(), "fixture-owned", .2, AttributeModifier.Operation.ADDITION)',
     'new AttributeModifier(ResourceLocation.parse("codpattern:fixture_owned"), .2,\n'
     '                AttributeModifier.Operation.ADD_VALUE)'),
    (APP + 'match/gametest/RoomTerminationGameTests.java', 1,
     'new AttributeModifier(UUID.randomUUID(), "other-mod", .1, AttributeModifier.Operation.ADDITION)',
     'new AttributeModifier(ResourceLocation.parse("codpattern:other_mod"), .1,\n'
     '                AttributeModifier.Operation.ADD_VALUE)'),
    (APP + 'match/runtime/termination/RoomTerminationService.java', 1,
     'modifier.getName(), modifier.getAmount(), modifier.getOperation().toValue()',
     'modifier.id().toString(), modifier.amount(), modifier.operation().toValue()'),
    (APP + 'match/runtime/termination/RoomTerminationService.java', 1,
     'record.attributes.put(modifier.getId().toString(), undo)',
     'record.attributes.put(modifier.id().toString(), undo)'),

    # ---- NbtIo Path 化 ----
    (APP + 'match/runtime/termination/PlayerRecoveryPersistence.java', 1,
     'NbtIo.writeCompressed(snapshot, temporary.toFile());',
     'NbtIo.writeCompressed(snapshot, temporary);'),
    (APP + 'match/runtime/termination/PlayerRecoveryPersistence.java', 1,
     'NbtIo.readCompressed(target.toFile())',
     'NbtIo.readCompressed(target, NbtAccounter.unlimitedHeap())'),
    (APP + 'match/runtime/termination/PlayerRecoveryPersistence.java', 1,
     'import net.minecraft.nbt.NbtIo;',
     'import net.minecraft.nbt.NbtAccounter;\nimport net.minecraft.nbt.NbtIo;'),

    # ---- DataResult.getOrThrow ----
    ('com/phasetranscrystal/fpsmatch/core/data/save/ISavePort.java', 2,
     '.getOrThrow(false, error -> {\n                    throw new RuntimeException(error);\n                })',
     '.getOrThrow(error -> new RuntimeException(error))'),

    # ---- ServerPlayer 构造器补 ClientInformation ----
    (APP + 'match/gametest/MapDeletionGameTests.java', 1,
     'new ServerPlayer(server, helper.getLevel(), new GameProfile(UUID.randomUUID(), "del-" + UUID.randomUUID().toString().substring(0, 8)))',
     'new ServerPlayer(server, helper.getLevel(),\n'
     '                new GameProfile(UUID.randomUUID(), "del-" + UUID.randomUUID().toString().substring(0, 8)), ' + CI + ')'),
    (APP + 'match/gametest/MapManagementGameTests.java', 1,
     'new com.mojang.authlib.GameProfile(UUID.randomUUID(), "map-reader"))',
     'new com.mojang.authlib.GameProfile(UUID.randomUUID(), "map-reader"), ' + CI + ')'),
    (APP + 'match/gametest/MapManagementGameTests.java', 1,
     'new com.mojang.authlib.GameProfile(UUID.randomUUID(), "map-admin"))',
     'new com.mojang.authlib.GameProfile(UUID.randomUUID(), "map-admin"), ' + CI + ')'),
    (APP + 'match/gametest/MapToolGameTests.java', 1,
     'new ServerPlayer(server, helper.getLevel(), new GameProfile(UUID.randomUUID(), "map-tool-test"))',
     'new ServerPlayer(server, helper.getLevel(),\n'
     '                new GameProfile(UUID.randomUUID(), "map-tool-test"), ' + CI + ')'),
    (APP + 'match/gametest/RoomTerminationGameTests.java', 1,
     'new ServerPlayer(helper.getLevel().getServer(), helper.getLevel(), new GameProfile(UUID.randomUUID(), "recovery-test"))',
     'new ServerPlayer(helper.getLevel().getServer(), helper.getLevel(),\n'
     '                new GameProfile(UUID.randomUUID(), "recovery-test"), ' + CI + ')'),
]

# RoomTerminationGameTests 需要 ResourceLocation import
NEED_RL = {APP + 'match/gametest/RoomTerminationGameTests.java'}
RL_IMPORT = 'import net.minecraft.resources.ResourceLocation;\n'


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
    if bad:
        print('\n'.join(['', '!!! 失败:'] + bad), file=sys.stderr)
        return 1
    for rel, txt in cache.items():
        if rel in NEED_RL:
            txt = insert_import(txt, RL_IMPORT)
        (ROOT / rel).write_text(txt, encoding='utf-8')
    print(f'\n写入 {len(cache)} 个文件')
    return 0


if __name__ == '__main__':
    sys.exit(main())
