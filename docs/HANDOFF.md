# 可恢复交接

## 当前入口

- 唯一仓库：[Zwhao0/20261015](https://github.com/Zwhao0/20261015)。任务：[Issue #1](https://github.com/Zwhao0/20261015/issues/1)。
- 当前仅 M0-0；开发分支 `codex/m0-0-bootstrap`，[Draft PR #2](https://github.com/Zwhao0/20261015/pull/2) → main；已交付待 ChatGPT 独立审核，未合并。实施与验证快照见 [STATUS](STATUS.md)。
- 从初始 main `6e80e6ce88ca952d3fbe3f0612b36058e8bd337e` 开始，无旧项目继承。未访问 H800；本地 `服务器.md` 保持仓库外且未读取。
- 已完成工程文档、轻量检查、正反例抽查、分支发布与 Draft PR；本地检查及首轮 CI 通过。首轮提交为 `bad23bfe5ae62d79e7495592429a5f8e30e0b915`，后续交接提交的精确 SHA/CI 结果以 PR 最新描述与 Checks 为准。
- 终端无 GitHub 推送凭据，已通过连接的 GitHub Git data 接口发布并核对 tree；后续可沿用创建 tree → 以当前 head 为 parent 创建 commit → 非强制更新开发分支 ref → 本地 fetch/fast-forward 的路径。失败与恢复记录见 STATUS/PR，不需要访问服务器。
- 本次未启动子智能体；主智能体实际模型/档位无可靠回读接口，未声称已核验。剩余事项为独立审核；环境事实与 M0 后续方案见 [基线](M0_BASELINE.md)，均未执行。

## 新会话恢复顺序

1. 只从上述 GitHub 仓库读取 README、AGENTS、Issue #1（含评论）、当前 Draft PR（含 diff、讨论、Checks）、STATUS、HANDOFF、M0_BASELINE。
2. 在已有 checkout 先检查 `git status --short --branch` 和 `git remote -v`；工作区非干净则保留并调查，不 reset、不覆盖。不存在 checkout 时只克隆本仓库。
3. `git fetch origin`，确认当前 PR 的 base/head 与开发分支。干净工作区可切至 `codex/m0-0-bootstrap` 并 `git pull --ff-only`；本地无该分支时跟踪对应远端分支。若 PR 已合并/关闭/换分支，以 GitHub 最新状态为准，记录差异后再推进。
4. 用 `git rev-parse HEAD`、`git log -3 --oneline` 核对 PR head；按 STATUS/PR 复核命令、结果与证据，不能把旧提交的 PASS 套到新提交。
5. 只继续当前获授权的小任务。授权或证据不明时记录 `UNKNOWN` / 阻塞，禁止自动进入 M0-1 或 M1。

## 三类角色的上下文检查点

- **ChatGPT**：从该窗口第一个用户问题计，每 5 个必须输出新窗口交接说明；上下文提前过长则提前。核实 GitHub 状态已保存，交由用户复制到新窗口，不声称能自动开窗。本仓库无法获知外部 ChatGPT 当前计数，恢复者须在自己的窗口维护。
- **Codex 主智能体（6.1 Sol/High）**：每个小任务结束写状态；可见上下文接近约 2/3、压缩前或决策难追溯时，先更新 STATUS/HANDOFF，提交并推送安全工作，汇总 PR、commit、测试、阻塞，再恢复新会话。不把未完成工作标完成；无法精确量化上下文时提前保存。
- **Codex 子智能体（6 Luna/Max）**：明确输入、可改范围、DoD 和证据；不改共享最终状态文件、不直接合并。上下文接近限制前交回主智能体：安全改动/提交、证据、失败、未完成项、恢复步骤；由主智能体整合并推送。配置不可用先报告，不擅自替换。
- 若推送失败，保存 commit 和恢复命令，报告远端缺失；不得声称新会话已能从 GitHub 完整恢复。完整约束见 [AGENTS](../AGENTS.md)。

## 每次交接的最小内容 / 可复制到 ChatGPT 新窗口

```text
唯一仓库：https://github.com/Zwhao0/20261015
任务：https://github.com/Zwhao0/20261015/issues/1；本次只审核/继续 M0-0。
请先从 GitHub 读取 README、AGENTS、docs/STATUS、docs/HANDOFF、docs/M0_BASELINE 和关联 PR。
PR URL / base / branch / HEAD SHA：<从 GitHub 复制，不猜测>
已完成 / 未完成：<分列，注明是否已推送>
验证：<命令、环境、提交、退出码、PASS/FAIL/NOT_RUN/INCONCLUSIVE、证据链接>
关键决定及依据：<基线/PR 的具体位置>
阻塞 / 风险 / UNKNOWN：<事实、影响和恢复路径>
下一步与授权边界：<当前允许的动作；禁止自动进入后续阶段>
ChatGPT 窗口计数：<旧窗口已计数量>；新窗口从自己的首个用户问题重新计数。
请独立审核仓库证据；M0-Gate 仍需 ChatGPT 审核与用户最终批准。
```

## 阻塞报告模板

```text
编号 / 阶段 / 日期：
原始症状与脱敏日志位置（原始敏感证据仅存授权机器）：
已尝试动作 / 命令 / 退出码 / 结果：
已保存 branch / commit / PR / 未推送内容：
影响范围与仍可完成的安全工作：
候选方案及依据、风险：
恢复步骤 / 重试条件 / 需要的授权或信息：
```
