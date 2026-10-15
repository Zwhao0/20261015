# M1-C2-A 当前执行状态（2026-10-15，Asia/Shanghai）

- 用户明确授权 [Issue #13](https://github.com/Zwhao0/20261015/issues/13) 的 C2-A 离线设计、实现和合成测试；C2-B 未授权。已核对远端 main=`504d43b2c66ff1d79959a94fe75b053729cc72f2`，tree=`dec625b9a2daf745a71515f32daab75f35ab2e0c`，PR #12 已合并、Issue #11 已关闭及独立复审6191123236。仓库旧“C1待审核/C2未授权”是历史，不覆盖本次授权。
- 新分支 `codex/m1-c2-a-parallel-context` 从该 main 建立。已读 AGENTS/README/STATUS/HANDOFF/M0_BASELINE/M0_2/M0_3/M1_C1 和 Issue #13，只访问本仓库。基线52测试实际 PASS/exit0，日志见 [C2-A证据](../evidence/c2-a/README.md)。
- 已写入 [来源计划](M1_C2_SOURCE_PLAN.md)、[Owner模板](M1_C2_OWNER_INPUT.md)、[独立ParallelContext协议](M1_C2_PARALLEL_CONTEXT.md)、纯 Python validator/normalizer 及合成fixture；当前集成审核中。C1 schema/源码/原52测试及golden、冻结M0/工作流/检查器不修改。
- 本地新增测试首轮35项/1错误/exit1：manifest尚未落盘；其余34项通过。补齐六份fixture SHA清单后相同35项 PASS/exit0，未改断言。原输出脱敏保存；子任务早期文档检查发现4行尾空格和主窗口未写完的3个链接，待集成后按原检查器全仓复核。完整最终测试/CI仍待执行，不能声称验收通过。
- 来源文档及只读反例审查委派 6 Luna/Max 子智能体；无可靠运行时配置回读，不声称主/子配置已切换或核验。子任务不修改最终状态，不直接提交/合并；由主窗口集成复核。
- 真实 launcher/scheduler/owner manifest/进程实例/GPU链、组/专家元数据、token routing、权限/存储/时钟/预算均 UNKNOWN；现场门禁 BLOCKED/INCONCLUSIVE。无H800/SSH/真实日志/私有数据/凭据/旧项目、GPU/训练/collective、安装升级或容器操作；不进入C2-B/C3、不合并、不强推。
- 恢复：先读 Issue #13、分支关联 Draft PR 的最新 head/tree/diff/Checks，再读上列三份C2文档与证据；核对 main/工作区，保持现有安全改动，运行 README 中功能与文档命令。精确交付HEAD/tree及新双job CI以本轮PR为准，禁止套用C1历史CI。失败用后续修复/revert保留，不覆盖历史。

下方历史全文保留，仅按其写入时点解释。

# PR #12 R1 最小修正（2026-10-15，Asia/Shanghai）

- 用户明确要求直接执行 [审核评论6190850559](https://github.com/Zwhao0/20261015/pull/12#issuecomment-6190850559)；被审HEAD `4624b7dc1f45e0ed1cfafd313966289840cd4bed`，tree `62f22a5442949e57380a6d4cbe895af2d3418eba`；main仍 `801fd156c2d39f696efa38811b0c0b433209b2d3`。在原分支/原Draft PR追加，不合并、不强推、不进入M1-C2。
- 修复：complete成员清单仅接受attempt作用域且成员为worker；聚合器收取manifests时再次核对identity/payload两处attempt scope。其余进程退出和最终Attempt证明规则不变。
- 实际反例：修复前新增8项回归在原代码上FAIL/exit1（18个子断言失败），包括伪完整清单+全员0+FINAL_ATTEMPT被误判COMPLETED。修复后8项及全部52项PASS/exit0，0失败/0错误/0跳过；保留局部IDENTITY和合法Attempt清单正例，并单独验证绕过输入校验后聚合器仍拒绝局部清单。
- [本轮原始失败/恢复/内容哈希证据](../evidence/README.md)已保存；原44项测试、T01～T14全部golden/哈希清单、M0原文及既有失败文件逐字不变。文档检查与功能结果分开；新HEAD/tree/双job新CI发布后以PR #12描述和Issue #11为准，旧44项CI不替代本次52项。
- 独立审核已发现R1，核心语义验收仍待修复提交复审；本节的PASS仅指实际测试，不能宣布M1-C1最终验收通过。无业务代码修改、低开销、MoE及DP/PP/TP/EP适配是已登记的后续要求，本次未实现或验证现场能力，不扩展schema或改冻结M0文档。本轮未委派子智能体。
- 恢复：先读上述审核及PR #12最新head/diff/Checks，再读本节和M1_C1_OFFLINE；保留原44项历史证据，按README命令运行52项全套和独立文档检查，等待ChatGPT复审。

# M1-C1 当前执行状态（2026-10-15，Asia/Shanghai）

- 用户已在本Codex会话明确授权“启动 M1-C1 离线开发”。[Issue #11](https://github.com/Zwhao0/20261015/issues/11)；PR #10已合并，开发起点 main `801fd156c2d39f696efa38811b0c0b433209b2d3`、tree `1f0136752f63cc2b9bca5a2ce0e2c2bac11394e3`，分支 `codex/m1-c1-offline-replay`。
- 仅标准库/合成数据/虚拟时间的schema 0.1离线契约、回放、三层聚合及T01～T14；不访问旧项目、H800、凭据或训练数据，不使用历史C1容器，无GPU/服务器/训练/环境或容器操作。不合并，不推进M1-C2。
- [Draft PR #12](https://github.com/Zwhao0/20261015/pull/12) 已发布，保持Open/Draft/未合并；实现提交 `2386bf43fc54189c40513612b9c9079592b31a1b`、tree `4ed01955e92018e9de9988a2cf6057552aedbddd`。首轮 [CI run38724950172](https://github.com/Zwhao0/20261015/actions/runs/38724950172) 的unit44项与docs检查分别PASS，已读取原始日志；该结论仅对应此实现head。证据跟进提交的最终head/tree/新CI见PR，不套用旧head CI。
- 实现及44项功能测试已集成；本地标准库unittest PASS（44项、0失败、0跳过），文档与差异检查分开保存于 [M1-C1证据](../evidence/README.md)，最终HEAD/tree/对应CI以Issue #11关联Draft PR为准；独立验收待ChatGPT检查，不自行宣布阶段通过。
- 保留失败：子任务fixtures施工缺失14项错误、初版schema_version遗漏；首次集成T09序号冲突1失败及原fixture；首次文档检查两个证据文件尚未落盘导致exit1。恢复未放宽断言或文档检查，详情见 [使用及限制](M1_C1_OFFLINE.md)。
- 发布失败及恢复：普通fetch未包含新分支，merge报not something we can merge（exit1）；显式fetch后ff-only同步成功，但设置跟踪因缺refspec失败（exit128）。仅追加本分支fetch refspec后跟踪成功、工作区干净；远端commit/tree一致，不强推、不改main。Git data工具发布后通过fetch/ff-only核对。
- 恢复顺序：先核对Issue #11和本分支Draft PR真实head/tree/diff/CI，再读本节、M1_C1_OFFLINE、冻结M0_3_SLICE；保持当前改动，按M1文档分别运行功能与文档命令。仅继续本离线任务；M1-C2/现场/合并仍未授权。
- 两个子任务分别实现契约与只读反例审查，未修改共享状态或合并；配置请求6Luna/Max但无可靠回读。未声称主智能体切换或完成外部ChatGPT独立验收。
- 下面原M0状态及其“未授权/待审核”措辞按历史写入时间解释，全文保留，不覆盖本次明确授权。

# 可恢复交接

## 当前授权与恢复锚点

- 唯一仓库：[Zwhao0/20261015](https://github.com/Zwhao0/20261015)。当前[Issue #1 — M0-Gate 正式审核记录](https://github.com/Zwhao0/20261015/issues/1)。用户2026-10-15明确授权启动正式记录，并追加“批准执行M0-GATE”；当时仅作为执行授权；2026-10-15后续[用户最终批准记录](https://github.com/Zwhao0/20261015/issues/1#issuecomment-6190108253)已登记最终Gate批准。当前用户已明确按[PR #10修正要求](https://github.com/Zwhao0/20261015/pull/10#issuecomment-6190117664)执行最小状态修正；M1执行仍未授权。
- 从最新 main `42bce13c5bd925c74856f96de64f431526d142bf` 新建分支 `codex/m0-gate-review-record`，基线 tree `b83c0ed32dfac917701b81be53ea5de37c75b2af`。精确交付head/tree/CI查询该分支关联PR描述与Checks，不猜SHA。
- PR #9已合并，审核head `1ef24fe27a63791857c8bf8fb2b59b715b61e542` 与main树相同；[设计复审PASS](https://github.com/Zwhao0/20261015/pull/9#issuecomment-6189756035)。旧head两项修正与失败仍可从[原交接快照](https://github.com/Zwhao0/20261015/blob/1ef24fe27a63791857c8bf8fb2b59b715b61e542/docs/HANDOFF.md)、[STATUS历史记录](STATUS.md)和PR #9恢复。
- [独立 M0-Gate 技术审查](https://github.com/Zwhao0/20261015/issues/1#issuecomment-6189883744)已完成；[正式记录](M0_GATE.md)登记离线设计/离线M1-C1技术准备PASS、真实接入/兼容/开销INCONCLUSIVE、整体Gate现为PASS（限工程基线/离线调查、矩阵、V0.1设计及M1-C1离线编码技术准备）；先前待批准INCONCLUSIVE为历史状态。Codex仅核对并记录，不冒充独立审核或用户批准。
- 本轮五份文档；原18条调查、能力矩阵、M0-3方案、AGENTS/检查器/CI不改。Issue #1同步事实和入口，Gate按最终批准勾选；Issue/PR不关闭或合并。

## 恢复顺序

1. 读README/AGENTS、Issue #1及评论6190108253/6189883744、PR #10评论6190117664、当前分支PR的diff/讨论/Checks、STATUS/M0_GATE/M0_BASELINE；有需要再读Issue #8/PR #9评论6189756035及原调查/矩阵/方案。来源冲突先记录，不从历史“待审核”自行反推最新事实。
2. `git status --short --branch`、`git remote -v`，保留现有修改。`git fetch origin`，核对main、当前PR head/tree/base及祖先；main变化先审差异，不reset/强推/覆盖。干净工作区方可跟踪本开发分支并ff-only同步。
3. 按README运行 `python3 scripts/check_docs.py`、`git diff --check`，按正式记录核对五文档范围和受保护文件字节不变。精确交付tree/CI从本轮PR取得，文档CI不是功能CI。
4. 核对批准栏及Issue #1评论6190108253：2026-10-15用户已批准限定Gate验收，工程基线/离线调查、矩阵、V0.1设计及M1-C1技术准备PASS；此前两条执行授权及待批准INCONCLUSIVE仅为历史过程。M1-C1执行仍未授权，C2～C4真实来源/服务器/现场另行审批，不因Gate PASS启动M1。
5. 等待本次文档PR独立审核和用户决定。下一步可安全继续仅限本记录的事实修正；不以真实输入缺失为由补做服务器探查、故障注入或功能实现。

## 未验证项与现场边界

- 真实任务/成员身份Host/boot/namespace/PID/start/Job/Run/Rank/GPU、权威退出与run最终证明、C1通用运行时来源、存储/访问者/保留期、跨机时钟及现场命令仍UNKNOWN；真实信号与GPU/collective兼容INCONCLUSIVE。
- T01～T14功能回放、CPU子进程、I0～I5双机、开销均NOT_RUN。四条SYNTHETIC payload只做过静态校验；阈值为设计预算，不能当实测。M1-C1指离线契约/回放候选，与历史容器候选C1不同；容器来源确认前不得用于开发/测试。
- 保留R1/R2设计：约定周期/心跳才用15秒STALE；稀疏源读取/连续性健康且无事件为IDLE、producer活性UNKNOWN。全员EXITED/0仅ATTEMPT_EXITED_OK；run完成需权威终态或不会重启续跑的最终attempt证明（后一路径还需完整成员全员0）。
- 不访问旧项目代码/构建产物或未授权日志/凭据。后续现场授权须先明确I0/V1/V3、运行时合法来源、受控存储/命令与预算；不扫描未知作业，不用历史PID补全真实身份链。
- 用户取消清理持续有效：不停止/重启/新建/删除容器，不删除镜像/卷。无训练入口/退出处理修改，未来回退仅停止自己的采集进程，受控记录按获准保留策略处理。
- 本轮无SSH/私密材料读取/GPU训练/collective/RAS/FR/环境变更。历史NCCL编译API2.29.7与探查库2.30.7差异保留，不换库。

## 上下文与发布协议

- ChatGPT从自己窗口首问计，每5问交接，上下文过长提前；不能替用户开窗，不用Codex轮数冒充外部计数。新窗口从自己的首问开始。
- 主智能体配置要求6.1Sol/High，无可靠回读则不声称核验或切换。每小任务更新状态，约2/3或难追溯/压缩前先保存安全工作、STATUS/HANDOFF并提交推送，再交回PR/commit/检查/阻塞；未完成不标完成。
- 子智能体仅明确委派时用6Luna/Max；不可用如实记录，不擅换。指定输入/边界/DoD/证据，不改共享最终状态，不直接合并；上下文紧张先交回证据/失败。本轮未委派。
- 终端历史缺GitHub推送凭据，可用已连接Git data创建tree/commit及新开发分支（或expected SHA/force=false更新），fetch核对tree/祖先并ff-only同步；不要求用户提供秘密。推送失败记录未发布内容，明确GitHub尚不能完整恢复，不自动改main。
- 检查用PASS/FAIL/NOT_RUN/INCONCLUSIVE，附命令、环境、验证对象、退出码和证据。精确新head/tree/最终CI写PR，避免循环自引。回退用审查revert或后续修正，保留失败，不强推改史。

## 可复制到ChatGPT新窗口

```text
唯一仓库：https://github.com/Zwhao0/20261015
当前任务：Issue #1 — M0-Gate正式审核记录。用户先授权记录执行，后于2026-10-15在ChatGPT明确“批准”限定Gate验收，登记于Issue #1评论6190108253。当前按PR #10评论6190117664修正五文档及Issue摘要/勾选；M1执行仍未授权。
先读README/AGENTS、Issue #1及独立技术审查评论6189883744、STATUS/HANDOFF/M0_GATE/M0_BASELINE和当前Draft PR diff/Checks。
分支codex/m0-gate-review-record，从main=42bce13c5bd925c74856f96de64f431526d142bf建立，基线tree=b83c0ed32dfac917701b81be53ea5de37c75b2af；精确交付head/tree/CI从分支关联PR获取。
PR #9已获评论6189756035设计复审PASS并合并；head=1ef24fe27a63791857c8bf8fb2b59b715b61e542，与上述main树相同。M0-0～M0-3各自限定交付PASS。
独立Gate技术审查认为离线设计/M1-C1离线编码技术准备PASS，真实接入/兼容/开销INCONCLUSIVE；整体M0-Gate已由独立审查及用户最终批准为限定范围PASS（工程基线/离线调查、矩阵、V0.1设计及M1-C1离线编码技术准备）。先前INCONCLUSIVE为批准前历史；M1执行仍未授权。
本轮仅正式审核记录与四份入口/状态文档，原18条证据/矩阵/方案/工程文件不改；Gate按批准勾选，Issue保持Open；不合并PR、不关闭Issue。请独立复审当前修复head及新CI，再由用户决定合并；无需再次询问Gate验收批准。
T01～T14功能回放/CPU子进程/I0～I5/GPU/collective/开销均NOT_RUN；实际任务/完整身份/权威退出与run最终证明/运行时来源/存储权限保留/时钟/命令仍缺。不得将合成静态校验或文档CI当功能验收。
离线M1-C1候选与历史容器候选C1不同；C2～C4真实接入/服务器/现场需要单独授权。禁止旧项目访问或环境变更；取消容器清理持续有效。本轮无SSH/凭据/私密证据读取，未委派子智能体。五问计数由新ChatGPT窗口首问起维护。
```

## 阻塞记录模板

```text
编号/阶段/日期；症状与脱敏证据位置；动作/命令/退出码/结果；
branch/commit/PR/未发布内容；影响与安全剩余工作；
候选方案/依据/风险；恢复条件/授权/路径。
原始敏感材料仅留授权位置，公开摘要一致性不替代现场真实性。
```
