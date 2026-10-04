#!/usr/bin/env python3
"""codPattern 1.21.1 port - batch G6: client render / GUI screen API deltas.

Every edit asserts its expected hit count; a miss aborts before writing anything.
Run from anywhere: python3 tools/migrate_g6.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / 'upstream' / 'src' / 'main' / 'java'

WRITTEN = []


def apply(rel, *edits):
    """edits: (desc, old, new, want)"""
    path = ROOT / rel
    src = path.read_text(encoding='utf-8')
    original = src
    for desc, old, new, want in edits:
        got = src.count(old)
        if got != want:
            print(f'FAIL {rel} :: {desc} (want {want}, got {got})')
            sys.exit(1)
        src = src.replace(old, new)
    if src == original:
        print(f'---- {rel} (no change)')
        return
    path.write_text(src, encoding='utf-8')
    WRITTEN.append(rel)
    print(f'OK   {rel}  ({len(edits)} edits)')


def create(rel, text):
    path = ROOT / rel
    if path.exists():
        print(f'SKIP {rel} (already exists)')
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
    WRITTEN.append(rel)
    print(f'NEW  {rel}')


# ---------------------------------------------------------------- 1. SoundEvents
apply('com/cdp/codpattern/client/state/ClientMatchStateStore.java',
      ('note_block_hat holder',
       'SoundEvents.NOTE_BLOCK_HAT.get()', 'SoundEvents.NOTE_BLOCK_HAT.value()', 2),
      ('note_block_bell holder',
       'SoundEvents.NOTE_BLOCK_BELL.get()', 'SoundEvents.NOTE_BLOCK_BELL.value()', 2),
      ('generic_explode holder',
       'playNotifySound(SoundEvents.GENERIC_EXPLODE,', 'playNotifySound(SoundEvents.GENERIC_EXPLODE.value(),', 1))

apply('com/cdp/codpattern/compat/fpsmatch/map/CodTdmPhaseStateHooks.java',
      ('note_block_pling holder',
       'SoundEvents.NOTE_BLOCK_PLING.get()', 'SoundEvents.NOTE_BLOCK_PLING.value()', 1))

# ---------------------------------------------------------------- 2. skins / avatars
apply('com/cdp/codpattern/client/gui/overlay/TdmHudOverlay.java',
      ('skin type',
       '        ResourceLocation skin = Minecraft.getInstance().getSkinManager()',
       '        net.minecraft.client.resources.PlayerSkin skin = Minecraft.getInstance().getSkinManager()', 1),
      ('getInsecureSkin',
       '.getInsecureSkinLocation(new GameProfile(player.uuid(), player.name()));',
       '.getInsecureSkin(new GameProfile(player.uuid(), player.name()));', 1))

# 1.20.1: (g, x, y, scale, mouseX, mouseY, entity)
# 1.21.1: (g, x1, y1, x2, y2, size, yOffset, mouseX, mouseY, entity) -> bounding box
apply('com/cdp/codpattern/client/gui/overlay/TdmPlayerModelRenderer.java',
      ('follows-mouse bounding box',
       """        InventoryScreen.renderEntityInInventoryFollowsMouse(
                graphics,
                centerX,
                baselineY,
                modelScale,
                motionX,
                motionY,
                entity
        );""",
       """        InventoryScreen.renderEntityInInventoryFollowsMouse(
                graphics,
                centerX - modelScale,
                baselineY - modelScale,
                centerX + modelScale,
                baselineY + modelScale,
                modelScale,
                0.0625f,
                motionX,
                motionY,
                entity
        );""", 1))

# 1.21.x RenderNameTagEvent#getPartialTick() returns a DeltaTracker, not a float
apply('com/cdp/codpattern/event/client/TdmCombatMarkerWorldRenderer.java',
      ('partial tick is a DeltaTracker now',
       'interpolatePlayerHeadPos(tracked, event.getPartialTick())',
       'interpolatePlayerHeadPos(tracked, event.getPartialTick().getGameTimeDeltaPartialTick(false))', 1))

# ---------------------------------------------------------------- 3. Tesselator / BufferBuilder
apply('com/cdp/codpattern/client/render/CombatMarkerWorldRenderer.java',
      ('immediate-mode quad -> retained MeshData',
       """        BufferBuilder bufferBuilder = Tesselator.getInstance().getBuilder();
        RenderSystem.setShader(GameRenderer::getPositionColorShader);
        bufferBuilder.begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR);
        bufferBuilder.vertex(matrix, left, top, 0.0f).color(red, green, blue, alpha).endVertex();
        bufferBuilder.vertex(matrix, left, bottom, 0.0f).color(red, green, blue, alpha).endVertex();
        bufferBuilder.vertex(matrix, right, bottom, 0.0f).color(red, green, blue, alpha).endVertex();
        bufferBuilder.vertex(matrix, right, top, 0.0f).color(red, green, blue, alpha).endVertex();
        BufferUploader.drawWithShader(bufferBuilder.end());
    }""",
       """        RenderSystem.setShader(GameRenderer::getPositionColorShader);
        BufferBuilder bufferBuilder = Tesselator.getInstance()
                .begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR);
        emitVertex(bufferBuilder, matrix, left, top, red, green, blue, alpha);
        emitVertex(bufferBuilder, matrix, left, bottom, red, green, blue, alpha);
        emitVertex(bufferBuilder, matrix, right, bottom, red, green, blue, alpha);
        emitVertex(bufferBuilder, matrix, right, top, red, green, blue, alpha);
        BufferUploader.drawWithShader(bufferBuilder.buildOrThrow());
    }

    private static void emitVertex(BufferBuilder bufferBuilder, Matrix4f matrix,
                                   float x, float y, float red, float green, float blue, float alpha) {
        Vector3f position = matrix.transformPosition(x, y, 0.0f, new Vector3f());
        bufferBuilder.addVertex(position.x(), position.y(), position.z())
                .setColor(red, green, blue, alpha);
    }""", 1))

# ---------------------------------------------------------------- 4. EditBox#tick removed
apply('com/cdp/codpattern/client/gui/screen/RenameBackpackScreen.java',
      ('drop tick() override',
       """    @Override
    public void tick() {
        if (nameBox != null) {
            nameBox.tick();
        }
    }

