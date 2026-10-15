# Distributed Training Observability & Diagnostics

An engineering project for **Training Observability** and **Detection, Localization & Diagnosis** in distributed AI training.

## Project status
- **Phase:** M0-Gate — approved for the design and engineering baseline; M1 execution not authorized.
- **Canonical repository:** https://github.com/Zwhao0/20261015
- **Current task and acceptance criteria:** https://github.com/Zwhao0/20261015/issues/1 (M0-Gate formal review record)
- **Implementation:** Codex, through small reviewed pull requests.
- **Planning and independent review:** ChatGPT and project owner.

## Roadmap
M0 Technical baseline → M1 Observability → M2 Fail-Stop → M3 Hang → M4 Fail-Slow → M5 Evidence-based Diagnosis & Delivery.

**No claims of functionality or GPU validation are made by this initial commit.**

## Working rules
GitHub issues, pull requests and checked-in state/handoff docs are the source of truth. Record evidence and failures; do not restart from scratch on blockers. Explicit approval is required for disruptive cluster actions, dependency/driver upgrades, merges and destructive Git operations. Do not commit secrets or private training logs.

See [M0 Issue #1](https://github.com/Zwhao0/20261015/issues/1) for the session handoff protocol (including ChatGPT's five-question window limit and Codex main/subagent context checkpoints), initial Codex task and M0 exit criteria.

## M0 工程入口

用户于 2026-10-15 明确授权“启动：Issue #1 — M0-Gate 正式审核记录”。[PR #9](https://github.com/Zwhao0/20261015/pull/9) 已获[设计修正独立复审 PASS](https://github.com/Zwhao0/20261015/pull/9#issuecomment-6189756035)并合并，审核基线 main 为 `42bce13c5bd925c74856f96de64f431526d142bf`。[M0-Gate 独立技术审查](https://github.com/Zwhao0/20261015/issues/1#issuecomment-6189883744)判定离线设计及 M1-C1 离线编码技术准备 PASS；真实环境接入与低开销 INCONCLUSIVE；整体 Gate 现为 PASS（限工程基线/离线调查、矩阵、V0.1设计及M1-C1离线编码技术准备），依据2026-10-15的[用户最终批准记录](https://github.com/Zwhao0/20261015/issues/1#issuecomment-6190108253)及[PR #10修正要求](https://github.com/Zwhao0/20261015/pull/10#issuecomment-6190117664)；真实接入/兼容/开销仍INCONCLUSIVE，M1执行未授权。正式结论与证据见[审核记录](docs/M0_GATE.md)。历史上“批准执行M0-GATE”仅作为记录执行授权登记；后续ChatGPT对话已单独取得最终Gate批准，现同步该事实。本轮仅同步文档和审核事实；T01～T14功能回放、CPU子进程、I0～I5、collective及资源测量均NOT_RUN。

- [AGENTS.md](AGENTS.md)：执行边界、角色、上下文与工程规范。
- [STATUS](docs/STATUS.md)：阶段、验证、阻塞和下一步。
- [HANDOFF](docs/HANDOFF.md)：从 GitHub 恢复会话及交接模板。
- [M0-Gate 正式审核记录](docs/M0_GATE.md)：审核对象、证据、分层结论、剩余门禁及用户批准栏。
- [M0 技术基线](docs/M0_BASELINE.md)：事实、证据、能力矩阵与后续验收骨架。
- [M0-1 只读调查与容器补证](docs/M0_1_INVENTORY.md)：main 已合并的18条证据、命令、摘要哈希与未验证项。
- [M0-2 能力与兼容性矩阵](docs/M0_2_CAPABILITIES.md)：能力分类、A/B 证据、版本条件、失败降级与后续补证门禁。
- [M0-3 切片与验收方案](docs/M0_3_SLICE.md)：V0.1范围、真实来源门禁、契约、14类回放用例、双机路径、预算、回退与M1候选。

在仓库根目录运行（Git、Python 3.9+，无第三方 Python 依赖）：

```sh
python3 scripts/check_docs.py
git diff --check
```

CI 在开发分支 push 和面向 main 的 PR 上执行文档检查；只验证仓库工程质量，不代表训练、GPU 或检测能力通过验收。
