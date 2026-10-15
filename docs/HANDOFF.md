# 可恢复交接

## 当前授权与恢复锚点

- 唯一仓库：[Zwhao0/20261015](https://github.com/Zwhao0/20261015)。当前 [Issue #6](https://github.com/Zwhao0/20261015/issues/6)，母 #1；用户于2026-10-15明确指令“启动 M0-2”，历史“M0-2未授权”不再适用。M0-3/M1仍未授权。
- 分支 `codex/m0-2-capability-matrix` 初始从main 4ae0555…建立，发布前已快进最新main `4d93a08d76a10ff9a52fba68b84cba2d5fc6475a`（PR #5合并）。当前PR由该分支关联的Draft PR确认，精确最新head/tree/CI从PR描述/Checks核对；不猜SHA、不用旧CI替代。
- M0-1 [PR #5](https://github.com/Zwhao0/20261015/pull/5) 的 [独立审核](https://github.com/Zwhao0/20261015/pull/5#issuecomment-6188441126) 限调查交付PASS；本轮启动时Open/Ready/Unmerged、draft=false；发布前核实GitHub已合并为上述main，Codex未操作合并。输入固定head `f15050dc1c4b8bf5cd5e49d75576f19ecf7b269d` 的[18条证据](https://github.com/Zwhao0/20261015/blob/f15050dc1c4b8bf5cd5e49d75576f19ecf7b269d/docs/M0_1_INVENTORY.md)。最新main/本分支同名文件已含完整18条；文件与固定输入一致，原补证分支保留。
- 本轮离线完成[能力矩阵](M0_2_CAPABILITIES.md)与版本条件/降级/补证门禁，待独立审核。没有重新SSH/读凭据、访问metrics/任务日志、查询RAS、触发FR、启动GPU/训练/collective或配置变更；这些均NOT_RUN。M0-Gate与实际信号兼容性INCONCLUSIVE，不进入M0-3/M1。

## 必须保留的事实与缺口

- 首轮实际采集16:08:10～16:12:18、补证16:36:01～16:42:26，均2026-10-15 UTC+08:00；A/B各自独立。公开摘要哈希只证明一致性，不证明主机来源真实性，本轮没有私密原始记录重验。
- A/B C1各有Torch2.13.0+cu130、Toolkit13.0.88、CPU导入成功/CUDA未初始化；NCCL包/header2.30.7、Torch编译API2.29.7、探查进程实际库2.30.7。差异不等于故障或ABI通过，不更换库。真实训练进程栈/完整Rank映射/进度/metrics/日志/RAS/FR信号与跨机精度UNKNOWN。
- C1来源仍需环境所有者确认是可合法复用的通用运行时，确认前不作为开发/测试环境；不得通过打开禁止的旧项目核实。后续主机读取/测试需明确对象和授权条件，参见V1～V7；本轮不自动安排执行。
- 用户曾授权既有容器与现有sudo供M0-1版本补证，后来明确取消清理。**不得恢复清理：不删除/停止/重启/新建容器，不删除镜像/卷。** 本轮无现场变更。
- 原始证据、私密连接入口/使用指南只在先前授权本机受控索引，公开LOCAL/<ID>不提供登录能力；本轮未读取。无受控材料不能声称重验现场。首轮/补证所有失败仍在PR #4/#5及固定快照，不因后续成功删除。

## 新会话恢复顺序

1. 读README/AGENTS、Issue #6/#1、当前M0-2 Draft PR的diff/讨论/Checks、STATUS/HANDOFF/M0_BASELINE/M0_2_CAPABILITIES，及PR #5固定证据和独立审核。
2. `git status --short --branch`、`git remote -v`；非干净先保留调查，不reset/覆盖。fetch main与M0-2开发分支、必要时只fetch前序补证分支，核对GitHub实时base/head和前序PR状态。
3. 干净工作区可跟踪开发分支并`git pull --ff-only`；核对`git rev-parse HEAD`/tree与PR。PR #5已合并，本分支基于其main合并提交；若main再更新先核对差异，保留两阶段事实与18条证据，不擅自覆盖。
4. 按STATUS复核文档与公开摘要；S1～S9为官方资料，归档/标签有适用版本；不得用更新教程默认值或上游标签冒充现场配置/构建。当前只需M0-2文档独立审核与已授权范围修正，不把UNKNOWN转PASS。
5. 现场补证均NOT_RUN；如后续用户授权，先核对任务身份、运行时来源、安全边界与V项条件。不自动运行GPU、查询共享作业RAS或触发dump，不实施M0-3/M1。

## 上下文与发布协议

- ChatGPT独立审核：从自己的窗口首个用户问题计，每5问交接，过长提前；输出可复制说明并核实GitHub可恢复，不能自动替用户开窗。Codex轮数不代替外部ChatGPT计数。
- 主智能体要求6.1 Sol/High；没有可靠回读，不声称已核验。每小任务写状态；约2/3上下文、压缩前或决定难追溯时，先保存安全工作/STATUS/HANDOFF并发布，再交回PR/commit/检查/阻塞，未完成不得标完成。
- 子智能体仅明确委派时使用6 Luna/Max；输入、可改范围、DoD、证据/访问边界须明确；不改最终共享STATUS/HANDOFF、不直接合并，配置不可用记录阻塞，不自行换模型。本轮没有子智能体。
- 终端历史上无GitHub推送凭据；可用已连接Git data创建tree/commit、创建开发分支或expected SHA/force=false更新，再fetch核对本地tree/祖先。无需用户提供秘密。发布失败必须记录未推送内容与症状，明确GitHub尚不可完整恢复；不以本地完成冒充已发布。
- 检查使用PASS/FAIL/NOT_RUN/INCONCLUSIVE并记录内容、命令、环境、退出码与证据；文档CI不是现场功能验证。详见[AGENTS](../AGENTS.md)。

## 可复制到ChatGPT新窗口

```text
唯一仓库：https://github.com/Zwhao0/20261015
当前任务：https://github.com/Zwhao0/20261015/issues/6，母Issue #1；用户已明确授权启动M0-2。
请读README/AGENTS、STATUS/HANDOFF/M0_BASELINE/M0_2_CAPABILITIES、当前M0-2分支关联Draft PR的diff/讨论/Checks。
分支：codex/m0-2-capability-matrix，启动main=4ae0555…，发布base/main=4d93a08d76a10ff9a52fba68b84cba2d5fc6475a（PR #5合并）。
最新PR/精确head/tree/CI从分支关联PR核实，不猜测。
前序PR #5启动时Open/Ready/Unmerged，发布前GitHub已合并；调查交付已获独立审核PASS，Codex未操作合并。
输入固定PR #5/head f15050dc1c4b8bf5cd5e49d75576f19ecf7b269d 的docs/M0_1_INVENTORY.md，共18条；最新main/本分支同名文件已含完整18条，内容未改。
M0-2交付9行矩阵、官方版本来源与V1～V7补证条件；待独立审核，真实信号/兼容性INCONCLUSIVE。
本轮未SSH/读凭据/读metrics日志/查RAS/触发FR/运行GPU或训练；不得说现场复测通过。
NCCL编译API2.29.7/探查库2.30.7保留；C1通用运行时来源待环境所有者确认，确认前不用作开发/测试。
用户已取消清理；不删除/停止/重启/新建容器，不删除镜像/卷。
完整身份链、进度、真实信号与跨机精度UNKNOWN。M0-3/M1未授权，M0-Gate未通过；不合并PR。
ChatGPT五问计数由外部窗口自行维护，新窗口从自己的首问计数。
```

## 阻塞记录模板

```text
编号/阶段/日期；症状与脱敏证据位置；动作/命令/退出码/结果；
branch/commit/PR/未发布内容；影响与安全剩余工作；
候选方案/依据/风险；恢复条件/授权/路径。
原始敏感材料仅留授权位置，不能用公开摘要一致性代替现场真实性。
```
