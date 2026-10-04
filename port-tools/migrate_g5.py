#!/usr/bin/env python3
"""批 G5: 散点事件/属性/客户端 API（非渲染类）。"""
import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / 'upstream' / 'src' / 'main' / 'java'

EV = 'com/cdp/codpattern/event/client/'
CM = 'com/cdp/codpattern/compat/fpsmatch/event/'
APP = 'com/cdp/codpattern/app/'
FPS = 'com/phasetranscrystal/fpsmatch/common/client/screen/'

MODE_OLD = """    private static void applyResult(PlayerInteractEvent event, InteractionResult result) {
        if (result == null || result == InteractionResult.PASS) {
            return;
        }
        event.setCancellationResult(result);
        event.setCanceled(true);
    }"""

MODE_NEW = """    private static void applyResult(PlayerInteractEvent.RightClickBlock event, InteractionResult result) {
        apply(event, result, event::setCancellationResult);
    }

    private static void applyResult(PlayerInteractEvent.RightClickItem event, InteractionResult result) {
        apply(event, result, event::setCancellationResult);
    }

    private static void applyResult(PlayerInteractEvent.EntityInteract event, InteractionResult result) {
        apply(event, result, event::setCancellationResult);
    }

    private static void apply(net.neoforged.bus.api.ICancellableEvent event, InteractionResult result,
                              java.util.function.Consumer<InteractionResult> cancellationResult) {
        if (result == null || result == InteractionResult.PASS) {
            return;
        }
        cancellationResult.accept(result);
        event.setCanceled(true);
    }"""

EDITS = [
    # RenderNameTagEvent 不 implements ICancellableEvent（继承 EntityEvent）→ 只能 setCanRender
    (EV + 'TdmNameTagVisibilityHandler.java', 1,
     'event.setResult(Event.Result.DENY);',
     'event.setCanRender(net.neoforged.neoforge.common.util.TriState.FALSE);'),
    (EV + 'TdmNameTagVisibilityHandler.java', 1,
     'import net.neoforged.bus.api.Event;\n', ''),

    # MouseScrollingEvent
    (EV + 'ThrowableClientInputHandler.java', 1,
     'Math.signum(event.getScrollDelta())', 'Math.signum(event.getScrollDeltaY())'),

    # Explosion 无 getDamageSource
    (CM + 'CodTdmEventHandler.java', 1,
     'event.getExplosion().getDamageSource()',
     'net.minecraft.world.level.Explosion.getDefaultDamageSource(event.getLevel(), creeper)'),

    # 玩家交互范围
    (FPS + 'MapCreatorToolScreen.java', 1,
     'minecraft.player.getBlockReach()', 'minecraft.player.blockInteractionRange()'),

    # ping
    (APP + 'tdm/service/TeamPlayerSnapshotService.java', 1,
     'Math.max(0, serverPlayer.latency)', 'Math.max(0, serverPlayer.connection.latency())'),

    # applyResult 参数类型收窄
    (CM + 'ModeObjectInteractionEventHandler.java', 1, MODE_OLD, MODE_NEW),
]


def main():
    cache, bad = {}, []
    for rel, want, old, new in EDITS:
        p = ROOT / rel
        if rel not in cache:
            cache[rel] = p.read_text(encoding='utf-8')
        n = cache[rel].count(old)
        if n != want:
            bad.append(f'{rel}: 期望 {want} 处, 实际 {n} 处 -> {old[:70]!r}')
            continue
        cache[rel] = cache[rel].replace(old, new, want)
        print(f'OK  {rel}  x{want}  {old.strip()[:60]!r}')
    if bad:
        print('\n'.join(['', '!!! 失败:'] + bad), file=sys.stderr)
        return 1
    for rel, txt in cache.items():
        (ROOT / rel).write_text(txt, encoding='utf-8')
    print(f'\n写入 {len(cache)} 个文件')
    return 0


if __name__ == '__main__':
    sys.exit(main())
