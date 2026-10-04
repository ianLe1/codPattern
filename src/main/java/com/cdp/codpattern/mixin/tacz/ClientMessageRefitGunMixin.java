package com.cdp.codpattern.mixin.tacz;

import com.cdp.codpattern.adapter.forge.network.ModNetworkChannel;
import com.cdp.codpattern.core.refit.AttachmentEditSessionManager;
import com.cdp.codpattern.network.SyncAttachmentCandidatesPacket;
import com.tacz.guns.network.message.ClientMessageRefitGun;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Inventory;
import net.neoforged.neoforge.network.handling.IPayloadContext;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(value = ClientMessageRefitGun.class, remap = false, priority = 900)
public abstract class ClientMessageRefitGunMixin {
    @Redirect(
            method = "lambda$handle$3",
            at = @At(
                    value = "INVOKE",
                    target = "Lnet/minecraft/server/level/ServerPlayer;getInventory()Lnet/minecraft/world/entity/player/Inventory;"
            )
    )
    private static Inventory codpattern$useRefitInventory(ServerPlayer player) {
        Inventory refitInventory = AttachmentEditSessionManager.getRefitInventory(player);
        return refitInventory == null ? player.getInventory() : refitInventory;
    }

    @ModifyVariable(method = "lambda$handle$3", at = @At("STORE"), ordinal = 0)
    private static Inventory codpattern$keepRefitInventoryVariable(Inventory inventory) {
        return codpattern$preferBackpackRefitInventory(inventory);
    }

    @Inject(
            method = "lambda$handle$3",
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/tacz/guns/network/NetworkHandler;sendToClientPlayer(Lnet/minecraft/network/protocol/common/custom/CustomPacketPayload;Lnet/minecraft/world/entity/player/Player;)V",
                    shift = At.Shift.BEFORE
            )
    )
    private static void codpattern$syncCandidatesBeforeRefresh(IPayloadContext context,
            ClientMessageRefitGun message,
            CallbackInfo ci) {
        if (!(context.player() instanceof ServerPlayer player)) {
            return;
        }
        if (AttachmentEditSessionManager.getSession(player.getUUID()) == null) {
            return;
        }
        ModNetworkChannel.sendToPlayer(new SyncAttachmentCandidatesPacket(
                AttachmentEditSessionManager.getSession(player.getUUID()).getBagId(),
                AttachmentEditSessionManager.getSession(player.getUUID()).getSlot(),
                AttachmentEditSessionManager.snapshotAttachmentCandidates(player)), player);
    }

    private static Inventory codpattern$preferBackpackRefitInventory(Inventory inventory) {
        if (inventory == null || !(inventory.player instanceof ServerPlayer player)) {
            return inventory;
        }
        Inventory refitInventory = AttachmentEditSessionManager.getRefitInventory(player);
        return refitInventory == null ? inventory : refitInventory;
    }
}
