package com.cdp.codpattern.adapter.neoforge.network;

/**
 * 取代已删除的 {@code net.minecraftforge.network.NetworkDirection}。
 * <p>
 * 只保留上游用到的两个方向常量（实测：PLAY_TO_SERVER 28 处、PLAY_TO_CLIENT 31 处）。
 */
public enum NetworkDirection {
    PLAY_TO_SERVER,
    PLAY_TO_CLIENT
}
