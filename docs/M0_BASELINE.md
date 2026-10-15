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

## M0-1 环境事实（待独立审核；训练层 INCONCLUSIVE）

起点 main `41a30e011b3fb0074aaef7cb8c42070aef4562b1`。用户当前明确授权两台指定服务器与连接信息文件的访问，实际只使用只读权限；没有沿用旧项目事实。采集于 2026-10-15 16:08:10～16:12:18 Asia/Shanghai（UTC+08:00）。下表 OBSERVED 限定于本次快照/命名空间，UNKNOWN 不能解释为未安装。

| 事实与状态 | A（独立采集） | B（独立采集） | 证据与限制 |
| --- | --- | --- | --- |
| GPU / 显存 OBSERVED | 8×NVIDIA H800；每卡 81559 MiB | 8×NVIDIA H800；每卡 81559 MiB | E-A-01 / E-B-01，nvidia-smi query，exit 0；无 GPU 计算验收 |
| Driver / 驱动声明 CUDA OBSERVED | 580.178.04 / 13.0 | 580.178.04 / 13.0 | 各自 01；驱动 CUDA 声明不等于实际 Runtime/Toolkit |
| OS / Kernel OBSERVED | Ubuntu 24.04 / Linux 6.8.0-146-generic x86_64 | Ubuntu 24.04 / Linux 6.8.0-139-generic x86_64 | 各自 01，exit 0；内核不能跨节点外推 |
| CPU / 内存总量 OBSERVED | 192 在线逻辑 CPU / 1056430708 kB | 192 在线逻辑 CPU / 1056419436 kB | 各自 01，getconf / MemTotal，exit 0；非容器资源配额 |
| 登录环境/容器线索 OBSERVED | container 检测 none，exit 1；两个标准标记未见 | container 检测 none，exit 1；两个标准标记未见 | 各自 01/02；支持宿主机视图线索，不证明全部隔离状态 |
| 默认 Python OBSERVED | 3.12.3 | 3.12.3 | 各自 01/02，exit 0；不替代实际训练解释器 |
| PyTorch / 训练 Python / 框架 UNKNOWN | 当前默认解释器未发现指定包元数据；实际训练版本 UNKNOWN | 同左，独立采集 | 各自 02；torch/deepspeed/transformers/accelerate/lightning/pytorch-lightning/megatron-core 清单见调查，不扫描其他环境 |
| CUDA Runtime / Toolkit UNKNOWN | Runtime UNKNOWN；nvcc 不在 PATH、默认位置未见 | 同左，独立采集 | 各自 01/02；不是全机未安装断言 |
| Torch 构建 CUDA/NCCL / 已加载 NCCL UNKNOWN | 均 UNKNOWN | 均 UNKNOWN | 各自 02；包元数据未发现，未 import/attach；其它可执行/系统 NCCL 版本亦 UNKNOWN |
| 训练启动/分布式 launcher UNKNOWN | 未读获准任务入口，实际启动器/版本 UNKNOWN | 同左 | 各自 01/02；torchrun/srun/mpirun 不在 PATH 不证明任务未使用它们 |
| Docker/容器 Toolkit OBSERVED | client 29.1.3；包 29.1.3-0ubuntu3~24.04.2 / 1.20.1-1 | 同版本，独立采集 | 各自 02/04；docker ps exit 1 permission denied，容器内部版本 NOT_RUN/BLOCKED |
| DCGM / Exporter 安装 OBSERVED | core/proprietary 包 1:4.6.1-1；exporter 包 4.8.4.3955-1 | 同版本，独立采集 | 各自 02/03；03 core/exporter 单项 exit 0，不等于正在产出信号 |
| 现有观测来源 OBSERVED / UNKNOWN | exporter/node_exporter comm 存在；配置/信号 UNKNOWN | 同左，独立采集 | 各自 02/04；指定 service 名 inactive/not-found 与进程线索并存，实际来源未查，未访问 metrics |
| NCCL RAS / Flight Recorder UNKNOWN | 安装/配置/信号均 UNKNOWN；API NOT_RUN | 同左 | 未读配置/任务日志、未调用 RAS/profiler，不以最新文档推断当前版本支持 |
| GPU compute-app 瞬时字段 OBSERVED | 02 时 0 行，04 时 8 行/8 PID/8 GPU | 02 时 8 行，04 时 8 行/8 PID/8 GPU | 各自 02/04；只发布聚合计数，不公开 PID/UUID，不推断为本项目训练 |
| Job/Run/Rank/Local Rank/Host-PID-GPU 关联 UNKNOWN | 除单机 PID-GPU 字段可读外，任务映射 UNKNOWN | 同左 | 无本项目可读任务标识；不读未知归属进程环境/args/日志，不形成 M0-2 能力判断 |
| 时区/同步线索 OBSERVED / INCONCLUSIVE | Etc/UTC；NTP=yes；NTPSynchronized=yes；chrony 4.5-1ubuntu4.2；tracking exit 1 | 同左，独立采集 | 各自 01/03/04；506 Cannot talk to daemon；跨机精度 UNKNOWN |
| 时钟 API OBSERVED | time=CLOCK_REALTIME；monotonic/perf_counter=CLOCK_MONOTONIC | 同左，独立采集 | 各自 02；仅 API 语义，不代表训练事件时间来源 |

## M0-1 原始/脱敏证据索引与未验证项

[只读调查记录](M0_1_INVENTORY.md) 保存采集前方案、精确命令、八条实际证据（E-A-01～04、E-B-01～04）、UTC 起止时间、各层退出码、公开摘要 SHA-256、失败记录及恢复条件。原始敏感材料仅留授权本机 Git 忽略目录、私下受控索引；公开逻辑引用 `LOCAL/<证据ID>` 不暴露实际路径。摘要哈希可验证公开摘要完整性，不能替代独立复核。精确 commit/PR/对应 CI 由本分支 Draft PR 描述保存。

- 容器读取 BLOCKED：现有登录账户对 Docker 清单无权限；没有提权或修改权限。
- 真实训练入口、训练 Python/Torch/Runtime/Toolkit/NCCL/框架版本、Rank 映射、已加载库均 UNKNOWN；获准任务内容读取 NOT_RUN。后续需任务所有者/管理员提供受控元数据与明确可读边界，不接触旧项目。
- metrics 端点/实际信号、训练日志/进度、RAS/Flight Recorder 配置/API、跨机同步精度均 UNKNOWN / NOT_RUN。未配置新观测或执行兼容性实验；M0-2/M0-3/M1 仍未执行。
- 关键决定、非零查询的解释、时间变化与失败保留见调查记录；不能给双机训练环境全量 PASS。等待 ChatGPT 独立审核，用户批准前不推进阶段。

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
