# 项目状态

更新：2026-10-15（Asia/Shanghai）。当前 [Issue #3](https://github.com/Zwhao0/20261015/issues/3)，母 Issue #1。

仅 M0-1。用户已新增授权现有容器访问与已提供凭据的 sudo 认证，优先复用已有 PyTorch；本轮完成两台当前运行 C1 的只读版本/CPU 导入补证，没有修改权限或训练环境。用户最新明确取消清理：**容器删除/停止/重启/新建均为 0**。已有可复用候选，未下载/上传/构建环境。M0-2/M0-3/M1 未授权。

## 阶段与恢复锚点

| 项目 | 状态 | 证据与边界 |
| --- | --- | --- |
| M0-0 | PASS，已合并 | PR #2，main 41a30e011b3fb0074aaef7cb8c42070aef4562b1 |
| M0-1 首轮快照 | 文档交付审核 PASS；训练环境 INCONCLUSIVE | [PR #4 审核](https://github.com/Zwhao0/20261015/pull/4#issuecomment-6187891676)，仅覆盖 1dced3b… 的原 8 条摘要 |
| M0-1 容器补证 | 版本/CPU 导入 PASS；训练/信号仍 INCONCLUSIVE，待审核 | A/B 各 07/08/09：Torch 2.13.0+cu130、Toolkit 13.0.88；NCCL API 2.29.7 与已加载库 2.30.7 分开；真实 GPU/训练 NOT_RUN |
| M0-2 / M0-3 / M1～M5 | NOT_RUN | 未执行、未授权 |
| M0-Gate | INCONCLUSIVE | 缺少后续材料与最终审核/批准 |

- 唯一仓库：[Zwhao0/20261015](https://github.com/Zwhao0/20261015)。最新 main = `4ae0555c6fca24a6082e8e6af4ac40f107cb6716`（合并 PR #4）；M0-1 初始起点仍是历史 `41a30e0…`。最新 main 的 tree 与原 `1dced3b…` 快照相同，已核验。
- 原 PR #4/head `1dced3bdbbdf8a091c9bfde74fede838c56406c8` 保留，初读为 Ready/Open，后续 fetch/API 核实已合并为上述 main。尝试恢复 Draft 返回 GraphQL FORBIDDEN；不能据此推断对开放 PR 的通用权限。未改旧分支、未自行合并。
- 当前分支 `codex/m0-1-container-inventory` → 最新 main，[Draft PR #5](https://github.com/Zwhao0/20261015/pull/5) 已发布，保持 Draft/Open/Unmerged。首个补证提交 `7ee7cc57c99e1af97e7d01eea7dc427975e72ea2`；交接提交整合最新 main 的父关系并更新入口，精确最新 head/tree/CI 写 PR 描述；不混用旧审核。
- [完整事实表](M0_BASELINE.md)、[调查/18条证据/命令/哈希](M0_1_INVENTORY.md)、[恢复交接](HANDOFF.md)。首轮 16:08:10～16:12:18；容器补证 16:36:01～16:42:26，均 2026-10-15 UTC+08:00。
- 主智能体要求 6.1 Sol/High、子智能体 6 Luna/Max；无可靠模型/档位回读接口，未声称核验或切换。本轮未启动子智能体，保留条件委派/回报协议。

## 验证与失败

| 检查 | 结果 | 命令/环境/退出码/证据 |
| --- | --- | --- |
| main/旧 PR/审核核对 | PASS | git fetch、rev-parse、GitHub PR #4/评论/Issue #3；旧 HEAD 未变 |
| A/B 既有 sudo/Docker 版本访问 | PASS（各自后续成功） | 06/07，exit 0；B05 sudo exit 1 保留，非全程无失败；不改权限 |
| 容器版本与 CPU 导入 | PASS（限定作用域） | 各 07/08/09；python -I -S -B，隐藏 GPU、限制线程、禁字节码；导入/版本查询 exit 0、CUDA 初始化标记 false |
| 完整 GPU/训练/分布式/观测能力 | NOT_RUN | 不创建训练、进程组、collective、profiler/RAS；不能把导入通过当训练或兼容通过 |
| 本地文档/18条摘要/敏感信息 | PASS，exit 0 | macOS/Python 3.9.6；python3 scripts/check_docs.py（5份必需文档、11文本文件）、git diff --check、公开摘要校验代码及受控副本比较、敏感值/身份模式/人工审查通过；原8条摘要字节与哈希不变 |
| 当前补证 HEAD CI | INCONCLUSIVE（写入时） | 新 HEAD 发布后单独核验 run/job/日志，最终精确 SHA/链接/结果见 [PR #5 描述及 Checks](https://github.com/Zwhao0/20261015/pull/5/checks)；旧 PR #4 的 PASS 不替代本轮 |
| 清理操作 | NOT_RUN / 用户取消 | 只有预备元数据读取，无 rm/prune/stop/restart/镜像或卷删除；没有清理后状态或磁盘回收量可声称 |

- **B-Container 已解除（系统/第三方版本查询）**：新增明确授权使用现有 sudo；没有配置新权限。B05 首次认证失败后，以已提供登录账户凭据查询成功；不枚举未知密码。
- **B-Workload / B-Signals 持续**：真实任务归属/launcher、Job/Run/Rank、训练进程已加载库、日志/metrics/RAS/FR 配置与信号 UNKNOWN。当前 C1 版本不是任何正在运行训练任务的完整证明。
- **V-NCCL（事实差异）**：包/header 2.30.7、Torch NCCL API 2.29.7、本次导入进程 ncclGetVersion=23007（2.30.7）；兼容性 INCONCLUSIVE，不修改库来消除差异。
- **F-ContainerList**：A05 容器列表输出 16 KiB 截断，前缀不是全量统计；06 单独状态聚合成功。本地前缀展示曾 IndexError/exit 1，过滤不完整行后恢复；原始数据未改。
- **F-MountTemplate**：A/B08 的 .Mounts.Name 对 bind mount 缺键，exit 1；09 仅读 Type 后 exit 0。volume 对象数0不代表没有 bind mount 数据，且用户已取消清理。
- **F-Draft（已界定）**：旧 PR 的 Draft 转换返回 FORBIDDEN，后来核实 #4 已合并；没有反复调用或改旧分支。已新建 PR #5 并确认 draft=true；直接对最新 main，不再需要以旧分支为 base。
- 首轮 Docker 拒绝、Chrony 506、dpkg 混合非零、终端推送凭据缺失、upstream refspec 和本地临时脚本编码诊断失败，均保留在调查记录、原 PR #4 与历史提交；不以本轮成功擦除失败。
- 本轮保留现状，无训练环境部署变更需回滚；原始材料与用户使用入口只在本地受控目录，公开不含身份/凭据。项目许可证仍未指定；待 ChatGPT 审核后由用户决定后续阶段。
