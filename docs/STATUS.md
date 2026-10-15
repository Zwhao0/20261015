# 项目状态

更新：2026-10-15（Asia/Shanghai）。当前 [Issue #8：M0-3](https://github.com/Zwhao0/20261015/issues/8)，母 [Issue #1](https://github.com/Zwhao0/20261015/issues/1)。用户明确指令“启动 M0-3”，取代历史文档的未授权状态。

## 阶段与当前交付

| 项目 | 状态 | 事实与边界 |
| --- | --- | --- |
| M0-0 / M0-1 | 限各次交付审核 PASS，已合并 | PR #2/#4/#5；18条调查证据，训练/真实信号 INCONCLUSIVE |
| M0-2 | 离线矩阵审核 PASS，已合并 PR #7 | [审核](https://github.com/Zwhao0/20261015/pull/7#issuecomment-6189223408)覆盖head `7c9326b61bb539f1c2cf9435d41fb48a403772f4`；merge/main `d36cdacb77b6b1b08392bf27b9b288952918aa98`；本轮Codex未合并 |
| M0-3 | 两项审核修正已写入，待新head复审 | [PR #9 审核](https://github.com/Zwhao0/20261015/pull/9#issuecomment-6189558036)要求区分来源空闲/失活、attempt/run终态；修正[V0.1方案](M0_3_SLICE.md)，仍14类未来回放，无功能实现 |
| M0-3 功能/现场 | NOT_RUN | T01～T14回放、CPU子进程、I0～I5双机、开销未执行；真实任务来源/完整身份/退出样本UNKNOWN |
| M0-Gate | INCONCLUSIVE | 旧head审核要求两项修正；新head独立复审与用户最终批准尚缺，不能进入M1 |
| M1～M5 | NOT_RUN | 未授权；只列M1候选，不创建/启动执行Issue、不实现Detector/故障注入 |

- 分支 `codex/m0-3-slice-acceptance` 从最新main d36cdac…新建；PR由该分支关联的Draft PR确认，最终head/tree/CI写PR描述，避免自引提交。只改README/STATUS/HANDOFF/M0_BASELINE并新增M0_3_SLICE；原调查/矩阵、AGENTS、检查器与CI保持原文。
- 真实来源选择“所有者任务清单+获准局部观测+启动器权威终止记录”，当前尚未落实。裸PID消失不能判退出，单节点launcher退出不外推所有worker或run终态；未明确编码的137不判OOM/SIGKILL。
- A/B历史版本：Torch2.13.0+cu130、Toolkit13.0.88；NCCL包/header2.30.7、Torch编译API2.29.7、探查库2.30.7。差异保留，不换库，不证明collective兼容。C1通用运行时来源待所有者确认，确认前不用于开发/测试。
- 本轮未SSH、读凭据/私密索引/metrics/任务日志、查询RAS/触发FR、运行GPU/训练/collective或更改环境。用户取消清理继续有效；容器删除/停止/重启/新建及镜像/卷删除均0。

## PR 9 审核修正

用户明确要求“根据 PR #9 审核评论完成两项修正”。修正起点/被审head `16a8bee3a1de5f40674d0dc3983862d8a9dc18ad`，main仍为d36cdac…；在原分支追加提交，保留旧head和原检查/失败。当前增量仅M0_3_SLICE、STATUS、HANDOFF三份文档。

- R1：来源合约分PERIODIC/EVENT_DRIVEN/UNKNOWN；15秒freshness只用于约定周期/心跳。事件源数小时无新记录但读取/连续性健康为IDLE，producer活性UNKNOWN；读取错误/丢源/轮转缺口仍UNAVAILABLE/GAP。同步SOURCE_STATUS、T07/T10、I0/I2及验收阈值。
- R2：process/attempt/run摘要分层、run键不带attempt；全员0只得ATTEMPT_EXITED_OK。run COMPLETED需权威run终态或绑定最终attempt且不会重启/续跑的受控证明，后一路径仍需完整成员全员0；缺成员不补终态，可能重试则run UNKNOWN。同步RUN_TERMINAL契约、T01/T14、I0/I3及完成验收。
- 本轮验证：PASS，macOS/Python3.9.6，exit0。`python3 scripts/check_docs.py`输出5份必需文档/13文本文件；`git diff --check`通过；标准库静态检查确认4个合成payload原文/值未变、14类编号/I0～I5齐备、R1/R2条款覆盖及旧误判规则移除、18摘要哈希/原8条不变；三文件增量及原历史/工程输入一致，有限敏感信息扫描无匹配。不是功能回放；T01～T14功能、CPU进程、双机/开销仍NOT_RUN。
- 当前修复head CI：INCONCLUSIVE（写入时）；精确新head/tree/发布后对应run/job/log与最终staged diff检查存PR #9；旧head CI PASS不替代新head。当前修正尚待独立复审。
- F-Export（已恢复）：首次将三份全文以默认ASCII转义JSON导出，工具输出预算截断，后续JSON.parse报错，尚未创建远端tree/commit或改ref。改为逐文件UTF-8 JSON读取并校验后发布；本地文档/暂存未丢失。

## 首轮验证记录

首轮本地macOS/Python3.9.6，验证对象为旧head16a8bee…的五份文档；精确SHA/发布/CI以PR记录为准。原验证及失败保留；本次修复验证见上节。检查只限文档与合成payload一致性，不表示监控功能通过。

| 检查 | 结果 | 命令 / 退出码 / 证据 |
| --- | --- | --- |
| 基线与前序审核 | PASS | `git fetch origin`、`git rev-parse HEAD origin/main` exit0；Issue #1/#6/#8、PR #7实际metadata/评论；PR已合并，旧文档待审核为历史状态 |
| 官方接口来源 | PASS（文档核对） | Python3.12 os/time、PyTorch v2.13.0 torchrun；方案内链接，仅API语义引用，不复制实现、不证明本地构建/任务来源；工具查询无shell退出码 |
| 文档与diff | PASS，exit0 | `python3 scripts/check_docs.py` → 5份必需文档/13文本文件；`git diff --check`；staged/最终diff结果保存PR |
| 合成示例/历史材料一致性 | PASS，exit0 | `python3`标准库解析4个SYNTHETIC payload，用`os.waitstatus_to_exitcode`核对0/7/15的静态编码，14类用例编号齐备；执行矩阵内公开脚本重算18摘要/原8条不变；原调查/矩阵/AGENTS/检查器/CI与main字节一致；非功能回放 |
| 范围与敏感信息 | PASS，exit0 + 人工审查 | 仅五份文档；IPv4/真实GPU UUID/私钥/常见token与password赋值/本机用户路径/SSH身份模式无匹配；不读凭据或受控材料，扫描覆盖有限 |
| 当前HEAD CI | INCONCLUSIVE（写入时） | 发布后核对本PR run/job/log与精确head/base；旧PR CI不能替代 |
| T01～T14 / CPU进程 / I0～I5 | NOT_RUN | 仅设计及样例值检查；无回放器/产品测试实现，无双机命令/现场退出码/新原始日志 |

## 阻塞与恢复

- B-Workload / B-Identity / B-Exit：无本项目获准真实任务/完整成员与进程实例/权威退出来源，接入门禁I0未满足。M0-3方案可独立审核，M1现场执行INCONCLUSIVE；须由任务所有者提供V1/V3白名单来源，不扫描全量env/args或访问旧项目。
- B-Runtime / B-Time / B-Signals：C1来源待确认，跨机误差/真实step/metrics/RAS/FR仍UNKNOWN；它们不是本切片全部前置项，但不能据此宣称真实功能或训练影响PASS。现场存储位置/访问者/保留期限/预算也待确认。
- B-Review：旧head已独立审核并要求上述两项修正，当前修复head待独立复审，M0-Gate和用户批准尚缺。M1候选C1～C4仅设计清单，未启动。
- 本轮无服务器失败或变更。一次本地批量定位命令在已完成fetch/HEAD输出后，对不存在的可选技能路径执行rg导致exit2；改为读取已列出的准确技能路径，exit0，未读取其它项目文件；不将该批量命令整体冒称exit0。
- F-Patch（已恢复）：首个多文件补丁对STATUS/HANDOFF同时使用Delete/Add，工具报multiple operations target并拒绝整批，未应用；改为独立Update及标准库完整写入，保留原历史失败链接，随后复核diff。
- F-Heredoc（已恢复）：本轮末尾状态辅助命令的结束符误用PY，Python将后续shell行视作源码并在执行前SyntaxError/exit1；文档未写入、暂存未执行。更正为匹配结束符后运行成功，随后重做检查。
- 历史失败保留于[调查记录](M0_1_INVENTORY.md)、[矩阵](M0_2_CAPABILITIES.md)及PR #4/#5/#7：Docker权限、Chrony506、dpkg混合非零、B05认证、A05截断/IndexError、08 mount模板、Git凭据/refspec/编码、候选资料URL失败、嵌套heredoc解析等。来源差异按当轮时间/作用域解释，不删除失败或升级UNKNOWN。
- 文档回退用审查revert/后续修正，不强推/覆盖；未合并、不关闭旧Issue。主智能体要求6.1Sol/High，无可靠模型/档位回读，不声称核验/切换；未委派子智能体。发布/上下文恢复见[HANDOFF](HANDOFF.md)。
