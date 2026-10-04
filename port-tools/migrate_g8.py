#!/usr/bin/env python3
"""codPattern 1.21.1 port - batch G8: AttributeModifier record accessors, Holder<Attribute>,
CommonListenerCookie, and the last two renderBackground call sites.

Run: python3 tools/migrate_g8.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / 'upstream' / 'src' / 'main' / 'java'
COOKIE = 'net.minecraft.server.network.CommonListenerCookie'
WRITTEN = []


def add_import(rel, fqcn):
    path = ROOT / rel
    src = path.read_text(encoding='utf-8')
    line = f'import {fqcn};'
    if line in src:
        return
    idx = src.index('\nimport ')
    path.write_text(src[:idx + 1] + line + '\n' + src[idx + 1:], encoding='utf-8')
    print(f'  + import {fqcn}')


def apply(rel, *edits):
    path = ROOT / rel
    src = path.read_text(encoding='utf-8')
    original = src
    for desc, old, new, want in edits:
        got = src.count(old)
        if got != want:
            print(f'FAIL {rel} :: {desc} (want {want}, got {got})')
            sys.exit(1)
        src = src.replace(old, new)
    if src != original:
        path.write_text(src, encoding='utf-8')
        WRITTEN.append(rel)
        print(f'OK   {rel}  ({len(edits)} edits)')
    else:
        print(f'---- {rel} (no change)')


# ------------------------------------------------- AttributeModifier is a record now
apply('com/cdp/codpattern/app/match/gametest/RoomTerminationGameTests.java',
      ('record accessors',
       '        record.attributes.put(own.getId().toString(), new PlayerRecoveryRecord.AttributeUndo("minecraft:generic.movement_speed", own.getName(), own.getAmount(), own.getOperation().toValue()));',
       '        record.attributes.put(own.id().toString(), new PlayerRecoveryRecord.AttributeUndo("minecraft:generic.movement_speed", own.id().toString(), own.amount(), own.operation().id()));',
       1),
      ('record accessors in assertion',
       'speed.getModifier(own.getId())==null && speed.getModifier(foreign.getId())!=null',
       'speed.getModifier(own.id())==null && speed.getModifier(foreign.id())!=null',
       1),
      ('ServerGamePacketListenerImpl needs a listener cookie',
       '        player.connection = new ServerGamePacketListenerImpl(helper.getLevel().getServer(), new Connection(PacketFlow.SERVERBOUND), player) {',
       '        player.connection = new ServerGamePacketListenerImpl(helper.getLevel().getServer(), new Connection(PacketFlow.SERVERBOUND), player, CommonListenerCookie.createInitial(player.getGameProfile(), false)) {',
       1))
add_import('com/cdp/codpattern/app/match/gametest/RoomTerminationGameTests.java', COOKIE)

apply('com/cdp/codpattern/app/match/gametest/MapDeletionGameTests.java',
      ('ServerGamePacketListenerImpl needs a listener cookie',
       '        player.connection = new ServerGamePacketListenerImpl(server, new Connection(PacketFlow.SERVERBOUND), player) {',
       '        player.connection = new ServerGamePacketListenerImpl(server, new Connection(PacketFlow.SERVERBOUND), player, CommonListenerCookie.createInitial(player.getGameProfile(), false)) {',
       1))
add_import('com/cdp/codpattern/app/match/gametest/MapDeletionGameTests.java', COOKIE)

apply('com/cdp/codpattern/app/match/gametest/MapToolGameTests.java',
      ('ServerGamePacketListenerImpl needs a listener cookie',
       '        player.connection = new ServerGamePacketListenerImpl(server, connection, player) {',
       '        player.connection = new ServerGamePacketListenerImpl(server, connection, player, CommonListenerCookie.createInitial(player.getGameProfile(), false)) {',
       1))
add_import('com/cdp/codpattern/app/match/gametest/MapToolGameTests.java', COOKIE)

# ------------------------------------------------- Operation#toValue() -> id()
apply('com/cdp/codpattern/app/match/runtime/termination/RoomTerminationService.java',
      ('Operation#toValue -> id',
       'modifier.operation().toValue()', 'modifier.operation().id()', 1))

# ------------------------------------------------- Holder<Attribute> + record accessors
apply('com/cdp/codpattern/app/match/runtime/termination/PlayerRecoveryExecutor.java',
      ('getHolder yields Holder<Attribute>',
       'BuiltInRegistries.ATTRIBUTE.getOptional(ResourceLocation.parse(attribute.getValue().attribute())).orElseThrow()',
       'BuiltInRegistries.ATTRIBUTE.getHolder(ResourceLocation.parse(attribute.getValue().attribute())).orElseThrow()',
       1),
      ('record accessors in conflict check',
       """                if (current != null && (!current.getName().equals(expected.name())
                        || Double.compare(current.getAmount(), expected.amount()) != 0
                        || current.getOperation().toValue() != expected.operation()))""",
       """                if (current != null && (!current.id().toString().equals(expected.name())
                        || Double.compare(current.amount(), expected.amount()) != 0
                        || current.operation().id() != expected.operation()))""",
       1))

# ------------------------------------------------- last two 1-arg renderBackground calls
apply('com/cdp/codpattern/client/gui/screen/ModeRoomScreen.java',
      ('4-arg renderBackground call',
       '        this.renderBackground(graphics);',
       '        this.renderBackground(graphics, mouseX, mouseY, partialTick);', 1))

apply('com/cdp/codpattern/client/gui/screen/WeaponScreen.java',
      ('4-arg renderBackground call',
       '        renderBackground(graphics);',
       '        renderBackground(graphics, mouseX, mouseY, partialTick);', 1))

# ------------------------------------------------- residual scan
print()
print('--- residual scan ---')
bad = 0
for rel, needles in {
    'com/cdp/codpattern/app/match/gametest/RoomTerminationGameTests.java': ['own.getId()', 'foreign.getId()', 'own.getName()', 'own.getAmount()', 'own.getOperation()'],
    'com/cdp/codpattern/app/match/runtime/termination/RoomTerminationService.java': ['toValue()'],
    'com/cdp/codpattern/app/match/runtime/termination/PlayerRecoveryExecutor.java': ['toValue()', 'current.getName()', 'current.getAmount()', 'current.getOperation()', 'ATTRIBUTE.getOptional('],
    'com/cdp/codpattern/client/gui/screen/ModeRoomScreen.java': ['this.renderBackground(graphics);'],
    'com/cdp/codpattern/client/gui/screen/WeaponScreen.java': ['renderBackground(graphics);'],
}.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for needle in needles:
        if needle in text:
            print(f'STALE {rel}: {needle}')
            bad += 1
import subprocess
g = subprocess.run(['grep', '-rn', '-E', r'\.getOperation\(\)|\.getAmount\(\)|toValue\(\)',
                    '--include=*.java', str(ROOT)], capture_output=True, text=True)
for line in g.stdout.splitlines():
    if '.getName()' not in line:
        print(f'GLOBAL {line.strip()}')
        bad += 1
g2 = subprocess.run(['grep', '-rn', '-E', r'renderBackground\((graphics|pGuiGraphics)\);',
                     '--include=*.java', str(ROOT)], capture_output=True, text=True)
for line in g2.stdout.splitlines():
    print(f'GLOBAL {line.strip()}')
    bad += 1
print(f'residual={bad}   changed files={len(set(WRITTEN))}')
