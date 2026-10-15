# M0-Gate 正式审核记录

日期：2026-10-15（Asia/Shanghai）。母任务：[Issue #1](https://github.com/Zwhao0/20261015/issues/1)。本记录登记已有独立审核及合并事实；Codex负责整理、核验与发布，不代替ChatGPT独立审核或用户最终验收批准。

## 审核对象与授权

- 唯一仓库：`Zwhao0/20261015`。审核基线 main `42bce13c5bd925c74856f96de64f431526d142bf`，tree `b83c0ed32dfac917701b81be53ea5de37c75b2af`。
- PR #9 合并提交即上述main；其审核head `1ef24fe27a63791857c8bf8fb2b59b715b61e542` 的tree与合并树相同。相等只证明内容一致，不把历史CI称为本轮新head的CI。
- 历史过程：首版head `f939da8b72844f71d6af5d99373cec01a7ca046a` 写入时，用户先明确“启动：Issue #1 — M0-Gate 正式审核记录”，随后明确“批准执行M0-GATE”；当时仅登记执行授权，整体Gate为INCONCLUSIVE。随后用户在ChatGPT对“是否同意 M0-Gate 的设计与工程基线验收通过？这项批准本身不授权 M1 开发或任何服务器操作”的提问明确回答“批准”。2026-10-15（Asia/Shanghai）已由[用户最终批准记录](https://github.com/Zwhao0/20261015/issues/1#issuecomment-6190108253)及[PR #10修正要求](https://github.com/Zwhao0/20261015/pull/10#issuecomment-6190117664)登记，现同步限定Gate PASS；不回溯改写先前批准状态。
- 本轮从上述main新建 `codex/m0-gate-review-record`。范围为本记录及README/STATUS/HANDOFF/M0_BASELINE、Issue #1状态同步和Draft PR；没有采集器/Detector或功能实现，无服务器访问/现场补证。
- 既有独立Gate审查来源：[ChatGPT技术审查，评论6189883744](https://github.com/Zwhao0/20261015/issues/1#issuecomment-6189883744)。其建议和结论按原范围登记，不将Codex复核自称为第二次独立审核。

## M0 交付、审核与证据

下表PASS均为独立审核者给出的限定交付结论。审核评论里“Draft/未合并”是当时状态；本轮GitHub实际元数据确认下列PR均已合并。

| 交付 | 独立结论与审核head | 已合并PR / 正式审核 |
| --- | --- | --- |
| M0-0 工程基线与交接协议 | PASS；`6a15e4c7c1827a0b8c1c31335f8867901f5e08e5` | [PR #2](https://github.com/Zwhao0/20261015/pull/2) / [复审6187338743](https://github.com/Zwhao0/20261015/pull/2#issuecomment-6187338743) |
| M0-1 宿主机调查快照 | PASS（仅快照/脱敏证据）；`1dced3bdbbdf8a091c9bfde74fede838c56406c8` | [PR #4](https://github.com/Zwhao0/20261015/pull/4) / [审核6187891676](https://github.com/Zwhao0/20261015/pull/4#issuecomment-6187891676)；当时完整训练层仍INCONCLUSIVE |
| M0-1 容器版本补证/调查交付 | PASS（限调查目的）；`f15050dc1c4b8bf5cd5e49d75576f19ecf7b269d` | [PR #5](https://github.com/Zwhao0/20261015/pull/5) / [审核6188441126](https://github.com/Zwhao0/20261015/pull/5#issuecomment-6188441126)；18条公开摘要，不等于私密原始证据现场复核 |
| M0-2 离线能力/兼容性矩阵 | PASS（文档条件）；`7c9326b61bb539f1c2cf9435d41fb48a403772f4` | [PR #7](https://github.com/Zwhao0/20261015/pull/7) / [审核6189223408](https://github.com/Zwhao0/20261015/pull/7#issuecomment-6189223408) |
| M0-3 最小切片/验收方案及两项修正 | PASS（设计修正）；`1ef24fe27a63791857c8bf8fb2b59b715b61e542` | [PR #9](https://github.com/Zwhao0/20261015/pull/9) / [复审6189756035](https://github.com/Zwhao0/20261015/pull/9#issuecomment-6189756035) |

材料入口：[工程规则](../AGENTS.md)、[18条调查证据/失败/公开摘要](M0_1_INVENTORY.md)、[9类能力及V1～V7补证矩阵](M0_2_CAPABILITIES.md)、[V0.1方案/契约/T01～T14/I0～I5/回退/M1候选](M0_3_SLICE.md)、[技术基线](M0_BASELINE.md)、[状态及历史失败](STATUS.md)、[恢复入口](HANDOFF.md)。原调查、矩阵、方案与工程输入在本轮保持字节不变。

PR #9旧head `16a8bee3a1de5f40674d0dc3983862d8a9dc18ad` 的[两项必修意见](https://github.com/Zwhao0/20261015/pull/9#issuecomment-6189558036)及原提交保留。复审已确认：R1区分PERIODIC/EVENT_DRIVEN，15秒STALE只对约定周期/心跳适用，事件源健康且无新事件为IDLE、producer活性UNKNOWN；R2区分process/attempt/run，全员0只证明attempt退出成功，run完成另需权威终态或最终attempt无重启续跑证明。无功能回放实施。

## 分层结论与决定

| 审核范围 | 结论 | 依据与实际含义 |
| --- | --- | --- |
| M0离线设计交付及进入M1-C1离线编码的技术准备 | PASS | 既有独立Gate技术审查；材料与设计边界齐备，仍须用户授权执行M1 |
| 真实训练接入、线上信号、GPU/collective兼容、低开销 | INCONCLUSIVE | 实际输入及现场验证缺失，不能证明系统可部署/可诊断 |
| T01～T14功能回放、CPU子进程、I0～I5双机、GPU/collective、开销 | NOT_RUN | 目前仅设计和静态样例；没有实现/执行证据 |
| 整体M0-Gate | PASS（限工程基线/离线调查、矩阵、V0.1设计及M1-C1离线编码技术准备） | 独立技术审查及2026-10-15用户最终验收批准均已取得；来源为[用户最终批准记录](https://github.com/Zwhao0/20261015/issues/1#issuecomment-6190108253)，M1执行仍未授权 |
| M1～M5执行 | NOT_RUN | 本轮未获M1授权，不创建/启动M1执行Issue |

关键决定：问题是如何区分设计就绪与真实接入缺口。选择依据独立审核及用户最终批准将整体Gate登记为PASS（限工程基线/离线调查、矩阵、V0.1设计及M1-C1离线编码技术准备）；依据是Issue #1评论6189883744、6190108253及PR #10评论6190117664。首版仅获执行授权时保留INCONCLUSIVE的历史过程见上文，不捏造回溯批准。风险是读者把设计PASS误当现场能力或阶段授权；通过单列结论、批准栏、未执行项及恢复顺序核验。无需在M0为设计验收补做GPU实验或编造真实来源。

## 剩余门禁与恢复条件

| 门禁 / 当前结果 | 所需输入及恢复路径 |
| --- | --- |
| B-Approval / PASS（限Gate验收） | 2026-10-15用户已明确回答“批准”，[用户最终批准记录](https://github.com/Zwhao0/20261015/issues/1#issuecomment-6190108253)记录问题原文及严格范围；本项已解除。M1执行授权仍未取得，C2～C4现场另行审批 |
| B-Workload / B-Identity / B-Exit / INCONCLUSIVE | 任务所有者批准的实际任务、完整成员与进程实例链、白名单来源、权威退出/run最终证明；依V1/V3/I0落实，不扫描未知作业或旧项目 |
| B-Runtime / INCONCLUSIVE | 环境所有者确认历史容器候选C1是可合法复用的通用运行时；确认前不用作开发/测试，不访问旧项目核实。离线M1-C1是候选任务名称，与该容器C1不同 |
| B-Storage / INCONCLUSIVE | 明确真实存储路径、访问者/权限、保留期限及资源预算，再批准具体现场命令 |
| B-Time / B-Signals / INCONCLUSIVE | 真实事件时间源、跨机误差、真实step/metrics/RAS/FR等增强信号按后续范围补证；非本最小离线切片全部前置，不凭安装线索判可用 |
| B-Integration / NOT_RUN | 在单独授权后执行功能/CPU/双机与开销验收，保存实际命令/环境/head/退出码/受控证据；历史CPU import或版本查询不证明GPU/训练兼容 |

NCCL编译API2.29.7与探查库2.30.7差异保留，不升级/换库。禁止读取未授权凭据、日志和旧项目代码/构建产物。用户取消清理持续有效，容器停止/重启/新建/删除及镜像/卷删除均未执行。本轮只用本仓库与GitHub公开于项目的记录，未SSH或读取受控原始证据。

## 用户最终批准栏

| 字段 | 记录 |
| --- | --- |
| 本轮执行授权 | 2026-10-15（Asia/Shanghai），本Codex会话：“启动：Issue #1 — M0-Gate 正式审核记录”；“批准执行M0-GATE” |
| 最终验收批准 | PASS；2026-10-15（Asia/Shanghai），ChatGPT当前对话中用户回答“批准”，问题原文见上方历史过程；来源：[用户最终批准记录](https://github.com/Zwhao0/20261015/issues/1#issuecomment-6190108253)、[PR #10修正要求](https://github.com/Zwhao0/20261015/pull/10#issuecomment-6190117664) |
| 批准范围 | 工程基线/离线调查、矩阵、V0.1设计及M1-C1离线编码技术准备；不包含M1执行、服务器操作或现场能力通过 |
| 整体Gate记录 | PASS（限工程基线/离线调查、矩阵、V0.1设计及M1-C1离线编码技术准备）；不等于真实训练接入、兼容或开销通过 |
| M1执行授权 | 未取得；本记录或本轮文档PR合并均不自动启动M1 |

## PR #10批准状态修正

用户明确要求直接按PR #10新评论执行；在原分支以首版head `f939da8b72844f71d6af5d99373cec01a7ca046a` 为父追加最小提交，仅本记录/README/STATUS/HANDOFF/M0_BASELINE。原调查/矩阵/方案/AGENTS/检查器/CI字节不变，不重做H800调查、不另起任务书；新head/tree及新CI存PR #10，修复待独立复审，不合并、不关闭Issue、不启动M1。

## 首版验证与发布（历史记录）

验证对象为基线 `42bce13c5bd925c74856f96de64f431526d142bf` 加本轮五份文档；macOS/Python3.9.6/Git，本地命令与结果在下表及本轮Draft PR留存。精确提交head/tree、最终本地/远端一致性与对应新CI在PR描述登记，避免源文件自引提交。

| 检查 | 结果 / 命令与证据 |
| --- | --- |
| 基线/合并树/历史审核 | PASS；`git fetch origin`、`git rev-parse HEAD HEAD^{tree} origin/main`、`git diff --exit-code 1ef24fe27a63791857c8bf8fb2b59b715b61e542 42bce13c5bd925c74856f96de64f431526d142bf`，exit0；GitHub实际PR元数据及上述审核链接（工具无shell退出码） |
| 文档与空白 | PASS，exit0；`python3 scripts/check_docs.py` → `PASS: 5 required documents; 14 text files checked`；`git diff --check`通过，最终staged检查结果在PR登记 |
| 范围与保真 | PASS，exit0；标准库核对仅五份文档、六个受保护输入逐字不变、STATUS历史原文保留；有限IPv4/GPU身份/私钥/token/本机路径/SSH身份模式扫描无匹配（覆盖有限），并人工审查diff；`git diff --exit-code 42bce13c5bd925c74856f96de64f431526d142bf -- docs/M0_1_INVENTORY.md docs/M0_2_CAPABILITIES.md docs/M0_3_SLICE.md AGENTS.md scripts/check_docs.py .github/workflows/docs.yml`，exit0；精确staged tree和最终发布一致性存PR |
| 历史CI | PASS（仅历史文档CI）；本轮读取[PR #9 run38718529836](https://github.com/Zwhao0/20261015/actions/runs/38718529836) API及[job116367055675日志](https://github.com/Zwhao0/20261015/actions/runs/38718529836/job/116367055675)，确认审核head/base与13文件检查输出；不是本次新head检查 |
| 本轮新head CI | INCONCLUSIVE（写入时）；发布后核对本轮PR对应head/base、run/job/log，最终结果写PR |
| 功能与现场 | NOT_RUN；本轮不执行回放器、CPU子进程或任何服务器测试 |

本轮最初对不存在的可选根AGENTS读取exit1，随后正确读取repo/AGENTS.md，exit0；未误报为整体成功。无服务器失败。历史失败见STATUS、原证据与旧PR；文档撤销采用审查后的revert/后续修正，不覆盖历史。
