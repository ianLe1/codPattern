#!/usr/bin/env python3
"""codPattern 1.21.1 port - batch G9: mixin runtime fixes.

Three defects found by inspecting TaCZ 1.21.1 (tacz-neoforge-1.21.1-1.1.8-hotfix-r7.jar) bytecode:

1. TaCZ rewrote its packets from `handle(Supplier<NetworkEvent.Context>)` to
   `handle(ClientMessageRefitGun, IPayloadContext)`.  The single lambda inside is therefore
   no longer `lambda$handle$0`: javac numbers lambdas class-wide in source order, and the
   StreamCodec lambdas in the static initialiser now occupy $0 and $1, pushing the handler
   lambda to `lambda$handle$3` (refit) / `lambda$handle$2` (unload).
2. `NetworkHandler.sendToClientPlayer` now takes CustomPacketPayload instead of Object.
3. The @Inject callback's first parameter was `NetworkEvent.Context` (a 1.20.1-era shim type);
   the target lambda's first parameter is now IPayloadContext, so the callback descriptor no
   longer matches.  Use IPayloadContext directly.

Also fixes codpattern.mixins.json: compatibilityLevel JAVA_17 -> JAVA_21 (MC 1.21.1 runs on
Java 21) and drops the stale refmap declaration (ModDevGradle does not generate one).

Run: python3 tools/migrate_g9.py
"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / 'upstream'
JAVA = BASE / 'src' / 'main' / 'java'
RES = BASE / 'src' / 'main' / 'resources'
SHIM = 'import com.cdp.codpattern.adapter.neoforge.network.NetworkEvent;'
NEO = 'import net.neoforged.neoforge.network.handling.IPayloadContext;'


def patch_text(path, edits):
    src = path.read_text(encoding='utf-8')
    original = src
    for desc, old, new, want in edits:
        got = src.count(old)
        if got != want:
            print(f'FAIL {path.name} :: {desc} (want {want}, got {got})')
            sys.exit(1)
        src = src.replace(old, new)
    if src == original:
        print(f'---- {path.name} (no change)')
        return False
    path.write_text(src, encoding='utf-8')
    print(f'OK   {path.name}  ({len(edits)} edits)')
    return True


# ---------------------------------------------------------------- mixins.json
mixins = RES / 'codpattern.mixins.json'
data = json.loads(mixins.read_text(encoding='utf-8'))
changed = False
if data.get('compatibilityLevel') != 'JAVA_21':
    print(f"  mixins.json compatibilityLevel {data.get('compatibilityLevel')} -> JAVA_21")
    data['compatibilityLevel'] = 'JAVA_21'
    changed = True
if 'refmap' in data:
    print(f"  mixins.json drop refmap={data['refmap']!r} (ModDevGradle generates none)")
    del data['refmap']
    changed = True
if changed:
    # keep Mixin's own key order: required, minVersion, package, plugin, compatibilityLevel, mixins, client, server
    ordered = {k: data[k] for k in
               ('required', 'minVersion', 'package', 'plugin', 'compatibilityLevel', 'mixins', 'client', 'server')
               if k in data}
    for k in data:
        ordered.setdefault(k, data[k])
    mixins.write_text(json.dumps(ordered, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

# ---------------------------------------------------------------- the two packet mixins
for cls, packet, lambda_name in (
        ('ClientMessageRefitGunMixin', 'ClientMessageRefitGun', 'lambda$handle$3'),
        ('ClientMessageUnloadAttachmentMixin', 'ClientMessageUnloadAttachment', 'lambda$handle$2'),
):
    path = JAVA / 'com' / 'cdp' / 'codpattern' / 'mixin' / 'tacz' / f'{cls}.java'
    patch_text(path, [
        ('lambda index',
         'method = "lambda$handle$0"', f'method = "{lambda_name}"', 3),
        ('sendToClientPlayer descriptor',
         'target = "Lcom/tacz/guns/network/NetworkHandler;sendToClientPlayer(Ljava/lang/Object;'
         'Lnet/minecraft/world/entity/player/Player;)V"',
         'target = "Lcom/tacz/guns/network/NetworkHandler;sendToClientPlayer('
         'Lnet/minecraft/network/protocol/common/custom/CustomPacketPayload;'
         'Lnet/minecraft/world/entity/player/Player;)V"', 1),
        ('callback first parameter is IPayloadContext now',
         f"""    private static void codpattern$syncCandidatesBeforeRefresh(NetworkEvent.Context context,
            {packet} message,
            CallbackInfo ci) {{
        ServerPlayer player = context.getSender();
        if (player == null) {{
            return;
        }}""",
         f"""    private static void codpattern$syncCandidatesBeforeRefresh(IPayloadContext context,
            {packet} message,
            CallbackInfo ci) {{
        if (!(context.player() instanceof ServerPlayer player)) {{
            return;
        }}""", 1),
        ('import the real payload context',
         SHIM, NEO, 1),
    ])

# ---------------------------------------------------------------- residual scan
print()
print('--- residual scan ---')
bad = 0
needles = ['lambda$handle$0', 'Lcom/tacz/guns/network/NetworkHandler;sendToClientPlayer(Ljava/lang/Object;',
           'adapter.neoforge.network.NetworkEvent', '"JAVA_17"', '"refmap"']
for path in list((JAVA / 'com' / 'cdp' / 'codpattern' / 'mixin').rglob('*.java')) + [mixins]:
    text = path.read_text(encoding='utf-8')
    for needle in needles:
        if needle in text:
            print(f'STALE {path.relative_to(BASE)}: {needle}')
            bad += 1
print(f'residual={bad}')
