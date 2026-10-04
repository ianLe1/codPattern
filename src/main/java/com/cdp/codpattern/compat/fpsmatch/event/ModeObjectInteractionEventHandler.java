package com.cdp.codpattern.compat.fpsmatch.event;

import com.cdp.codpattern.CodPatternConstants;
import com.cdp.codpattern.app.match.model.ModeObjectInteractionContext;
import com.cdp.codpattern.app.match.runtime.object.ModeObjectInteractionBypassContributors;
import com.cdp.codpattern.compat.fpsmatch.FpsMatchGateway;
import com.cdp.codpattern.compat.fpsmatch.FpsMatchGatewayProvider;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.common.EventBusSubscriber;

@EventBusSubscriber(modid = CodPatternConstants.MOD_ID, bus = EventBusSubscriber.Bus.GAME)
public final class ModeObjectInteractionEventHandler {
    private ModeObjectInteractionEventHandler() {
    }

    @SubscribeEvent
    public static void onRightClickBlock(PlayerInteractEvent.RightClickBlock event) {
        if (isBlockHandledByOwnUse(event)) {
            return;
        }
        if (!(event.getEntity() instanceof ServerPlayer player) || player.level().isClientSide) {
            return;
        }
        FpsMatchGateway gateway = FpsMatchGatewayProvider.gateway();
        gateway.findPlayerInteractableObjectPort(player).ifPresent(port -> applyResult(event, port.interact(
                player,
                new ModeObjectInteractionContext(
                        port.roomId(),
                        event.getHand(),
                        event.getPos(),
                        event.getFace(),
                        null,
                        heldItem(player, event)))));
    }

    @SubscribeEvent
    public static void onRightClickItem(PlayerInteractEvent.RightClickItem event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || player.level().isClientSide) {
            return;
        }
        FpsMatchGateway gateway = FpsMatchGatewayProvider.gateway();
        gateway.findPlayerInteractableObjectPort(player).ifPresent(port -> applyResult(event, port.interact(
                player,
                new ModeObjectInteractionContext(
                        port.roomId(),
                        event.getHand(),
                        null,
                        null,
                        null,
                        heldItem(player, event)))));
    }

    @SubscribeEvent
    public static void onEntityInteract(PlayerInteractEvent.EntityInteract event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || player.level().isClientSide) {
            return;
        }
        FpsMatchGateway gateway = FpsMatchGatewayProvider.gateway();
        gateway.findPlayerInteractableObjectPort(player).ifPresent(port -> applyResult(event, port.interact(
                player,
                new ModeObjectInteractionContext(
                        port.roomId(),
                        event.getHand(),
                        null,
                        null,
                        event.getTarget(),
                        heldItem(player, event)))));
    }

    private static ItemStack heldItem(ServerPlayer player, PlayerInteractEvent event) {
        return event.getHand() == null ? ItemStack.EMPTY : player.getItemInHand(event.getHand()).copy();
    }

    private static boolean isBlockHandledByOwnUse(PlayerInteractEvent.RightClickBlock event) {
        return ModeObjectInteractionBypassContributors.handlesOwnUse(
                event.getLevel().getBlockState(event.getPos()));
    }

    private static void applyResult(PlayerInteractEvent.RightClickBlock event, InteractionResult result) {
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
    }
}
