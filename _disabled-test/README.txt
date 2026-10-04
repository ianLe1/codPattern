上游 1.20.1/Forge 时代的 JUnit 源码测试（41 文件 / 492K）。
1.21.1 NeoForge + moddev 构建下，这些测试引用的 gson / BuiltInRegistries / net.minecraft.server.level
等符号在 test 源集里不可见（上游靠 ForgeGradle 的测试配置提供），compileTestJava 因此报 186 个错误。
它们不参与 mod jar 的构建，故移到此处以免 `./gradlew build` 失败。
要恢复：mv _disabled-test src/test
