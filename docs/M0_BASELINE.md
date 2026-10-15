# M0 技术基线（骨架）

依据：[README](../README.md)、[Issue #1](https://github.com/Zwhao0/20261015/issues/1)。2026-10-15 仅交付 M0-0；本页没有环境调查或功能实现结论。

## 路线与门禁

M0 技术基线 → M1 Observability → M2 Fail-Stop → M3 Hang → M4 Fail-Slow → M5 Evidence-based Diagnosis & Delivery。
M0-1～M0-3 填充以下材料后，由 ChatGPT 独立审核、用户最终批准 M0-Gate；当前 `INCONCLUSIVE`，不自动进入 M1。

## M0-0 决策记录

| 问题 | 选项与选择 | 依据 | 风险及验证 |
| --- | --- | --- | --- |
| 初始化放多少工程工具 | 选择 Markdown + Python 标准库检查 + 单个 CI；暂不引入应用脚架/训练依赖 | Issue 要求最小初始化，环境尚未调查 | 检查覆盖有限；运行检查并人工审核语义、权限与敏感信息 |
| 状态如何跨会话恢复 | GitHub Issue/PR + STATUS/HANDOFF；不依赖聊天记忆 | Issue 明确规定事实基线与上下文检查点 | 状态可能过时；每小任务更新并核对 PR head/Checks |
| CI 如何接入 | 普通 push/PR 工作流，contents 只读、checkout 固定 commit、关闭凭据持久化 | 只需仓库文档验证；无需 GPU、服务器或部署密钥 | runner/托管 Action 是外部依赖；保留本地相同检查命令，故障时记录而非绕过 |
| 技术栈何时确定 | 先留 UNKNOWN，后续授权调查后决策；不预装 PyTorch/CUDA 等 | 避免猜测 H800 环境或提前开展 M1 | 目前不能证明兼容性；须由 M0-1/2 的事实与证据验证 |

## M0-1 环境事实表（NOT_RUN）

用户描述的“两台 H800”只作为待核实输入，不是已确认硬件事实。不记录连接信息；只有后续明确授权才能执行只读调查。

| 对象 | GPU / OS / Driver / CUDA / NCCL / PyTorch / 训练框架 | 运行方式 / 日志 / 指标 | 证据编号 |
| --- | --- | --- | --- |
| 授权节点 A（脱敏代号） | UNKNOWN | UNKNOWN | 无；未调查 |
| 授权节点 B（脱敏代号） | UNKNOWN | UNKNOWN | 无；未调查 |

## 原始证据索引（待填）

每条证据记录：编号、采集时间与时区、授权范围、脱敏对象代号、命令/版本、是否真实运行、退出码、原始材料在授权机器的位置、脱敏摘要/校验值、对应 commit/PR。原始敏感日志留在授权机器；公开索引不得暴露 IP、用户名、密钥、内部路径或训练数据。

当前无服务器或训练证据。仓库工程验证见 [STATUS](STATUS.md) 与 Draft PR。

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
- [actions/checkout v4.2.2](https://github.com/actions/checkout/releases/tag/v4.2.2)：CI 引用官方 Action `11bd71901bbe5b1630ceea73d27597364c9af683`，MIT 许可证；仅检出本仓库，不将其代码复制入项目。
- 未引入旧项目、外部训练实现或算法代码；项目自身许可证尚未指定，后续需由所有者决定，不擅自添加。
