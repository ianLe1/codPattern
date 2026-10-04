#!/usr/bin/env python3
"""codPattern 1.21.1 移植 · 批 E：注解与零散 API。

覆盖编译-3 里除网络层以外的全部「找不到符号」：
 1. Mod.EventBusSubscriber -> 顶层 EventBusSubscriber（NeoForge 从 Mod 的嵌套类提为顶层）
 2. LivingHurtEvent / LivingAttackEvent -> LivingIncomingDamageEvent
 3. LivingEvent.LivingTickEvent -> EntityTickEvent.Pre
 4. RegistryObject -> DeferredHolder（泛型形参两个）
 5. ForgeRegistries.ITEMS -> Registries.ITEM
 6. ForgeEventFactory.firePlayerSavingEvent -> EventHooks.firePlayerSavingEvent
 7. DistExecutor.safeRunWhenOn -> FMLEnvironment.dist 判断
 8. FMLJavaModLoadingContext -> @Mod 构造器注入 IEventBus
 9. ClientboundCustomPayloadPacket：protocol.game -> protocol.common
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "upstream" / "src" / "main" / "java"


def patch(rel, pairs, must_hit=True):
    """对单个文件做字面量替换，返回命中次数。"""
    p = ROOT / rel
    if not p.exists():
        print(f"  !! 缺文件 {rel}")
        return 0
    t = p.read_text(encoding="utf-8")
    orig = t
    hits = 0
    for old, new in pairs:
        n = t.count(old)
        if n:
            hits += n
            t = t.replace(old, new)
        elif must_hit:
            print(f"  !! 未命中 {rel}: {old[:70]!r}")
    if t != orig:
        p.write_text(t, encoding="utf-8")
        print(f"  M {rel}  ({hits} 处)")
    return hits


def add_import_after_last(t, imp):
    if imp in t:
        return t
    lines = t.split("\n")
    idx = -1
    for i, l in enumerate(lines):
        if l.startswith("import "):
            idx = i
    if idx < 0:
        for i, l in enumerate(lines):
            if l.startswith("package "):
                idx = i
                break
    lines.insert(idx + 1, imp)
    return "\n".join(lines)


def step1_event_bus_subscriber():
    print("[1] Mod.EventBusSubscriber -> EventBusSubscriber")
    n = 0
    for p in sorted(ROOT.rglob("*.java")):
        t = p.read_text(encoding="utf-8")
        if "Mod.EventBusSubscriber" not in t:
            continue
        t = t.replace("Mod.EventBusSubscriber", "EventBusSubscriber")
        t = add_import_after_last(t, "import net.neoforged.fml.common.EventBusSubscriber;")
        p.write_text(t, encoding="utf-8")
        n += 1
    print(f"  已改 {n} 个文件")
    return n


def main():
    if not ROOT.is_dir():
        sys.exit(f"ROOT 不存在: {ROOT}")
    print(f"ROOT = {ROOT}\n")

    step1_event_bus_subscriber()

    print("\n[2] LivingHurtEvent -> LivingIncomingDamageEvent")
    patch("com/cdp/codpattern/compat/fpsmatch/event/CodTdmEventHandler.java", [
        ("import net.neoforged.neoforge.event.entity.living.LivingHurtEvent;",
         "import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;"),
        ("LivingHurtEvent", "LivingIncomingDamageEvent"),  # 剩余用法
    ])

    print("\n[3] LivingEvent.LivingTickEvent / LivingAttackEvent -> NeoForge 等价")
    patch("com/cdp/codpattern/event/RoomTerminationEvents.java", [
        ("net.neoforged.neoforge.event.entity.living.LivingEvent.LivingTickEvent",
         "net.neoforged.neoforge.event.tick.EntityTickEvent.Pre"),
        ("net.neoforged.neoforge.event.entity.living.LivingAttackEvent",
         "net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent"),
    ])
    patch("com/cdp/codpattern/app/match/gametest/RoomTerminationGameTests.java", [
        ("new net.neoforged.neoforge.event.entity.living.LivingEvent.LivingTickEvent(delayed)",
         "new net.neoforged.neoforge.event.tick.EntityTickEvent.Pre(delayed)"),
        ("""new net.neoforged.neoforge.event.entity.living.LivingAttackEvent(unrelated,
                    level.damageSources().mobAttack(delayed), 1)""",
         """new net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent(unrelated,
                    new net.neoforged.neoforge.common.damagesource.DamageContainer(
                            level.damageSources().mobAttack(delayed), 1))"""),
    ])

    print("\n[4] RegistryObject -> DeferredHolder / ForgeRegistries -> Registries")
    patch("com/phasetranscrystal/fpsmatch/common/item/FPSMItemRegister.java", [
        ("import net.neoforged.neoforge.registries.ForgeRegistries;",
         "import net.minecraft.core.registries.Registries;"),
        ("import net.neoforged.neoforge.registries.RegistryObject;",
         "import net.neoforged.neoforge.registries.DeferredHolder;"),
        ("DeferredRegister.create(ForgeRegistries.ITEMS, FPSMatch.MODID)",
         "DeferredRegister.create(Registries.ITEM, FPSMatch.MODID)"),
        ("RegistryObject<MapManagementTool>", "DeferredHolder<Item, MapManagementTool>"),
        ("RegistryObject<MapCreatorTool>", "DeferredHolder<Item, MapCreatorTool>"),
        ("RegistryObject<SpawnPointTool>", "DeferredHolder<Item, SpawnPointTool>"),
    ])
    patch("com/phasetranscrystal/fpsmatch/common/item/FPSMCreativeModeTabRegister.java", [
        ("import net.neoforged.neoforge.registries.RegistryObject;",
         "import net.neoforged.neoforge.registries.DeferredHolder;"),
        ("RegistryObject<CreativeModeTab> CODPATTERN_TOOLS_AND_ITEMS",
         "DeferredHolder<CreativeModeTab, CreativeModeTab> CODPATTERN_TOOLS_AND_ITEMS"),
    ])

    print("\n[5] ForgeEventFactory -> EventHooks")
    patch("com/cdp/codpattern/app/match/runtime/termination/PlayerRecoveryPersistence.java", [
        ("import net.neoforged.neoforge.event.ForgeEventFactory;",
         "import net.neoforged.neoforge.event.EventHooks;"),
        ("ForgeEventFactory.firePlayerSavingEvent", "EventHooks.firePlayerSavingEvent"),
    ])

    print("\n[6] DistExecutor -> FMLEnvironment.dist")
    patch("com/cdp/codpattern/bootstrap/CoreBootstrap.java", [
        ("import net.neoforged.fml.DistExecutor;",
         "import net.neoforged.fml.loading.FMLEnvironment;"),
        ("DistExecutor.safeRunWhenOn(Dist.CLIENT, () -> CoreClientBootstrap::install);",
         "if (FMLEnvironment.dist == Dist.CLIENT) {\n"
         "            CoreClientBootstrap.install();\n"
         "        }"),
    ])

    print("\n[7] FMLJavaModLoadingContext -> 构造器注入 IEventBus")
    patch("com/cdp/codpattern/CodPattern.java", [
        ("import net.neoforged.fml.javafmlmod.FMLJavaModLoadingContext;\n", ""),
        ("import net.neoforged.fml.common.Mod;",
         "import net.neoforged.bus.api.IEventBus;\nimport net.neoforged.fml.common.Mod;"),
        ("public CodPattern() {\n        var modEventBus = FMLJavaModLoadingContext.get().getModEventBus();\n",
         "public CodPattern(IEventBus modEventBus) {\n"),
    ])

    print("\n[8] ClientboundCustomPayloadPacket：protocol.game -> protocol.common")
    patch("com/cdp/codpattern/app/match/gametest/MapToolGameTests.java", [
        ("import net.minecraft.network.protocol.game.ClientboundCustomPayloadPacket;",
         "import net.minecraft.network.protocol.common.ClientboundCustomPayloadPacket;"),
    ])

    print("\n=== 残留自查 ===")
    bad = 0
    for pat, desc in [
        (r"Mod\.EventBusSubscriber", "Mod.EventBusSubscriber"),
        (r"\bLivingHurtEvent\b", "LivingHurtEvent"),
        (r"\bLivingAttackEvent\b", "LivingAttackEvent"),
        (r"LivingEvent\.LivingTickEvent", "LivingEvent.LivingTickEvent"),
        (r"\bRegistryObject\b", "RegistryObject"),
        (r"\bForgeRegistries\b", "ForgeRegistries"),
        (r"\bForgeEventFactory\b", "ForgeEventFactory"),
        (r"\bDistExecutor\b", "DistExecutor"),
        (r"\bFMLJavaModLoadingContext\b", "FMLJavaModLoadingContext"),
        (r"net\.minecraft\.network\.protocol\.game\.ClientboundCustomPayloadPacket",
         "ClientboundCustomPayloadPacket@game"),
    ]:
        hits = []
        for p in ROOT.rglob("*.java"):
            for i, l in enumerate(p.read_text(encoding="utf-8").split("\n"), 1):
                if re.search(pat, l):
                    hits.append(f"{p.relative_to(ROOT)}:{i}")
        if hits:
            bad += len(hits)
            print(f"  ✗ {desc}: {len(hits)} -> {hits[:5]}")
        else:
            print(f"  ✓ {desc}: 0")
    print(f"\n残留合计 = {bad}")


if __name__ == "__main__":
    main()
