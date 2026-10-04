#!/usr/bin/env python3
"""批 G3: FriendlyByteBuf#writeComponent/readComponent/writeItem/readItem -> PayloadBuf 垫片。"""
import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / 'upstream' / 'src' / 'main' / 'java'
IMPORT = 'import com.cdp.codpattern.adapter.neoforge.network.PayloadBuf;\n'

N = 'com/cdp/codpattern/network/'
F = 'com/phasetranscrystal/fpsmatch/common/packet/'

EDITS = [
    (N + 'match/PopupNoticePacket.java', 1,
     'this.title = buf.readComponent();', 'this.title = PayloadBuf.readComponent(buf);'),
    (N + 'match/PopupNoticePacket.java', 1,
     'this.message = buf.readComponent();', 'this.message = PayloadBuf.readComponent(buf);'),
    (N + 'match/PopupNoticePacket.java', 1,
     'buf.writeComponent(title);', 'PayloadBuf.writeComponent(buf, title);'),
    (N + 'match/PopupNoticePacket.java', 1,
     'buf.writeComponent(message);', 'PayloadBuf.writeComponent(buf, message);'),

    (F + 'AddAreaDataS2CPacket.java', 1,
     'buf.writeComponent(name);', 'PayloadBuf.writeComponent(buf, name);'),
    (F + 'AddAreaDataS2CPacket.java', 1,
     'Component name = buf.readComponent();', 'Component name = PayloadBuf.readComponent(buf);'),
    (F + 'AddPointDataS2CPacket.java', 1,
     'buf.writeComponent(name);', 'PayloadBuf.writeComponent(buf, name);'),
    (F + 'AddPointDataS2CPacket.java', 1,
     'Component name = buf.readComponent();', 'Component name = PayloadBuf.readComponent(buf);'),

    (N + 'match/KillFeedPacket.java', 1,
     'this.weaponStack = buf.readItem();', 'this.weaponStack = PayloadBuf.readItem(buf);'),
    (N + 'match/KillFeedPacket.java', 1,
     'buf.writeItem(weaponStack);', 'PayloadBuf.writeItem(buf, weaponStack);'),

    (N + 'SyncAttachmentCandidatesPacket.java', 1,
     'buffer.writeItem(stack == null ? ItemStack.EMPTY : stack);',
     'PayloadBuf.writeItem(buffer, stack == null ? ItemStack.EMPTY : stack);'),
    (N + 'SyncAttachmentCandidatesPacket.java', 1,
     'attachmentCandidates.add(buffer.readItem());',
     'attachmentCandidates.add(PayloadBuf.readItem(buffer));'),

    (N + 'SyncThrowableInventoryPacket.java', 1,
     'this.stacks[i] = buf.readItem();', 'this.stacks[i] = PayloadBuf.readItem(buf);'),
    (N + 'SyncThrowableInventoryPacket.java', 1,
     'buf.writeItem(stack);', 'PayloadBuf.writeItem(buf, stack);'),
]


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
            bad.append(f'{rel}: 期望 {want} 处, 实际 {n} 处 -> {old!r}')
            continue
        cache[rel] = cache[rel].replace(old, new, want)
        print(f'OK  {rel}  x{want}  {old[:60]!r}')
    if bad:
        print('\n'.join(['', '!!! 失败:'] + bad), file=sys.stderr)
        return 1
    for rel, txt in cache.items():
        (ROOT / rel).write_text(insert_import(txt, IMPORT), encoding='utf-8')
    print(f'\n写入 {len(cache)} 个文件')
    return 0


if __name__ == '__main__':
    sys.exit(main())