""", '', 1),
      ('moveCursorToEnd(boolean)',
       'nameBox.moveCursorToEnd();', 'nameBox.moveCursorToEnd(true);', 1),
      ('background call needs 4 args',
       '        this.renderBackground(graphics);',
       '        this.renderBackground(graphics, mouseX, mouseY, partialTick);', 1))

apply('com/cdp/codpattern/client/gui/screen/EndTeleportScreen.java',
      ('drop field tick() calls',
       '        x.tick(); y.tick(); z.tick();\n', '', 1))

apply('com/cdp/codpattern/client/gui/screen/MapManagementScreen.java',
      ('drop nameField.tick()',
       '        if (nameField != null) nameField.tick();\n', '', 1))

apply('com/phasetranscrystal/fpsmatch/common/client/screen/MapCreatorToolScreen.java',
      ('drop EditBox.tick() calls',
       """        if (this.mapNameField != null) {
            this.mapNameField.tick();
        }
        for (EditBox field : getPosFields()) {
            field.tick();
        }
""", '', 1))

# ---------------------------------------------------------------- 5. Screen#renderBackground(GuiGraphics) gone
apply('com/cdp/codpattern/client/gui/screen/ModeRoomScreen.java',
      ('4-arg renderBackground',
       '    public void renderBackground(@NotNull GuiGraphics graphics) {',
       '    public void renderBackground(@NotNull GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {', 1))

apply('com/cdp/codpattern/client/gui/screen/WeaponScreen.java',
      ('4-arg renderBackground',
       '    public void renderBackground(@NotNull GuiGraphics graphics) {',
       '    public void renderBackground(@NotNull GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {', 1))

apply('com/cdp/codpattern/client/gui/screen/BackpackMenuScreen.java',
      ('4-arg renderBackground',
       '    public void renderBackground(@NotNull GuiGraphics pGuiGraphics) {',
       '    public void renderBackground(@NotNull GuiGraphics pGuiGraphics, int mouseX, int mouseY, float partialTick) {', 1),
      ('background call needs 4 args',
       '        this.renderBackground(pGuiGraphics);',
       '        this.renderBackground(pGuiGraphics, pMouseX, pMouseY, pPartialTick);', 1))

apply('com/cdp/codpattern/client/gui/screen/WeaponMenuScreen.java',
      ('4-arg renderBackground',
       '    public void renderBackground(@NotNull GuiGraphics pGuiGraphics) {',
       '    public void renderBackground(@NotNull GuiGraphics pGuiGraphics, int mouseX, int mouseY, float partialTick) {', 1),
      ('background call needs 4 args',
       '        this.renderBackground(pGuiGraphics);',
       '        this.renderBackground(pGuiGraphics, pMouseX, pMouseY, pPartialTick);', 1))

apply('com/cdp/codpattern/compat/tacz/client/CodGunRefitScreen.java',
      ('4-arg renderBackground',
       '    public void renderBackground(@NotNull GuiGraphics graphics) {',
       '    public void renderBackground(@NotNull GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {', 1))

# ---------------------------------------------------------------- 6. mouseScrolled 4 args
apply('com/cdp/codpattern/client/gui/screen/MapManagementScreen.java',
      ('4-arg mouseScrolled signature',
       'public boolean mouseScrolled(double mouseX, double mouseY, double delta) {',
       'public boolean mouseScrolled(double mouseX, double mouseY, double deltaX, double deltaY) {', 1),
      ('delta -> deltaY (scroll list)',
       'listScroll = Math.max(0, listScroll - (delta > 0 ? 1 : -1));',
       'listScroll = Math.max(0, listScroll - (deltaY > 0 ? 1 : -1));', 1),
      ('delta -> deltaY (scroll detail)',
       'detailScroll = Math.max(0, detailScroll - (delta > 0 ? 1 : -1));',
       'detailScroll = Math.max(0, detailScroll - (deltaY > 0 ? 1 : -1));', 1),
      ('super call forward',
       'return super.mouseScrolled(mouseX, mouseY, delta);',
       'return super.mouseScrolled(mouseX, mouseY, deltaX, deltaY);', 1))

apply('com/cdp/codpattern/client/gui/screen/ModeRoomScreen.java',
      ('4-arg mouseScrolled signature',
       'public boolean mouseScrolled(double mouseX, double mouseY, double delta) {',
       'public boolean mouseScrolled(double mouseX, double mouseY, double deltaX, double deltaY) {', 1),
      ('delta -> deltaY up',
       'if (delta > 0 && roomListScrollOffset > 0) {',
       'if (deltaY > 0 && roomListScrollOffset > 0) {', 1),
      ('delta -> deltaY down',
       'if (delta < 0 && roomListScrollOffset < roomListMaxScrollOffset) {',
       'if (deltaY < 0 && roomListScrollOffset < roomListMaxScrollOffset) {', 1),
      ('super call forward',
       'return super.mouseScrolled(mouseX, mouseY, delta);',
       'return super.mouseScrolled(mouseX, mouseY, deltaX, deltaY);', 1))

apply('com/cdp/codpattern/client/gui/screen/ModeSelectScreen.java',
      ('4-arg mouseScrolled signature',
       'public boolean mouseScrolled(double mouseX, double mouseY, double delta) {',
       'public boolean mouseScrolled(double mouseX, double mouseY, double deltaX, double deltaY) {', 1),
      ('delta -> deltaY left',
       'if (delta > 0.0d) {', 'if (deltaY > 0.0d) {', 1),
      ('delta -> deltaY right',
       '} else if (delta < 0.0d) {', '} else if (deltaY < 0.0d) {', 1),
      ('super call forward',
       'return super.mouseScrolled(mouseX, mouseY, delta);',
       'return super.mouseScrolled(mouseX, mouseY, deltaX, deltaY);', 2),
      ('dirt background helper removed',
       '        renderDirtBackground(graphics);', '        renderTransparentBackground(graphics);', 1))

apply('com/cdp/codpattern/client/gui/screen/WeaponScreen.java',
      ('4-arg mouseScrolled signature',
       'public boolean mouseScrolled(double mouseX, double mouseY, double delta) {',
       'public boolean mouseScrolled(double mouseX, double mouseY, double deltaX, double deltaY) {', 1),
      ('delta -> deltaY left',
       '        if (delta > 0) {', '        if (deltaY > 0) {', 1),
      ('delta -> deltaY right',
       '        } else if (delta < 0) {', '        } else if (deltaY < 0) {', 1))

# ---------------------------------------------------------------- 7. tooltip context
apply('com/phasetranscrystal/fpsmatch/common/item/MapManagementTool.java',
      ('appendHoverText context',
       'public void appendHoverText(ItemStack stack, Level level, List<Component> tooltip, TooltipFlag flag) {',
       'public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {',
       1))

# ---------------------------------------------------------------- residual scan
STALE = [
    'Tesselator.getInstance().getBuilder()',
    'bufferBuilder.begin(VertexFormat.Mode',
    'getInsecureSkinLocation',
    'getDirtBackground',
    'renderDirtBackground',
    'moveCursorToEnd()',
    'nameField.tick()',
    'mapNameField.tick()',
    'field.tick()',
    'x.tick(); y.tick(); z.tick();',
    'public boolean mouseScrolled(double mouseX, double mouseY, double delta)',
    'public void renderBackground(@NotNull GuiGraphics graphics) {',
    'public void renderBackground(@NotNull GuiGraphics pGuiGraphics) {',
    'appendHoverText(ItemStack stack, Level level',
]
print()
print('--- residual scan ---')
bad = 0
for rel in sorted(set(WRITTEN)):
    text = (ROOT / rel).read_text(encoding='utf-8')
    for needle in STALE:
        if needle in text:
            print(f'STALE {rel}: {needle}')
            bad += 1
print(f'residual={bad}   changed files={len(set(WRITTEN))}')
sys.exit(0)
