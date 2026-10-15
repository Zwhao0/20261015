# Distributed Training Observability & Diagnostics

An engineering project for **Training Observability** and **Detection, Localization & Diagnosis** in distributed AI training.

## Project status
- **Phase:** M0-1 — read-only environment inventory; independent review pending.
- **Canonical repository:** https://github.com/Zwhao0/20261015
- **Current task and acceptance criteria:** https://github.com/Zwhao0/20261015/issues/3 (parent: https://github.com/Zwhao0/20261015/issues/1)
- **Implementation:** Codex, through small reviewed pull requests.
- **Planning and independent review:** ChatGPT and project owner.

## Roadmap
M0 Technical baseline → M1 Observability → M2 Fail-Stop → M3 Hang → M4 Fail-Slow → M5 Evidence-based Diagnosis & Delivery.

**No claims of functionality or GPU validation are made by this initial commit.**

## Working rules
GitHub issues, pull requests and checked-in state/handoff docs are the source of truth. Record evidence and failures; do not restart from scratch on blockers. Explicit approval is required for disruptive cluster actions, dependency/driver upgrades, merges and destructive Git operations. Do not commit secrets or private training logs.

See [M0 Issue #1](https://github.com/Zwhao0/20261015/issues/1) for the session handoff protocol (including ChatGPT's five-question window limit and Codex main/subagent context checkpoints), initial Codex task and M0 exit criteria.

## M0 工程入口

M0-0 已独立审核并合并 PR #2；本次仅执行 M0-1。A/B 平台与容器版本已采集，现有 PyTorch 可导入；真实训练/信号仍有 UNKNOWN，容器补证待独立审核；M0-2/M0-3/M1 未执行、未授权，M0-Gate 仍 INCONCLUSIVE。

- [AGENTS.md](AGENTS.md)：执行边界、角色、上下文与工程规范。
- [STATUS](docs/STATUS.md)：阶段、验证、阻塞和下一步。
- [HANDOFF](docs/HANDOFF.md)：从 GitHub 恢复会话及交接模板。
- [M0 技术基线](docs/M0_BASELINE.md)：事实、证据、能力矩阵与后续验收骨架。
- [M0-1 只读调查](docs/M0_1_INVENTORY.md)：授权、命令、A/B 独立证据、摘要哈希与未验证项。

在仓库根目录运行（Git、Python 3.9+，无第三方 Python 依赖）：

```sh
python3 scripts/check_docs.py
git diff --check
```

CI 在开发分支 push 和面向 main 的 PR 上执行文档检查；只验证仓库工程质量，不代表训练、GPU 或检测能力通过验收。
