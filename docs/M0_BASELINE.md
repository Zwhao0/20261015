# M0 技术基线

依据：[README](../README.md)、母 [Issue #1](https://github.com/Zwhao0/20261015/issues/1)、当前 [Issue #3](https://github.com/Zwhao0/20261015/issues/3)。2026-10-15（Asia/Shanghai）更新 M0-1 真实只读调查；M0-0 已审核并合并，未实现监控/检测功能。

## 路线与门禁

M0 技术基线 → M1 Observability → M2 Fail-Stop → M3 Hang → M4 Fail-Slow → M5 Evidence-based Diagnosis & Delivery。
M0-1～M0-3 填充以下材料后，由 ChatGPT 独立审核、用户最终批准 M0-Gate；当前 `INCONCLUSIVE`，不自动进入 M1。

## M0-0 决策记录

| 问题 | 选项与选择 | 依据 | 风险及验证 |
| --- | --- | --- | --- |
| 初始化放多少工程工具 | 选择 Markdown + Python 标准库检查 + 单个 CI；暂不引入应用脚架/训练依赖 | Issue 要求最小初始化，环境尚未调查 | 检查覆盖有限；运行检查并人工审核语义、权限与敏感信息 |
| 状态如何跨会话恢复 | GitHub Issue/PR + STATUS/HANDOFF；不依赖聊天记忆 | Issue 明确规定事实基线与上下文检查点 | 状态可能过时；每小任务更新并核对 PR head/Checks |
| CI 如何接入 | 普通 push/PR 工作流，contents 只读、checkout v7.0.1 固定 commit、关闭凭据持久化 | 首轮 v4 检查通过但有 Node 20 弃用警告；改用官方 Node 24 版本，已观察 runner 2.337.0 满足最低要求 2.327.1 | runner/托管 Action 是外部依赖；变更后重跑 CI，保留本地相同检查命令 |
| 技术栈何时确定 | 先留 UNKNOWN，后续授权调查后决策；不预装 PyTorch/CUDA 等 | 避免猜测 H800 环境或提前开展 M1 | 目前不能证明兼容性；须由 M0-1/2 的事实与证据验证 |

## M0-1 环境事实（容器补证待审核；训练验收 INCONCLUSIVE）

起点 main `41a30e011b3fb0074aaef7cb8c42070aef4562b1`。首轮宿主机快照 2026-10-15 16:08:10～16:12:18 Asia/Shanghai（UTC+08:00），容器补证 16:36:01～16:42:26 同时区；A/B 均独立执行，不继承旧项目环境结论。用户新增容器与既有 sudo 访问授权，优先复用环境；清理容器的请求在执行前被用户取消，删除/停止/重启/新建均为 0。

| 事实与状态 | A（独立采集） | B（独立采集） | 证据与限制 |
| --- | --- | --- | --- |
| GPU / 显存 OBSERVED | 8×NVIDIA H800；每卡 81559 MiB | 同规格，独立采集 | E-A-01 / E-B-01，exit 0；没有 GPU 计算验收 |
| Driver / 驱动声明 CUDA OBSERVED | 580.178.04 / 13.0 | 同版本，独立采集 | 各自 01；驱动声明不等于 Runtime/Toolkit |
| OS / Kernel OBSERVED | Ubuntu 24.04 / Linux 6.8.0-146-generic x86_64 | Ubuntu 24.04 / Linux 6.8.0-139-generic x86_64 | 各自 01；内核不同 |
| CPU / MemTotal OBSERVED | 192 逻辑 CPU / 1056430708 kB | 192 逻辑 CPU / 1056419436 kB | 各自 01；不是容器 cgroup 配额 |
| 默认宿主机 Python OBSERVED | 3.12.3，指定 Torch 元数据未发现 | 同版本，独立采集 | 各自 01/02；不能外推到容器，原拒绝访问已解除 |
| 当前复用候选 C1 OBSERVED | running、未暂停；容器 Ubuntu 24.04 / Python 3.12.3 | 同状态/版本，独立采集 | 各自 06/07；只查系统与第三方包，不读取/复制旧项目 |
| 容器 PyTorch OBSERVED | 2.13.0+cu130，CPU 导入 exit 0 | 同版本/结果，独立采集 | 各自 07/08/09；is_initialized 查询前后均 false；GPU/训练 NOT_RUN |
| Torch 构建 CUDA / Toolkit OBSERVED | 13.0 / nvcc 13.0.88 | 同版本，独立采集 | 各自 07/09；构建声明与编译器版本分列 |
| 当前探查进程 CUDA Runtime OBSERVED / UNKNOWN | 已映射 libcudart.so.13；补丁版本 UNKNOWN | 同左，独立采集 | 各自 08/09；未调用 CUDA 初始化/内核；真实训练进程 Runtime UNKNOWN |
| NCCL 包 / 头文件 OBSERVED | nvidia-nccl-cu13 2.30.7 / header 2.30.7 | 同版本，独立采集 | 各自 07；安装事实不等于 Torch 版本 API |
| Torch NCCL 版本 API OBSERVED | (2,29,7)，raw 8591835143 | 同值，独立采集 | 各自 09；不冒称为实际训练进程加载版本 |
| 本次探查进程实际 NCCL 库 OBSERVED | libnccl.so.2，RTLD_NOLOAD 后 ncclGetVersion code 23007 / exit 0（2.30.7） | 同值，独立采集 | 各自 09；版本 API 与运行库不同，兼容性 INCONCLUSIVE；真实训练进程已加载库 UNKNOWN |
| 容器框架包 OBSERVED | Transformers 5.17.0 / Accelerate 1.15.0 | 同版本，独立采集 | 各自 07；元数据，不代表真实训练框架/启动器版本 |
| 真实训练/launcher/任务来源 UNKNOWN | 未识别获准本项目任务；Job/Run/Rank/Local Rank UNKNOWN | 同左 | PID/GPU 字段在 04 可读，但未读取未知归属进程 args/env/日志；真实分布式启动方式未验证 |
| Docker/容器 Toolkit OBSERVED | client 29.1.3；docker.io 29.1.3-0ubuntu3~24.04.2 / Toolkit 包 1.20.1-1 | 同版本，独立采集 | 各自 02/04；06 后以授权现有 sudo 成功查询，未改权限 |
| DCGM / Exporter 安装 OBSERVED | core/proprietary 1:4.6.1-1；exporter 4.8.4.3955-1 | 同版本，独立采集 | 各自 02/03；不等于正在产出指标 |
| 现有观测 / RAS / Flight Recorder | exporter/node_exporter 进程线索；配置/实际信号 UNKNOWN；RAS/FR UNKNOWN | 同左 | 各自 02/04；版本查询不是观测能力测试，不访问日志或 metrics 端点 |
| 时间线索 OBSERVED / INCONCLUSIVE | Etc/UTC，NTP=yes/同步报告yes；chrony 4.5-1ubuntu4.2；tracking exit 1/506 | 同左，独立采集 | 各自 01/03/04；偏差/跨机精度 UNKNOWN；未改时钟 |
| 时钟 API OBSERVED | time=CLOCK_REALTIME；monotonic/perf_counter=CLOCK_MONOTONIC | 同左，独立采集 | 各自 02；不是训练事件时间来源证据 |

## M0-1 证据、已解决阻塞与剩余缺口

[只读调查记录](M0_1_INVENTORY.md) 保存两轮授权、方案、实际命令、18 条证据（A/B 各 01～09）、精确 UTC 起止、分层退出码、规范 JSON 摘要/哈希和失败恢复。首轮 8 条摘要/哈希保持原文；新增 10 条单列，不能混用时间/作用域。敏感原始材料仅留本机授权受控索引，公开逻辑 `LOCAL/<ID>` 不泄露真实身份/路径，摘要哈希不替代原始证据独立审核。

- **B-Container 已对版本补证解除**：使用本轮明确授权的现有 sudo 权限，未修改用户组/socket/sudoers。B 首次认证 exit 1，随后使用已提供的登录凭据成功；原失败保留。
- 已找到可复用的现有环境，未触发下载/上传/构建条件。仅证明 C1 的版本读取与 CPU 导入；不把候选升级为 GPU/双机训练通过，不复用旧项目代码/构建内容。
- Torch NCCL API 2.29.7 与本进程 ncclGetVersion 2.30.7 差异已观察；不推断兼容与否，不更换库。实际训练入口/launcher、Runtime 完整版本、训练进程已加载库、Rank、日志/指标配置、RAS/FR 与时钟精度仍 UNKNOWN / NOT_RUN。
- 清理 CANCELLED / NOT_RUN，无容器/镜像/卷删除；原始数据和既有运行容器保留。
- [PR #4 独立审核](https://github.com/Zwhao0/20261015/pull/4#issuecomment-6187891676) 仅覆盖旧宿主机快照 `1dced3b…`。原 PR #4 已合并，最新 main 为 `4ae0555c6fca24a6082e8e6af4ac40f107cb6716`。本轮以 `codex/m0-1-container-inventory` 提交 [Draft PR #5](https://github.com/Zwhao0/20261015/pull/5)，base=最新 main，新的 head/CI/审核单独记录。M0-Gate 与训练层仍 INCONCLUSIVE，用户未授权 M0-2/M0-3/M1。

## M0-2 观测能力与兼容性矩阵（NOT_RUN）

调查后仅使用“直接可得 / 需配置或版本支持 / 不可得 / UNKNOWN”，每个结论附证据和失败降级；下列均为待核查项。

| 能力 | 可用性 | 版本/配置约束、证据、降级 |
| --- | --- | --- |
| Job / Run / Host / PID / Rank / GPU UUID 映射 | UNKNOWN | 待调查 |
| 时间戳语义与跨机时钟 | UNKNOWN | 待调查 |
| 训练进度 | UNKNOWN | 待调查 |
| DCGM 与现有日志/指标 | UNKNOWN | 待调查 |
| NCCL RAS | UNKNOWN | 待调查 |
| Flight Recorder | UNKNOWN | 待调查 |

## M0-3 最小端到端切片及验收（NOT_RUN）

候选方向来自 Issue：真实任务基础观测与异常退出事件，尚未选定或实现。后续授权任务需填：

- 真实训练证据来源、明确的切片目标与非目标。
- 数据契约：对象身份、事件/时间戳语义、进度、来源和证据引用。
- 可用性/开销约束、采集失败降级与 `UNKNOWN` 传播。
- 本地轻量测试/回放、双机集成步骤、预期结果与验收阈值。
- 回退步骤、共享训练保护、执行所需授权；M0 仅方案，M1 才实现。

## M0-Gate 材料与审核（INCONCLUSIVE）

待补：环境事实及原始/脱敏证据索引、能力矩阵、待验证假设、V0.1 切片与可执行验收/回退方案、明确的 M1 候选 Issue 列表。
审核时填写：范围、被审核 SHA/PR、证据、`PASS/FAIL/INCONCLUSIVE`、ChatGPT 审核意见、用户最终批准及日期；目前均未完成。

## 外部来源

- [GitHub Actions 事件文档](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)：参考 push/普通 pull_request 触发方式。
- [actions/checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1)：CI 引用官方 Action `3d3c42e5aac5ba805825da76410c181273ba90b1`；[运行时声明](https://github.com/actions/checkout/blob/v7.0.1/action.yml)、[兼容性说明](https://github.com/actions/checkout/blob/v7.0.1/README.md)、[MIT 许可证](https://github.com/actions/checkout/blob/v7.0.1/LICENSE)。仅检出本仓库，不将其代码复制入项目。
- 未引入旧项目、外部训练实现或算法代码；项目自身许可证尚未指定，后续需由所有者决定，不擅自添加。
