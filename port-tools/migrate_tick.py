#!/usr/bin/env python3
# codPattern 1.21.1 移植：TickEvent -> event.tick.{ServerTickEvent,PlayerTickEvent}.Post / client.event.ClientTickEvent.{Pre,Post}
# 说明：NeoForge 1.21 取消了 TickEvent 与 Phase，Pre/Post 拆成独立类，因此
#       `if (event.phase == Phase.END)` 这类相位判断必须连同外层花括号一起消掉，
#       不是简单改名。逐站点精确替换，任何一条未命中都会打印出来。
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / 'upstream/src/main/java'
miss = []
hits = 0


def sub(rel, pairs):
    global hits
    p = ROOT / rel
    s = p.read_text(encoding='utf-8')
    orig = s
    for a, b in pairs:
        if a not in s:
            miss.append((rel, a[:100]))
            continue
        s = s.replace(a, b)
        hits += 1
    if s != orig:
        p.write_text(s, encoding='utf-8')
        print('  ok  ' + rel)


# 1) 客户端 refit：END 相位 -> Post，去掉相位判断
sub('com/cdp/codpattern/client/refit/AttachmentRefitClientEvents.java', [
    ('import net.neoforged.neoforge.event.TickEvent;',
     'import net.neoforged.neoforge.client.event.ClientTickEvent;'),
    ('public static void onClientTick(TickEvent.ClientTickEvent event) {\n'
     '        if (event.phase == TickEvent.Phase.END) {\n'
     '            AttachmentRefitClientState.tryOpenIfReady();\n'
     '        }\n'
     '    }',
     'public static void onClientTick(ClientTickEvent.Post event) {\n'
     '        AttachmentRefitClientState.tryOpenIfReady();\n'
     '    }'),
])

# 2) 服务端 tick：!= END -> Post，去掉守卫
sub('com/cdp/codpattern/compat/fpsmatch/event/ModeRoomTickEventHandler.java', [
    ('import net.neoforged.neoforge.event.TickEvent;',
     'import net.neoforged.neoforge.event.tick.ServerTickEvent;'),
    ('public static void onServerTick(TickEvent.ServerTickEvent event) {\n'
     '        if (event.phase != TickEvent.Phase.END) {\n'
     '            return;\n'
     '        }\n'
     '        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();',
     'public static void onServerTick(ServerTickEvent.Post event) {\n'
     '        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();'),
])

# 3) 服务端 tick：复合守卫，只保留后半段
sub('com/cdp/codpattern/event/AttachmentEditSessionServerEvents.java', [
    ('import net.neoforged.neoforge.event.TickEvent;',
     'import net.neoforged.neoforge.event.tick.ServerTickEvent;'),
    ('public static void onServerTick(TickEvent.ServerTickEvent event) {\n'
     '        if (event.phase != TickEvent.Phase.END || ServerLifecycleHooks.getCurrentServer() == null) {',
     'public static void onServerTick(ServerTickEvent.Post event) {\n'
     '        if (ServerLifecycleHooks.getCurrentServer() == null) {'),
])

# 4) 玩家 tick：event.player -> event.getEntity()，去掉相位条件
sub('com/cdp/codpattern/event/RoomFoodLockEventHandler.java', [
    ('import net.neoforged.neoforge.event.TickEvent;',
     'import net.neoforged.neoforge.event.tick.PlayerTickEvent;'),
    ('public static void onPlayerTick(TickEvent.PlayerTickEvent event) {\n'
     '        if (event.phase != TickEvent.Phase.END\n'
     '                || event.player.level().isClientSide\n'
     '                || !(event.player instanceof ServerPlayer player)) {',
     'public static void onPlayerTick(PlayerTickEvent.Post event) {\n'
     '        if (event.getEntity().level().isClientSide\n'
     '                || !(event.getEntity() instanceof ServerPlayer player)) {'),
])

# 5) 服务端 tick：== END 包裹体，拆掉包裹（保留 event.getServer()）
sub('com/cdp/codpattern/event/RoomTerminationEvents.java', [
    ('import net.neoforged.neoforge.event.TickEvent;',
     'import net.neoforged.neoforge.event.tick.ServerTickEvent;'),
    ('public static void tick(TickEvent.ServerTickEvent event) {\n'
     '        if (event.phase == TickEvent.Phase.END) {\n'
     '            RoomTerminationService.get(event.getServer()).tick();\n'
     '            com.cdp.codpattern.app.match.management.MapDeletionCoordinator.get(event.getServer()).tick();\n'
     '        }\n'
     '    }',
     'public static void tick(ServerTickEvent.Post event) {\n'
     '        RoomTerminationService.get(event.getServer()).tick();\n'
     '        com.cdp.codpattern.app.match.management.MapDeletionCoordinator.get(event.getServer()).tick();\n'
     '    }'),
])

# 6) 玩家 tick：event.player -> event.getEntity()
sub('com/cdp/codpattern/event/ThrowableServerEvents.java', [
    ('import net.neoforged.neoforge.event.TickEvent;',
     'import net.neoforged.neoforge.event.tick.PlayerTickEvent;'),
    ('public static void onPlayerTick(TickEvent.PlayerTickEvent event) {\n'
     '        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player)) {',
     'public static void onPlayerTick(PlayerTickEvent.Post event) {\n'
     '        if (!(event.getEntity() instanceof ServerPlayer player)) {'),
])

