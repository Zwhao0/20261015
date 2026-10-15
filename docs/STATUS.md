# 项目状态

更新：2026-10-15（Asia/Shanghai）。任务依据：[Issue #1](https://github.com/Zwhao0/20261015/issues/1)。

当前授权：仅修复 [ChatGPT 审核评论](https://github.com/Zwhao0/20261015/pull/2#issuecomment-6187217983) 指出的 AGENTS 生命周期规则，并更新状态/交接、验证与发布。唯一必修项已修复，待 ChatGPT 复审；PR #2 保持 Draft，不合并、不进入 M0-1；不连接 H800、不读取连接凭据、不开发 Detector/复杂算法、不进行故障注入。

## 阶段与范围

| 项目 | 状态 | 说明 |
| --- | --- | --- |
| M0-0 | 已修复，待复审 | AGENTS 两条临时限制已改为通用授权规则，仅同步 STATUS/HANDOFF；尚未批准合并 |
| M0-1 | NOT_RUN | 环境事实调查，需单独明确授权 |
| M0-2 | NOT_RUN | 观测能力/兼容性核查；仅建立空表 |
| M0-3 | NOT_RUN | 首个端到端切片与验收方案；仅建立待填项 |
| M0-Gate | INCONCLUSIVE | 尚无环境/训练证据，ChatGPT 未审核、用户未批准 |
| M1～M5 | NOT_RUN | 不在本次范围；路线见 README |

## 恢复锚点

- 初始 main：`6e80e6ce88ca952d3fbe3f0612b36058e8bd337e`，仅 README，单个提交。
- 开发分支：`codex/m0-0-bootstrap`；[Draft PR #2](https://github.com/Zwhao0/20261015/pull/2)，base 为 main。
- 当前 HEAD 以 GitHub PR 的 head SHA 为准；文档不嵌入自身 commit 的 SHA。恢复步骤见 [HANDOFF](HANDOFF.md)。
- 模型配置：用户指定主智能体 6.1 Sol/High、子智能体 6 Luna/Max；本会话无可靠模型/推理档位回读接口，未声称已核验实际配置；未启动子智能体。

## 验证与证据

| 检查 | 结果 | 证据/限制 |
| --- | --- | --- |
| main/来源核对 | PASS | `git log`、`git ls-tree`、`git remote -v`；仅克隆指定项目 |
| 本地文档检查 | PASS | macOS / Python 3.9.6；`python3 scripts/check_docs.py`，exit 0，5 份必需文档、10 个文本文件 |
| 检查器正反例抽查 | PASS | 临时 Git 夹具：正常文档通过；断链、行末空格、冲突标记、缺少必需文档均被拒绝；exit 0 |
| 空白与 diff 审查 | PASS | `git diff --cached --check`、`git diff main...HEAD --check`，exit 0；已人工审查范围、链接与敏感信息 |
| 首轮 GitHub CI | PASS | `bad23bfe5ae62d79e7495592429a5f8e30e0b915`；[run 38700465193](https://github.com/Zwhao0/20261015/actions/runs/38700465193)，docs job success，输出 5 份必需文档、10 个文本文件 |
| 前次交付的 CI | PASS | 审核基线 `bc560436388f7bb96864680ad64242552fb26a07`；[run 38700717006](https://github.com/Zwhao0/20261015/actions/runs/38700717006) success |
| 本次修复的 CI | INCONCLUSIVE（写入时） | 本地文档与 diff 检查已通过；发布后核实对应新 HEAD 的 CI，精确 SHA、运行链接及结果记录于 [PR 描述与 Checks](https://github.com/Zwhao0/20261015/pull/2/checks)，旧结果不替代新提交验证 |
| H800/训练/GPU/检测器验证 | NOT_RUN | 本次未授权、不执行；不能从文档检查推断通过 |

## 阻塞与下一步

- B1（已绕过）：`GIT_TERMINAL_PROMPT=0 git push --dry-run origin HEAD`，exit 128，`could not read Username`；终端无推送凭据。已用连接的 GitHub Git data 接口发布同一分支，再 fetch/fast-forward；首轮本地/远端 tree 均为 `afce283f50ce392c03de8e1072582b177483467d`。后续发布可复用此路径，不需要服务器凭据。
- F1（已恢复）：反例抽查首轮夹具在正常样例断言失败（exit 1）；macOS 临时路径 `/var` 与解析后的 `/private/var` 不一致。夹具根路径改用 `Path.resolve()` 后正常及四项反例全部通过，产品检查器无需修改。
- F2（已恢复）：single-branch clone 初次设置 upstream 失败；为开发分支增加 fetch refspec 后恢复跟踪，无历史覆盖。首轮 CI 的 Node 20 弃用警告通过改用固定 SHA 的官方 checkout v7.0.1 处理，最终 CI 见 PR。
- 环境与观测事实均为 `UNKNOWN`，不是调查结论。
- 无待用户处理的实施阻塞。等待 ChatGPT 对唯一必修项复审；模型档位未独立核验、项目许可证未指定，均已明确记录。
- M0-0 审核不等于 M0-Gate 通过；后续 M0 工作需另行授权。阻塞报告模板见 HANDOFF。
