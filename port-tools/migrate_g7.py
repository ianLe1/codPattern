#!/usr/bin/env python3
"""codPattern 1.21.1 port - batch G7: TaCZ IGun provider-first signatures + preset (de)serialization.

Every edit asserts its expected hit count; a miss aborts before writing anything.
Run: python3 tools/migrate_g7.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / 'upstream' / 'src' / 'main' / 'java'
SHIM = 'com.cdp.codpattern.adapter.neoforge.registry.RegistryAccessHolder'
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


# ------------------------------------------------------------------ TaczCoreGateway
apply('com/cdp/codpattern/compat/tacz/TaczCoreGateway.java',
      ('getAttachment takes a provider',
       '            ItemStack attachment = iGun.getAttachment(gunStack, type);',
       '            ItemStack attachment = iGun.getAttachment(RegistryAccessHolder.get(), gunStack, type);', 1),
      ('save needs a provider',
       """            ItemStack attachment = iGun.getAttachment(RegistryAccessHolder.get(), gunStack, type);
            CompoundTag attachmentTag = new CompoundTag();
            if (attachment.isEmpty()) {
                ItemStack.EMPTY.save(attachmentTag);
            } else {
                attachment.save(attachmentTag);
            }
            preset.put(key, attachmentTag);""",
       """            ItemStack attachment = iGun.getAttachment(RegistryAccessHolder.get(), gunStack, type);
            preset.put(key, attachment.isEmpty()
                    ? ItemStack.EMPTY.save(RegistryAccessHolder.get())
                    : attachment.save(RegistryAccessHolder.get()));""", 1),
      ('ItemStack.of -> parseOptional',
       '            ItemStack attachment = ItemStack.of(preset.getCompound(key));',
       '            ItemStack attachment = ItemStack.parseOptional(RegistryAccessHolder.get(), preset.getCompound(key));', 1),
      ('unloadAttachment takes a provider',
       '                iGun.unloadAttachment(gunStack, type);',
       '                iGun.unloadAttachment(RegistryAccessHolder.get(), gunStack, type);', 1),
      ('installAttachment takes a provider',
       '                iGun.installAttachment(gunStack, attachment);',
       '                iGun.installAttachment(RegistryAccessHolder.get(), gunStack, attachment);', 1))
add_import('com/cdp/codpattern/compat/tacz/TaczCoreGateway.java', SHIM)

# ------------------------------------------------------------------ BackpackAttachmentFilter
apply('com/cdp/codpattern/app/backpack/service/BackpackAttachmentFilter.java',
      ('getAttachment takes a provider',
       '            ItemStack attachmentStack = iGun.getAttachment(gunStack, type);',
       '            ItemStack attachmentStack = iGun.getAttachment(RegistryAccessHolder.get(), gunStack, type);', 1),
      ('unloadAttachment takes a provider',
       '            iGun.unloadAttachment(gunStack, type);',
       '            iGun.unloadAttachment(RegistryAccessHolder.get(), gunStack, type);', 1))
add_import('com/cdp/codpattern/app/backpack/service/BackpackAttachmentFilter.java', SHIM)

# ------------------------------------------------------------------ residual scan
print()
print('--- residual scan ---')
bad = 0
for rel, needles in {
    'com/cdp/codpattern/compat/tacz/TaczCoreGateway.java': [
        'iGun.getAttachment(gunStack', 'iGun.unloadAttachment(gunStack',
        'iGun.installAttachment(gunStack, attachment)', 'ItemStack.of(', 'ItemStack.EMPTY.save(attachmentTag)'],
    'com/cdp/codpattern/app/backpack/service/BackpackAttachmentFilter.java': [
        'iGun.getAttachment(gunStack', 'iGun.unloadAttachment(gunStack'],
}.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for needle in needles:
        if needle in text:
            print(f'STALE {rel}: {needle}')
            bad += 1
for rel in set(WRITTEN):
    if SHIM not in (ROOT / rel).read_text(encoding='utf-8'):
        print(f'MISSING IMPORT {rel}')
        bad += 1
print(f'residual={bad}   changed files={len(set(WRITTEN))}')
