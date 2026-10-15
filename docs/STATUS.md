# 项目状态

更新：2026-10-15（Asia/Shanghai）。当前任务：[Issue #3](https://github.com/Zwhao0/20261015/issues/3)，母 [Issue #1](https://github.com/Zwhao0/20261015/issues/1)。

当前授权仅 M0-1：用户明确允许读取指定的仓库外服务器信息文件并访问两台服务器；实际操作限定只读、低侵入，不使用变更权限。已完成 A/B 独立平台与宿主机元数据调查，训练层仍有 UNKNOWN/访问阻塞，等待 ChatGPT 独立审核。M0-2/M0-3/M1 未授权；不合并、不故障注入、不实现采集/检测器。

## 阶段与范围

| 项目 | 状态 | 事实与门禁 |
| --- | --- | --- |
| M0-0 | PASS，已合并 | [第二轮独立审核](https://github.com/Zwhao0/20261015/pull/2#issuecomment-6187338743)；PR #2 已于 2026-10-15 合并，main=41a30e0… |
| M0-1 | 已采集，待独立审核；训练层 INCONCLUSIVE | 两台均真实连接；各 8×H800、Driver 580.178.04、Ubuntu 24.04；内核不同。容器访问 BLOCKED，训练版本/任务来源/实际信号仍 UNKNOWN，不能给全量 PASS |
| M0-2 / M0-3 | NOT_RUN | 当前未授权，矩阵与切片骨架未填充为结论 |
| M0-Gate | INCONCLUSIVE | 未完成全部 M0 材料、独立审核及用户最终批准 |
| M1～M5 | NOT_RUN | 不在本次范围 |

## 恢复锚点与当前交付

- 最新 main 起点：`41a30e011b3fb0074aaef7cb8c42070aef4562b1`；开始工作前 fetch 并核对，和用户提供锚点一致。原始 main `6e80e6c…` 仅为 M0-0 历史。
- 分支：`codex/m0-1-inventory` → main。Draft PR 发布进行中；精确 head、tree、最终 CI 以该分支关联 PR 描述为准，尚未合并。
- [基线事实表](M0_BASELINE.md)、[M0-1 调查与证据](M0_1_INVENTORY.md)、[恢复交接](HANDOFF.md)。采集窗口 2026-10-15 16:08:10～16:12:18 UTC+08:00；8 条实际证据、完整命令、子命令退出码与公开摘要哈希已保存。
- 模型要求为主智能体 6.1 Sol/High、子智能体 6 Luna/Max；本会话没有可靠的实际模型/推理档位回读接口，不声称核验或切换成功。本次未启动子智能体，保留条件委派/回报协议。

## 验证与边界

| 检查 | 结果 | 环境、内容、退出码与证据 |
| --- | --- | --- |
| main / Issue / PR #2 核对 | PASS | git fetch、rev-parse；GitHub API 的 Issue #3、PR #2 merged/merge SHA、独立复审评论；只使用唯一仓库 |
| A/B 平台只读采集 | PASS（仅字段获取） | 各自 E-A-01/E-B-01，真实 SSH exit 0；GPU 查询、OS/kernel、Python 与时间报告 exit 0；container 检测 exit 1/none 单列解释 |
| A/B 软件/来源元数据 | INCONCLUSIVE（训练层） | 各自 02/03/04，SSH exit 0；包、进程类别与 API 时钟事实已获取；Docker/Chrony/dpkg 混合查询失败保留，不能按 SSH exit 0 记全通过 |
| 本地文档 / diff | PASS，exit 0 | macOS / Python 3.9.6；`python3 scripts/check_docs.py`：5 份必需文档、11 个文本文件；`git diff --check`；对本次五份文档内容执行并人工审查范围/链接 |
| 摘要哈希 / 敏感信息 | PASS，exit 0 | 标准库核对八条 ID、规范 JSON 摘要哈希与受控副本；五份公开文档的指定敏感值/常见身份与密钥模式扫描通过，人工检查通过。不是通用秘密检测器或服务器功能测试 |
| 对应新 HEAD GitHub CI | INCONCLUSIVE（尚未发布） | 不继承 PR #2 的 PASS；新提交发布后核验 head 关联 run、job 与日志，精确链接/结果写 Draft PR |
| GPU 计算 / 训练 / 映射集成 / RAS / Flight Recorder / 故障注入 | NOT_RUN | 本次不创建负载、不初始化 CUDA、不调用进程内 API、不跑 profiler，不读取任务私有数据，不能从文档检查推断通过 |

## 失败、阻塞与下一步

- **B-Container（持续）**：A/B 当前账户 `docker ps` exit 1，permission denied（03）；未提权/改权限。容器 Python/Torch/CUDA/NCCL/框架版本 UNKNOWN。恢复需管理员提供批准容器的脱敏版本元数据或既有只读访问方式。
- **B-Workload（持续）**：04 各有 8 行 PID/GPU 关联，但归属与任务类型未确认；没有读取获准本项目训练入口/日志，Job/Run/Rank/Local Rank UNKNOWN。后续需明确可读任务及字段，不碰旧项目/第三方数据；不启动训练补证。
- **F-Time（保留）**：A/B chronyc tracking exit 1，`506 Cannot talk to daemon`；timedatectl 报告同步但详细偏差未知，未修改时钟/服务。
- **F-Package（已界定）**：混合模式 dpkg 查询 exit 1，不等于全部包缺失；03 DCGM 单包查询 exit 0。02 仅保留 stderr 存在标记；03 是另一次诊断复采，未虚构原始 stderr。
- **B-Publish（连接已恢复）**：初次 GitHub 工具不可调用；终端 dry-run exit 128（缺少 GitHub 凭据）。连接恢复后以 Git data 接口非强制发布同树，计划 fetch/一致性核对；终端无凭据不需用户提供秘密。
- **F-Local（已恢复）**：本地临时文档辅助脚本直接执行两次报 source 非 UTF-8（exit 1）；文件 UTF-8 严格解码、tokenize/compile 均通过，显式 UTF-8 读取并 compile/exec 后生成成功（exit 0）。未查明解释器直接读文件差异原因；辅助脚本不进仓库，不改产品代码，后续文档检查通过。
- 历史 M0-0 的临时夹具路径失败、single-branch upstream 恢复与 CI 变更证据保留在 [PR #2](https://github.com/Zwhao0/20261015/pull/2)，不作为本次调查验证。
- 当前可安全交付证据与明确缺口；ChatGPT 独立审核前不推进后续阶段。项目自身许可证仍未指定。阻塞恢复模板及上下文检查点见 HANDOFF。
