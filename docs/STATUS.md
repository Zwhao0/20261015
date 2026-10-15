# 项目状态

更新：2026-10-15（Asia/Shanghai）。当前 [Issue #6：M0-2](https://github.com/Zwhao0/20261015/issues/6)，母 [Issue #1](https://github.com/Zwhao0/20261015/issues/1)。用户明确指令“启动 M0-2”；历史文档的未授权状态已被本轮指令取代。

## 阶段与当前交付

| 项目 | 状态 | 事实与边界 |
| --- | --- | --- |
| M0-0 | PASS，已合并 | PR #2，历史 main 41a30e0… |
| M0-1 首轮 | 文档审核 PASS，已合并 PR #4 | 历史 main `4ae0555c6fca24a6082e8e6af4ac40f107cb6716` |
| M0-1 容器补证 | 限环境调查交付审核 PASS；训练/信号 INCONCLUSIVE | [PR #5 审核](https://github.com/Zwhao0/20261015/pull/5#issuecomment-6188441126)，精确 head f15050dc1c4b8bf5cd5e49d75576f19ecf7b269d；启动时 Open/Ready/Unmerged；发布前GitHub已合并为main `4d93a08d76a10ff9a52fba68b84cba2d5fc6475a`，本轮未操作合并 |
| M0-2 | 离线矩阵材料完成，待独立审核 | [9行矩阵](M0_2_CAPABILITIES.md)、A/B证据、官方版本来源、V1～V7条件与失败降级；不声明真实信号可用 |
| M0-2 现场验证 | NOT_RUN | 未再次 SSH/读凭据/读metrics或私有日志/查询RAS/触发FR/GPU/训练/collective；完整兼容性 INCONCLUSIVE |
| M0-3 / M1～M5 | NOT_RUN | 未授权，本轮不选切片/不实现监控或检测、不故障注入 |
| M0-Gate | INCONCLUSIVE | M0-2 独立审核、后续材料与最终批准尚缺 |

- 分支 `codex/m0-2-capability-matrix` 先从4ae0555…建立，发布前fetch发现PR #5已合并，保存草稿后快进到main `4d93a08d76a10ff9a52fba68b84cba2d5fc6475a`；不改旧分支、不操作GitHub合并。当前 Draft PR 由该分支关联，最终 head/tree/CI 在 PR 描述保存；仅五份文档改动，工程检查器/CI/AGENTS/原调查证据不变。
- 最新main已包含完整18条证据，原始分析输入仍固定为 [PR #5 固定快照](https://github.com/Zwhao0/20261015/blob/f15050dc1c4b8bf5cd5e49d75576f19ecf7b269d/docs/M0_1_INVENTORY.md) 的18条；本分支同名本地文件随main快进同步，原8条及新增10条未改。GitHub可恢复公开输入，不提供主机登录或私密原始证据。
- A/B 各自版本调查：Torch 2.13.0+cu130、Toolkit 13.0.88；NCCL 包/header 2.30.7、Torch编译API 2.29.7、探查进程库2.30.7。上游编译宏解释支持两种查询可不同，不证明本地ABI/collective兼容。
- 直接可得仅限历史主机设备/瞬时PID-GPU字段、时钟API语义；完整Job/Run/Rank身份、跨机精度、真实进度、metrics/日志来源、RAS/FR现场配置/输出仍UNKNOWN。RAS/FR有对应版本支持路径，需配置/本地构建核实；没有证据判完整能力“不可得”。

## 验证记录

本地 macOS / Python 3.9.6，验证对象为本分支待提交的五份文档；最终提交用相同 tree 绑定，精确SHA和CI由PR记录。

| 检查 | 结果 | 命令 / 退出码 / 证据 |
| --- | --- | --- |
| 仓库、main、Issue、前序审核 | PASS | `git status --short --branch`、`git fetch origin`、`git rev-parse origin/main` exit 0；GitHub Issue #1/#3、PR #5 metadata/审核 API；新任务 Issue #6 |
| 官方版本资料 | PASS（离线来源核对） | 矩阵 S1～S9；NCCL 2.30.7归档、PyTorch v2.13.0源码、exporter 4.8.4 release；工具查询无 shell 退出码，部分候选URL失败另列，不算功能测试 |
| 本地文档/diff | PASS，exit 0 | `python3 scripts/check_docs.py` → 5份必需文档/12文本文件；`git diff --check`；最终staged diff同样检查 |
| 18条公开摘要/原8条不变 | PASS，exit 0 | `python3` 标准库复核（矩阵内可复跑代码）：18个唯一ID/规范JSON SHA-256匹配，与历史4ae0555…原8条的JSON文本/哈希逐字一致，最新main18条与f15050d输入逐字一致；不读取私密原始材料 |
| 敏感信息/范围 | PASS，exit 0 + 人工审查 | 标准库扫描五份全文的IPv4/真实GPU UUID/私钥头/常见token和password赋值/本机用户路径/SSH身份模式无匹配；仅五份文档，AGENTS/CI/检查器/旧证据未改；扫描覆盖有限，不读取凭据 |
| 当前HEAD CI | INCONCLUSIVE（写入时） | 发布后核对本次 PR Checks 的 run/job/log；旧PR的PASS不能替代，精确链接保存PR描述 |
| 真实信号/GPU/双机验证 | NOT_RUN | 没有本轮主机命令/现场退出码/新原始日志；不将文档检查冒充功能验收 |

## 阻塞、失败与恢复

- B-Workload / B-Signals / B-Time：无已确认可读本项目任务、launcher/Rank/进度来源、metrics/RAS/FR信号与时钟误差界，继续 UNKNOWN。补证条件 V1～V6 见矩阵，不自行读取未知归属任务。
- B-Runtime：C1只完成版本/CPU导入，通用运行时来源待环境所有者确认，确认前不作为开发/测试环境。GPU/双机验证为V7后续独立授权项，不为消除NCCL差异换库。
- B-Predecessor（已解除）：发布前发现PR #5已合并；草稿以命名stash和本机公开文档备份保留后快进最新main，整合M0-2入口。固定SHA仍保留用于可复现；无远端强推/合并。
- F-Docs：初次NCCL RAS路径错误/PyTorch 2.13文档页与部分候选路径工具访问失败；改查NCCL2.30.7正确归档路径和PyTorch v2.13.0官方源码成功。失败仅表示本次工具未取得资料，不证明HTTP404或功能缺失，详见矩阵。
- F-Local-M0-2（已恢复）：一次文档辅助命令的嵌套heredoc结束符相同，zsh解析报unmatched backtick/exit 1，整段未执行；改用apply_patch和不同结束符后成功，不涉及服务器。
- 历史失败不抹去：Docker权限、Chrony506、dpkg混合非零、B05认证、A05截断/本地IndexError、08 mount模板、终端推送凭据/upstream refspec/本地编码诊断，均保留在[首轮记录](M0_1_INVENTORY.md)、PR #4/#5与固定18条证据快照。容器版本访问后来已获准成功，时间/训练信号缺口仍在。
- 用户取消清理继续有效：删除/停止/重启/新建容器、镜像/卷删除为0；本轮没有服务器配置变更需回滚。文档可经审查revert/后续修复，不覆盖失败历史。
- 主智能体要求6.1 Sol/High，无可靠模型/档位回读，不声称已核验/切换；本轮未委派子智能体。上下文检查点、发布恢复与独立审核入口见[HANDOFF](HANDOFF.md)。
