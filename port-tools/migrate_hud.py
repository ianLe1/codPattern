#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
codPattern 1.21.1 移植 —— HUD 批（Forge overlay API -> NeoForge 1.21.1 GUI layer API）

实测依据（neoforge-21.1.253-universal.jar）：
  RegisterGuiOverlaysEvent            -> 已移除；替代 net.neoforged.neoforge.client.event.RegisterGuiLayersEvent
                                         其 registerAboveAll(ResourceLocation, LayeredDraw.Layer) 仍在
  IGuiOverlay                         -> 已移除；替代 net.minecraft.client.gui.LayeredDraw.Layer
                                         唯一方法 render(GuiGraphics, DeltaTracker)
  ForgeGui                            -> 已移除（render 首参消失）
  RenderGuiOverlayEvent(.Pre)         -> 已移除；替代 net.neoforged.neoforge.client.event.RenderGuiLayerEvent(.Pre)
                                         event.getOverlay().id()  ->  event.getName()
  VanillaGuiOverlay.HOTBAR.id()       -> 已移除；替代 net.neoforged.neoforge.client.gui.VanillaGuiLayers.HOTBAR（直接是 ResourceLocation 常量）
  DeltaTracker.getGameTimeDeltaPartialTick(boolean) 提供 partialTick
  Window.getGuiScaledWidth()/getGuiScaledHeight() 提供 screenWidth/screenHeight
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / 'upstream' / 'src/main/java'
MISSES = []


def sub(rel, pairs):
    p = ROOT / rel
    s = p.read_text(encoding='utf-8')
    orig = s
    for old, new in pairs:
        if old not in s:
            MISSES.append('%s :: 未找到 -> %s' % (rel, old.replace('\n', '\\n')[:90]))
            continue
        s = s.replace(old, new, 1)
    if s != orig:
        p.write_text(s, encoding='utf-8')
        print('  ok  ' + rel)
    else:
        print('  --  ' + rel + '（无变化）')
    return s


def sub_all(root_rel, pairs):
    n = 0
    for p in sorted((ROOT / root_rel).rglob('*.java')) if root_rel else sorted(ROOT.rglob('*.java')):
        s = p.read_text(encoding='utf-8')
        o = s
        for old, new in pairs:
            s = s.replace(old, new)
        if s != o:
            p.write_text(s, encoding='utf-8')
            n += 1
    print('  ok  %s：%d 个文件' % (root_rel or '全库', n))


print('== A. RegisterGuiOverlaysEvent -> RegisterGuiLayersEvent（全库）==')
sub_all(None, [('net.neoforged.neoforge.client.event.RegisterGuiOverlaysEvent',
                'net.neoforged.neoforge.client.event.RegisterGuiLayersEvent'),
               ('RegisterGuiOverlaysEvent', 'RegisterGuiLayersEvent')])

print('== B. CoreClientBootstrap：叠层注册用 ResourceLocation 键 ==')
sub('com/cdp/codpattern/client/bootstrap/CoreClientBootstrap.java', [
    ('import com.cdp.codpattern.client.extension.ModeGuiOverlayContributor;',
     'import com.cdp.codpattern.CodPatternConstants;\n'
     'import com.cdp.codpattern.client.extension.ModeGuiOverlayContributor;'),
    ('import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;',
     'import net.minecraft.resources.ResourceLocation;\n'
     'import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;'),
    ('event.registerAboveAll("tdm_hud", TdmHudOverlay.INSTANCE);',
     'event.registerAboveAll(\n'
     '                        ResourceLocation.fromNamespaceAndPath(CodPatternConstants.MOD_ID, "tdm_hud"),\n'
     '                        TdmHudOverlay.INSTANCE);'),
])

print('== C. TdmHudOverlay：IGuiOverlay -> LayeredDraw.Layer，render 首参删除 ==')
sub('com/cdp/codpattern/client/gui/overlay/TdmHudOverlay.java', [
    ('import net.minecraftforge.client.gui.overlay.ForgeGui;\n'
     'import net.minecraftforge.client.gui.overlay.IGuiOverlay;',
     'import net.minecraft.client.DeltaTracker;\n'
     'import net.minecraft.client.gui.LayeredDraw;'),
    ('public class TdmHudOverlay implements IGuiOverlay {',
     'public class TdmHudOverlay implements LayeredDraw.Layer {'),
    ('    public void render(ForgeGui gui, GuiGraphics graphics, float partialTick, int screenWidth, int screenHeight) {\n'
     '        if (!shouldRenderHud()) {\n'
     '            return;\n'
     '        }\n'
     '\n'
     '        Font font = Minecraft.getInstance().font;\n',
     '    public void render(GuiGraphics graphics, DeltaTracker deltaTracker) {\n'
     '        if (!shouldRenderHud()) {\n'
     '            return;\n'
     '        }\n'
     '\n'
     '        float partialTick = deltaTracker.getGameTimeDeltaPartialTick(false);\n'
     '        int screenWidth = Minecraft.getInstance().getWindow().getGuiScaledWidth();\n'
     '        int screenHeight = Minecraft.getInstance().getWindow().getGuiScaledHeight();\n'
     '        Font font = Minecraft.getInstance().font;\n'),
])

print('== D. TdmVanillaHudSuppressor：RenderGuiOverlayEvent -> RenderGuiLayerEvent ==')
sub('com/cdp/codpattern/event/client/TdmVanillaHudSuppressor.java', [
    ('import net.neoforged.neoforge.client.event.RenderGuiOverlayEvent;\n'
     'import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;',
     'import net.minecraft.client.gui.LayeredDraw;\n'
     'import net.neoforged.neoforge.client.event.RenderGuiLayerEvent;\n'
     'import net.neoforged.neoforge.client.gui.VanillaGuiLayers;'),
    ('VanillaGuiOverlay.HOTBAR.id(),\n'
     '            VanillaGuiOverlay.PLAYER_HEALTH.id(),\n'
     '            VanillaGuiOverlay.EXPERIENCE_BAR.id(),\n'
     '            VanillaGuiOverlay.FOOD_LEVEL.id());',
     'VanillaGuiLayers.HOTBAR,\n'
     '            VanillaGuiLayers.PLAYER_HEALTH,\n'
     '            VanillaGuiLayers.EXPERIENCE_BAR,\n'
     '            VanillaGuiLayers.FOOD_LEVEL);'),
    ('public static void onRenderGuiOverlay(RenderGuiOverlayEvent.Pre event) {',
     'public static void onRenderGuiLayer(RenderGuiLayerEvent.Pre event) {'),
    ('SUPPRESSED_OVERLAY_IDS.contains(event.getOverlay().id())',
     'SUPPRESSED_OVERLAY_IDS.contains(event.getName())'),
])

print()
if MISSES:
    print('!!! 有未命中的站点：')
    for m in MISSES:
        print('   ' + m)
    sys.exit(1)
print('全部替换命中。')
