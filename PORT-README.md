# codPattern — 1.21.1 / NeoForge 移植

把 [codPattern](https://github.com/popura404/codPattern)（1.20.1 Forge）移植到
**Minecraft 1.21.1 + NeoForge 21.1.253**。分支 `1.21.1-neoforge-port`。

上游：`popura404/codPattern`，GPL-3.0-only。移植基于上游 `4b03abf`（`main`）。

## 这是什么

codPattern 是 TaCZ 的玩法附属，自带 `frontline`(FTL) 与 `teamdeathmatch`(TDM) 两个模式。
它**不是** FPSMatch 的附属——它把一套 FPSM 兼容核心内嵌在自己内部
（`com.phasetranscrystal.fpsmatch.*`，90 个类；FPSMatch 新版已改名到 `net.ptcrys.fpsmatch.*`），
所以它不依赖 `fpsmatch.jar`，也不与 FPSMatch 交换代码。

## 状态

| 项 | 结果 |
|---|---|
| 编译 | 错误 1234 → 526 → 424 → 128 → 13 → 0 |
| 产物 | `build/libs/codpattern-0.8.6b-1.21.1-port.jar` |
| 服务端实机 | 与 FPSMatch / BlockOffensive 同服启动成功：`Done (1.224s)`，零新增报错 |

## 构建

```bash
GRADLE_USER_HOME=$PWD/.gradle-home ./gradlew build --offline
```

`libs/` 需要第三方 jar，见 [libs/README.md](libs/README.md)（不入库）。
**不要跑 `./gradlew clean`**（NeoForge 中间工件不在离线缓存里，清掉后无法重新解析）。

## port-tools/

移植过程中写的定点修复脚本（幂等），与 FPSMatch / BlockOffensive 的 `tools/` 同类。

## 许可

上游 GPL-3.0-only，本移植同样以 GPL-3.0-only 发布，见 [LICENSE.txt](LICENSE.txt)。
依 GPLv3 §5(a) 声明：本分支相对上游做了修改，修改内容即上述移植改动。
