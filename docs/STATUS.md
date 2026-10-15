# 项目状态

更新：2026-10-15（Asia/Shanghai）。任务依据：[Issue #1](https://github.com/Zwhao0/20261015/issues/1)。

## 阶段与范围

| 项目 | 状态 | 说明 |
| --- | --- | --- |
| M0-0 | 实施中 | 文档、交接协议和轻量检查；提交 Draft PR 后待独立审核 |
| M0-1 | NOT_RUN | 环境事实调查，需单独明确授权 |
| M0-2 | NOT_RUN | 观测能力/兼容性核查；仅建立空表 |
| M0-3 | NOT_RUN | 首个端到端切片与验收方案；仅建立待填项 |
| M0-Gate | INCONCLUSIVE | 尚无环境/训练证据，ChatGPT 未审核、用户未批准 |
| M1～M5 | NOT_RUN | 不在本次范围；路线见 README |

## 恢复锚点

- 初始 main：`6e80e6ce88ca952d3fbe3f0612b36058e8bd337e`，仅 README，单个提交。
- 开发分支：`codex/m0-0-bootstrap`；PR：尚未创建。
- 当前 HEAD 以 GitHub PR 的 head SHA 为准；文档不嵌入自身 commit 的 SHA。恢复步骤见 [HANDOFF](HANDOFF.md)。
- 模型配置：用户指定主智能体 6.1 Sol/High、子智能体 6 Luna/Max；本会话无可靠模型/推理档位回读接口，未声称已核验实际配置；未启动子智能体。

## 验证与证据

| 检查 | 结果 | 证据/限制 |
| --- | --- | --- |
| main/来源核对 | PASS | `git log`、`git ls-tree`、`git remote -v`；仅克隆指定项目 |
| 本地文档检查 | PASS | macOS / Python 3.9.6；`python3 scripts/check_docs.py`，exit 0，5 份必需文档、10 个文本文件 |
| 检查器正反例抽查 | PASS | 临时 Git 夹具：正常文档通过；断链、行末空格、冲突标记、缺少必需文档均被拒绝；exit 0 |
| 空白与 diff 审查 | PASS | `git diff --check`，exit 0；已人工审查范围、链接与敏感信息；提交前复核暂存区 |
| GitHub CI | NOT_RUN | 推送并建 PR 后记录运行链接与提交 |
| H800/训练/GPU/检测器验证 | NOT_RUN | 本次未授权、不执行；不能从文档检查推断通过 |

## 阻塞与下一步

- B1（恢复中）：`GIT_TERMINAL_PROMPT=0 git push --dry-run origin HEAD`，exit 128，`could not read Username`；终端未配置推送凭据。使用已连接 GitHub 接口发布同一分支，再 fetch 核对 tree/HEAD；不索取或提交密钥。最终结果记录于 PR。
- F1（已恢复）：反例抽查首轮夹具在正常样例断言失败（exit 1）；macOS 临时路径 `/var` 与解析后的 `/private/var` 不一致。夹具根路径改用 `Path.resolve()` 后正常及四项反例全部通过，产品检查器无需修改。
- 环境与观测事实均为 `UNKNOWN`，不是调查结论。
- 完成本地验证、推送开发分支、建立 Draft PR，补充 PR/CI 证据后交 ChatGPT 审核 M0-0。
- M0-0 审核不等于 M0-Gate 通过；后续 M0 工作需另行授权。阻塞报告模板见 HANDOFF。