# 7) 客户端 tick：START/END 双相位 -> 拆成 Pre / Post 两个订阅方法
sub('com/cdp/codpattern/event/client/ClientTickHandler.java', [
    ('import net.neoforged.neoforge.event.TickEvent;',
     'import net.neoforged.neoforge.client.event.ClientTickEvent;'),
    ('    @SubscribeEvent\n'
     '    public static void onClientTick(TickEvent.ClientTickEvent event) {\n'
     '        if (event.phase == TickEvent.Phase.START) {\n'
     '            ClientTdmState.enforceDeathCamViewLock();\n'
     '            return;\n'
     '        }\n'
     '        if (event.phase == TickEvent.Phase.END) {\n'
     '            ClientTdmState.clientTick();\n'
     '            TdmCombatMarkerTracker.INSTANCE.clientTick();\n'
     '        }\n'
     '    }',
     '    @SubscribeEvent\n'
     '    public static void onClientTickPre(ClientTickEvent.Pre event) {\n'
     '        ClientTdmState.enforceDeathCamViewLock();\n'
     '    }\n'
     '\n'
     '    @SubscribeEvent\n'
     '    public static void onClientTickPost(ClientTickEvent.Post event) {\n'
     '        ClientTdmState.clientTick();\n'
     '        TdmCombatMarkerTracker.INSTANCE.clientTick();\n'
     '    }'),
])

# 8) 客户端 tick：!= END -> Post
sub('com/cdp/codpattern/event/client/ThrowableClientInputHandler.java', [
    ('import net.neoforged.neoforge.event.TickEvent;',
     'import net.neoforged.neoforge.client.event.ClientTickEvent;'),
    ('public static void onClientTick(TickEvent.ClientTickEvent event) {\n'
     '        if (event.phase != TickEvent.Phase.END) {\n'
     '            return;\n'
     '        }\n',
     'public static void onClientTick(ClientTickEvent.Post event) {\n'),
])

# 9) 服务端 tick：!= END -> Post
sub('com/cdp/codpattern/fpsmatch/room/CodTdmRoomManager.java', [
    ('import net.neoforged.neoforge.event.TickEvent;',
     'import net.neoforged.neoforge.event.tick.ServerTickEvent;'),
    ('public static void onServerTick(TickEvent.ServerTickEvent event) {\n'
     '        if (event.phase != TickEvent.Phase.END) {\n'
     '            return;\n'
     '        }\n'
     '        getInstance().flushPendingRoomPush();',
     'public static void onServerTick(ServerTickEvent.Post event) {\n'
     '        getInstance().flushPendingRoomPush();'),
])

# 10) 内嵌 FPSM 核心：玩家 tick
sub('com/phasetranscrystal/fpsmatch/common/FPSMEvents.java', [
    ('import net.neoforged.neoforge.event.TickEvent;',
     'import net.neoforged.neoforge.event.tick.PlayerTickEvent;'),
    ('public static void onPlayerTickEvent(TickEvent.PlayerTickEvent event) {\n'
     '        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player)) {',
     'public static void onPlayerTickEvent(PlayerTickEvent.Post event) {\n'
     '        if (!(event.getEntity() instanceof ServerPlayer player)) {'),
])

# 11) 内嵌 FPSM 核心：服务端 tick
sub('com/phasetranscrystal/fpsmatch/core/FPSMCore.java', [
    ('import net.neoforged.neoforge.event.TickEvent;',
     'import net.neoforged.neoforge.event.tick.ServerTickEvent;'),
    ('public static void onServerTickEvent(TickEvent.ServerTickEvent event) {\n'
     '        if (event.phase == TickEvent.Phase.END && initialized()) {\n'
     '            getInstance().onServerTick();\n'
     '        }\n'
     '    }',
     'public static void onServerTickEvent(ServerTickEvent.Post event) {\n'
     '        if (initialized()) {\n'
     '            getInstance().onServerTick();\n'
     '        }\n'
     '    }'),
])

# 全库：EventBusSubscriber.Bus.FORGE -> Bus.GAME（NeoForge 只有 GAME/MOD）
n = 0
for p in ROOT.rglob('*.java'):
    s = p.read_text(encoding='utf-8')
    if 'EventBusSubscriber.Bus.FORGE' in s:
        p.write_text(s.replace('EventBusSubscriber.Bus.FORGE', 'EventBusSubscriber.Bus.GAME'), encoding='utf-8')
        n += 1
print('  ok  Bus.FORGE -> Bus.GAME：%d 个文件' % n)

# 残留检查
left = []
for p in ROOT.rglob('*.java'):
    s = p.read_text(encoding='utf-8')
    if 'TickEvent' in s and 'LivingTickEvent' not in s:
        left.append(p.relative_to(ROOT))
    elif 'TickEvent' in s:
        for i, l in enumerate(s.splitlines(), 1):
            if 'TickEvent' in l and 'LivingTickEvent' not in l:
                left.append('%s:%d' % (p.relative_to(ROOT), i))
if left:
    print('\n!!! 仍有非 LivingTickEvent 的 TickEvent 残留：')
    for x in left:
        print('   ' + str(x))

print('\n替换命中 %d 条' % hits)
if miss:
    print('!!! 未命中 %d 条：' % len(miss))
    for r, a in miss:
        print('   %s :: %s' % (r, a))
else:
    print('全部替换命中。')
