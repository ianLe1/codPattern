package com.phasetranscrystal.fpsmatch.common.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.phasetranscrystal.fpsmatch.FPSMatch;
import com.phasetranscrystal.fpsmatch.common.client.data.RenderableArea;
import com.phasetranscrystal.fpsmatch.common.client.data.RenderablePoint;
import net.minecraft.client.Camera;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.world.phys.Vec3;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.neoforge.client.event.ClientPlayerNetworkEvent;
import net.neoforged.neoforge.client.event.RenderLevelStageEvent;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.Mod;

import java.util.Collection;
import net.neoforged.fml.common.EventBusSubscriber;

@EventBusSubscriber(modid = FPSMatch.MODID, bus = EventBusSubscriber.Bus.GAME, value = Dist.CLIENT)
public final class FPSMClientEvents {
    private FPSMClientEvents() {
    }

    @SubscribeEvent
    public static void onLevelRender(RenderLevelStageEvent event) {
        if (event.getStage() != RenderLevelStageEvent.Stage.AFTER_SOLID_BLOCKS) {
            return;
        }

        Collection<RenderableArea> areas = FPSMClient.getGlobalData().getDebugData().getAreas();
        Collection<RenderablePoint> points = FPSMClient.getGlobalData().getDebugData().getPoints();
        if (areas.isEmpty() && points.isEmpty()) {
            return;
        }

        PoseStack poseStack = event.getPoseStack();
        MultiBufferSource.BufferSource bufferSource = Minecraft.getInstance().renderBuffers().bufferSource();

        poseStack.pushPose();
        try {
            Camera camera = event.getCamera();
            Vec3 cameraPos = camera.getPosition();
            poseStack.translate(-cameraPos.x, -cameraPos.y, -cameraPos.z);

            for (RenderableArea area : areas) {
                area.render(poseStack, bufferSource);
            }
            for (RenderablePoint point : points) {
                point.render(poseStack, bufferSource);
            }

            bufferSource.endBatch();
        } finally {
            poseStack.popPose();
        }
    }

    @SubscribeEvent
    public static void onClientLogout(ClientPlayerNetworkEvent.LoggingOut event) {
        FPSMClient.reset();
    }
}
