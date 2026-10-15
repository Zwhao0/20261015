# M0 技术基线

依据：[README](../README.md)、母 [Issue #1](https://github.com/Zwhao0/20261015/issues/1)及[M0-Gate 正式审核记录](M0_GATE.md)。2026-10-15（Asia/Shanghai）用户授权启动 M0-Gate 正式审核记录，随后明确“批准执行M0-GATE”；首版仅登记执行授权，整体Gate当时INCONCLUSIVE。2026-10-15后续[用户最终批准记录](https://github.com/Zwhao0/20261015/issues/1#issuecomment-6190108253)已登记最终验收批准，现按[PR #10修正要求](https://github.com/Zwhao0/20261015/pull/10#issuecomment-6190117664)同步限定范围PASS。M0-3 PR #9/head `1ef24fe27a63791857c8bf8fb2b59b715b61e542` 已获[独立设计复审 PASS](https://github.com/Zwhao0/20261015/pull/9#issuecomment-6189756035)，合并基线 main `42bce13c5bd925c74856f96de64f431526d142bf`，tree `b83c0ed32dfac917701b81be53ea5de37c75b2af` 与审核 head 相同。以下 M0-0～M0-2 的时间、版本、授权及失败为历史事实，保留原适用范围；最新门禁以正式记录为准，M1 未授权。

## 路线与门禁

M0 技术基线 → M1 Observability → M2 Fail-Stop → M3 Hang → M4 Fail-Slow → M5 Evidence-based Diagnosis & Delivery。
M0-0～M0-3 材料已获各自限范围独立审核 PASS；[整体技术审查](https://github.com/Zwhao0/20261015/issues/1#issuecomment-6189883744)认为离线设计就绪。用户最终批准现已取得，整体 M0-Gate 为 PASS（限工程基线/离线调查、矩阵、V0.1设计及M1-C1离线编码技术准备）；真实接入/兼容/开销仍INCONCLUSIVE，M1执行未授权。

## M0-0 决策记录

| 问题 | 选项与选择 | 依据 | 风险及验证 |
| --- | --- | --- | --- |
| 初始化放多少工程工具 | 选择 Markdown + Python 标准库检查 + 单个 CI；暂不引入应用脚架/训练依赖 | Issue 要求最小初始化，环境尚未调查 | 检查覆盖有限；运行检查并人工审核语义、权限与敏感信息 |
| 状态如何跨会话恢复 | GitHub Issue/PR + STATUS/HANDOFF；不依赖聊天记忆 | Issue 明确规定事实基线与上下文检查点 | 状态可能过时；每小任务更新并核对 PR head/Checks |
| CI 如何接入 | 普通 push/PR 工作流，contents 只读、checkout v7.0.1 固定 commit、关闭凭据持久化 | 首轮 v4 检查通过但有 Node 20 弃用警告；改用官方 Node 24 版本，已观察 runner 2.337.0 满足最低要求 2.327.1 | runner/托管 Action 是外部依赖；变更后重跑 CI，保留本地相同检查命令 |
| 技术栈何时确定 | 先留 UNKNOWN，后续授权调查后决策；不预装 PyTorch/CUDA 等 | 避免猜测 H800 环境或提前开展 M1 | 目前不能证明兼容性；须由 M0-1/2 的事实与证据验证 |

## M0-1 环境事实（限调查目的审核 PASS；训练验收 INCONCLUSIVE）

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
- [PR #4 独立审核](https://github.com/Zwhao0/20261015/pull/4#issuecomment-6187891676) 仅覆盖旧宿主机快照 `1dced3b…`。原 PR #4 已合并，当时 main 为 `4ae0555c6fca24a6082e8e6af4ac40f107cb6716`。容器补证 [PR #5](https://github.com/Zwhao0/20261015/pull/5)/head `f15050dc1c4b8bf5cd5e49d75576f19ecf7b269d` 已获[独立审核](https://github.com/Zwhao0/20261015/pull/5#issuecomment-6188441126)限调查目的PASS；启动M0-2时尚未合并，发布前已合并为main `4d93a08d76a10ff9a52fba68b84cba2d5fc6475a`。当轮用户明确授权M0-2；当时M0-Gate与训练层仍INCONCLUSIVE，M0-3/M1尚未授权；最新M0-3授权见本文开头。C1通用运行时来源仍需所有者确认，确认前不作为开发/测试环境。

## M0-2 观测能力与兼容性矩阵（离线材料审核 PASS，已合并）

完整 [M0-2 矩阵](M0_2_CAPABILITIES.md) 给出9行能力、A/B独立证据、版本适用条件、失败降级、V1～V7补证条件与官方来源。

| 能力 | 结论（只限历史快照与文档条件） |
| --- | --- |
| Host/PID/GPU UUID 局部字段 | 历史采样直接可得；Job/Run/Rank/Local Rank 完整关联 UNKNOWN |
| 时间语义 | 本机 API 语义直接可得；真实事件时间源/跨机精度 UNKNOWN |
| 训练进度 | UNKNOWN，不能用GPU利用率/存活替代 |
| DCGM/主机 metrics/日志 | 安装/进程线索存在，实际来源与信号 UNKNOWN |
| NCCL RAS | 需配置或版本支持；2.30.7归档有路径，实际任务配置与信号 UNKNOWN |
| PyTorch Flight Recorder | 需配置或版本支持；上游v2.13.0有实现，本地构建/启用/导出 UNKNOWN |

M0-2轮现场测试 NOT_RUN，完整运行兼容性 INCONCLUSIVE；没有证据支持把未知项判“不可得”或健康。原矩阵按历史快照保留，其中“待审核/M0-3未授权”是当轮状态；最新审核与授权以上文、STATUS和当前Issue为准。

## M0-3 最小端到端切片及验收（设计复审 PASS，PR #9 已合并）

选定V0.1：一个明确获准真实任务的基础观测及进程异常退出。完整[切片方案](M0_3_SLICE.md)包含：

- 任务所有者清单/启动器权威终止记录作为证据入口；当前真实来源仍UNKNOWN，不依赖旧项目或未核实RAS/FR/step。
- Job/Run/attempt、Host/boot/namespace/PID/start、Rank/Local Rank/GPU、时间域、退出编码与证据索引契约；缺链只展示局部字段。
- 进程/任务作用域、重启、缺样本、源失败/轮转/乱序等UNKNOWN规则，以及14类未来回放用例。
- I0～I5双机接入/验收步骤、量化资源/延迟预算和回退；现场命令须待真实对象批准后在M1 PR落实。
- M1候选C1～C4及DoD，仅列表不创建/启动任务。M0只做设计；功能回放/双机/开销测试均NOT_RUN。

## M0-Gate 材料与审核（限定范围PASS）

[正式审核记录](M0_GATE.md)汇总 M0-0～M0-3 的审核 SHA、合并事实、证据和批准栏。独立审查来源为[Issue #1 评论](https://github.com/Zwhao0/20261015/issues/1#issuecomment-6189883744)，Codex 本轮只登记及核对，不替代独立审核者。

- 离线设计交付及 M1-C1 离线编码技术准备：PASS（独立技术审查结论）。
- 真实训练接入、信号有效性、兼容与低开销：INCONCLUSIVE；真实来源/身份/权威退出/运行时来源/受控存储/时钟及现场命令仍缺。
- T01～T14 功能回放、CPU子进程、I0～I5、GPU/collective及开销：NOT_RUN。
- 整体 M0-Gate：PASS（限工程基线/离线调查、矩阵、V0.1设计及M1-C1离线编码技术准备）。2026-10-15用户在ChatGPT中明确回答“批准”，[用户最终批准记录](https://github.com/Zwhao0/20261015/issues/1#issuecomment-6190108253)记录原提问与范围；先前仅授权记录时的INCONCLUSIVE过程保留于正式记录和历史STATUS。M1执行仍未授权，C2～C4真实接入/服务器授权另行取得；不以文档PASS代替功能验收。

## 外部来源

- [GitHub Actions 事件文档](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)：参考 push/普通 pull_request 触发方式。
- [actions/checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1)：CI 引用官方 Action `3d3c42e5aac5ba805825da76410c181273ba90b1`；[运行时声明](https://github.com/actions/checkout/blob/v7.0.1/action.yml)、[兼容性说明](https://github.com/actions/checkout/blob/v7.0.1/README.md)、[MIT 许可证](https://github.com/actions/checkout/blob/v7.0.1/LICENSE)。仅检出本仓库，不将其代码复制入项目。
- 未引入旧项目、外部训练实现或算法代码；项目自身许可证尚未指定，后续需由所有者决定，不擅自添加。
