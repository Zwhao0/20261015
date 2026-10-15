# 可恢复交接

## 当前入口与授权

- 唯一仓库：[Zwhao0/20261015](https://github.com/Zwhao0/20261015)。当前 [Issue #3](https://github.com/Zwhao0/20261015/issues/3)，母 Issue #1 继续打开。
- 仅 M0-1 只读环境事实调查。用户在当前会话明确批准访问指定服务器信息文件及两台服务器；连接信息不进入公开仓库。只读范围不包括未知归属任务的私有数据、旧项目文件、依赖/训练环境变更或故障注入。M0-2/M0-3/M1 未执行、未授权，不自动合并。
- M0-0 已获 [ChatGPT 第二轮 PASS](https://github.com/Zwhao0/20261015/pull/2#issuecomment-6187338743)，PR #2 已合并。当前起点 main `41a30e011b3fb0074aaef7cb8c42070aef4562b1`；旧 STATUS/HANDOFF 的 M0-0 限制仅为历史状态，已由本次正式授权更新。
- 分支 `codex/m0-1-inventory` → main，Draft PR 发布进行中。精确 head/tree/最终 CI 由关联 Draft PR 描述及 Checks 保存；写入时尚未合并。不要将 M0-0 或某个旧 HEAD 的 PASS 套到当前提交。

## 已完成、缺口与受控证据

- A/B 各四次真实只读会话，2026-10-15 16:08:10～16:12:18 Asia/Shanghai。各 8×H800、Driver 580.178.04、Ubuntu 24.04；内核分别 6.8.0-146/139-generic。八条 E-A-01～04/E-B-01～04 证据含命令、UTC 起止时间、执行状态、分层退出码、脱敏摘要 SHA-256，见 [调查记录](M0_1_INVENTORY.md) 与 [基线](M0_BASELINE.md)。
- GPU 活动存在时间变化；04 各见 8 PID/8 GPU 关联，只保留计数，不确认任务性质。默认宿主机 Python 3.12.3，无指定 Torch/框架包元数据；实际训练环境版本、启动方式、Rank/Job/Run、日志/metrics/RAS/Flight Recorder 配置与信号仍 UNKNOWN。未运行新训练/API/profiler，不是完整双机训练环境 PASS。
- Docker 读取 permission denied，容器证据 BLOCKED；Chrony tracking exit 1/506，详细时间偏差 UNKNOWN；dpkg 混合查询非零与独立成功均保留。恢复需管理员/任务所有者明确可读环境和元数据来源，不绕过权限，不触碰旧项目。
- 原始证据与连接解析器只在本机 Git 忽略受控目录中，权限目录 0700/文件 0600，公开仅逻辑引用 `LOCAL/<证据ID>`；公开 GitHub 无真实路径、凭据或主机身份。新本地会话向用户私下获取该索引；没有受控材料时只能核对公开摘要，不冒称重验原始输出。仅从 GitHub 恢复不提供服务器登录能力，仍需本会话同等明确授权。
- GitHub 工具最初不可调用、终端 dry-run exit 128；工具随后恢复。发布使用 Git data：树 → 指向该树/当前 head 的 commit → 仅开发分支非强制 ref 更新 → fetch 和 staged tree 一致性校验。不能重置/强推；终端不需要配置或输出秘密。
- 本次没有子智能体。主模型/档位要求 6.1 Sol/High，但缺少可靠回读接口，不声称核验；子智能体仅明确委派时使用 6 Luna/Max，不能未获限定权限并发访问服务器。

## 新会话恢复顺序

1. 从唯一仓库读取 README、AGENTS、Issue #3（含评论）、关联 Draft PR（含 diff/讨论/Checks）、STATUS、HANDOFF、M0_BASELINE、M0_1_INVENTORY。必要时核对 PR #2 的已合并/独立复审证据。
2. 先 `git status --short --branch`、`git remote -v`；非干净则保留并调查，不 reset/覆盖。只克隆本仓库，不接触旧项目。
3. `git fetch origin main` 并获取 `codex/m0-1-inventory`；核对 PR base/head 与 main。干净工作区可跟踪分支后 `git pull --ff-only`；若远端出现新提交或 PR 已变更，核实差异再继续，不覆盖历史。
4. `git rev-parse HEAD` / `git log -3 --oneline`；按 PR 精确 SHA/CI 和八条摘要复核。公开摘要不是原始日志；训练层 UNKNOWN/失败不能变成 PASS。
5. 当前只允许修复 M0-1 审核指出的问题或按既有边界补证。新任务来源、管理员权限或后续阶段授权不明确时停在门禁并记录 BLOCKED/NOT_RUN。ChatGPT 独立审核与用户批准前，不开始 M0-2/M0-3/M1。

## 三类角色的上下文检查点

- **ChatGPT**：从该窗口第一个用户问题计，每 5 个必须交接；上下文提前过长则提前。给出可复制说明并核实 GitHub 已保存，不能声称自动开窗。本仓库不知道外部 ChatGPT 窗口计数，Codex 聊天轮数不能替代。
- **Codex 主智能体（要求 6.1 Sol/High）**：每个小任务更新状态；约 2/3 上下文、压缩前或决定难追溯时，先写 STATUS/HANDOFF、提交并推送安全工作，再汇总 PR/commit/测试/阻塞。不能仅靠自动压缩保存进度；未完成工作不得标完成。本次检查点：计划→A/B 平台→软件/失败诊断→八条证据整理→发布/CI。
- **Codex 子智能体（要求 6 Luna/Max）**：仅明确委派，限定输入、可改范围、DoD、证据及访问边界；不改共享最终 STATUS/HANDOFF、不直接合并。接近限制先交回安全改动/提交、失败/风险/未完成项与恢复点，由主智能体整合推送。配置不可用记录阻塞，不擅自替换。
- 推送失败须保存本地 commit、症状与重试方式，明确 GitHub 尚不可恢复未推送内容；不虚报完成。完整协议见 [AGENTS](../AGENTS.md)。

## 可复制到 ChatGPT 新窗口

```text
唯一仓库：https://github.com/Zwhao0/20261015
当前任务：https://github.com/Zwhao0/20261015/issues/3；只审核 M0-1。
请从 GitHub 读取 README、AGENTS、docs/STATUS、docs/HANDOFF、docs/M0_BASELINE、docs/M0_1_INVENTORY 和关联 Draft PR。
分支：codex/m0-1-inventory；base 起点 main 41a30e011b3fb0074aaef7cb8c42070aef4562b1。
PR URL / 最新 head SHA / CI run/job：从该分支 Draft PR 描述与 Checks 核实，不猜测。
已完成：A/B 各四次真实只读平台/元数据调查、八条脱敏证据与摘要哈希、命令/失败记录。
未完成：容器访问 BLOCKED；训练版本/任务来源/Rank/信号配置和详细同步误差 UNKNOWN；GPU/训练/API/故障注入测试 NOT_RUN。
验证：核对精确 head 的文档检查、哈希/敏感审查及 CI；不能用旧 HEAD 的 PASS 替代。
私密原始证据只在授权本机，公开逻辑 LOCAL/<ID> 无登录信息；无原始材料不得冒称重验。
请独立审核，用户批准前不得推进 M0-2/M0-3/M1；M0-Gate 仍 INCONCLUSIVE。
ChatGPT 窗口计数：由旧 ChatGPT 窗口填写；新窗口从自己的首个用户问题重新计数。
```

## 阻塞报告模板

```text
编号 / 阶段 / 日期：
原始症状与脱敏日志位置（原始敏感证据仅存授权位置）：
已尝试动作 / 命令 / 退出码 / PASS-FAIL-NOT_RUN-INCONCLUSIVE：
已保存 branch / commit / PR / 未推送内容：
影响范围与仍可完成的安全工作：
候选方案及依据、风险：
恢复步骤 / 重试条件 / 需要的授权或信息：
```
