# 可恢复交接

## 当前授权与恢复锚点

- 唯一仓库：[Zwhao0/20261015](https://github.com/Zwhao0/20261015)。当前 [Issue #8](https://github.com/Zwhao0/20261015/issues/8)，母 #1。用户2026-10-15明确指令“启动 M0-3”；授权设计与Draft PR，不是服务器访问/功能实现或M1授权。
- 基线main `d36cdacb77b6b1b08392bf27b9b288952918aa98`；分支 `codex/m0-3-slice-acceptance` 从该main新建。当前Draft PR通过分支查询，精确head/tree/CI取PR描述与Checks，不猜SHA。
- M0-2 [PR #7](https://github.com/Zwhao0/20261015/pull/7) 已获[独立审核PASS](https://github.com/Zwhao0/20261015/pull/7#issuecomment-6189223408)并合并，审核head `7c9326b61bb539f1c2cf9435d41fb48a403772f4`，仅离线矩阵；本轮未操作合并。Issue #6/原矩阵中的待审核/M0-3未授权为历史状态，最新以本轮明确授权及GitHub实时事实为准，不覆盖原证据。
- 本轮完成[V0.1方案](M0_3_SLICE.md)，只五份文档；原M0_1_INVENTORY/M0_2_CAPABILITIES、AGENTS、检查器、CI不变。M0-Gate INCONCLUSIVE；未进入M1，无Detector/采集器实现。

## PR 9 两项修正与复审入口

用户已明确授权根据[审核评论](https://github.com/Zwhao0/20261015/pull/9#issuecomment-6189558036)完成两项修正。被审旧head `16a8bee3a1de5f40674d0dc3983862d8a9dc18ad` 保留；在原分支追加提交，增量仅M0_3_SLICE/STATUS/HANDOFF三份文档，新head/tree/CI核对PR #9描述与Checks。

- R1：PERIODIC有约定周期/心跳时才以15秒判STALE；EVENT_DRIVEN健康读取但数小时无新事件为IDLE，producer活性仍UNKNOWN，不能因空闲判GAP。权限/读取错误、来源消失、确认轮转缺口继续UNAVAILABLE/GAP。对应契约/SOURCE_STATUS、T07/T10、I0/I2和验收。
- R2：process/attempt/run三层终态与键分开；完整成员全0仅ATTEMPT_EXITED_OK，run保持UNKNOWN直至权威run终态或受控最终attempt且不会重启/续跑证明。最终attempt完成路径还需完整成员全0，无权威证明或仍可重试不宣告COMPLETED。对应契约/摘要、T01/T14、I0/I3和验收。
- 仅文档与静态样例检查；14类功能回放/CPU进程/双机/开销仍NOT_RUN。新head待ChatGPT独立复审，不自行宣告审核通过/合并/Gate PASS/M1授权。
- 外部ChatGPT在上述评论中已记录其第5问交接；新窗口从自己的首问计数，不沿用Codex轮数。恢复先读评论与修复增量，而不是重审旧head后直接放行。

## 设计结论与现场缺口

- 选定一个获准真实任务的基础观测及进程异常退出；入口是所有者清单/获准局部快照/启动器权威终止记录。实际任务、成员、namespace/start、Job/Rank/GPU链和退出样本尚UNKNOWN，不能用历史PID/GPU字段补成完整链。需要I0/V1/V3输入，不能读取旧项目核实。
- 契约含attempt/boot/namespace/PID/start、对象scope、source epoch/seq、事件/采集时间域、证据引用与UNKNOWN原因。PID消失/空行/超时不判退出；launcher退出不传播到全体worker；不明137不判OOM。进程终止、run最终结局、采集覆盖分开。
- T01～T14、I0～I5、量化预算/资源/回退及M1候选C1～C4已写方案，功能/CPU进程/双机/开销均NOT_RUN；当前只有合成payload值校验，不是回放功能通过。M1逐条真实命令须在对象批准后落实，不能执行虚构路径/占位符。
- A/B旧证据采集于2026-10-15 16:08:10～16:12:18及16:36:01～16:42:26 UTC+08:00；18条原文与固定PR #5/head f15050dc1c4b8bf5cd5e49d75576f19ecf7b269d一致。公开摘要哈希只证完整性，不证主机真实性；本轮未读取私密原文。
- 历史版本Torch2.13.0+cu130、Toolkit13.0.88；NCCL包/header2.30.7、编译API2.29.7、探查库2.30.7保留，不换库。C1通用运行时来源待所有者确认，确认前不用于开发/测试；真实任务NCCL/Runtime、step、指标/RAS/FR/时钟误差UNKNOWN。
- 本轮未SSH/读凭据或私密索引/读metrics私有日志/查RAS/触发FR/运行GPU训练collective/修改环境。连接与受控证据索引只在先前授权位置，公开LOCAL逻辑引用无登录能力，不因本方案默认读取。
- 用户取消清理继续有效：**不删除/停止/重启/新建容器，不删除镜像/卷。** M1回退只停止自己的采集进程，未经授权不修改训练入口/退出处理或自动清理真实记录；真实存储位置/访问者/保留期先明确。

## 新会话恢复顺序

1. 读README/AGENTS、Issue #8/#1、PR #9上述审核评论及本分支最新diff/讨论/Checks、STATUS/HANDOFF/M0_BASELINE/M0_3_SLICE；先核对旧head到新head的两项修复，核对PR #7已合并事实，再读原矩阵/18条证据。
2. `git status --short --branch`、`git remote -v`，有修改先保留，不reset/覆盖。fetch main与本开发分支，核对实际head/base和祖先；新main若改变则先审差异，不自动覆盖。
3. 干净工作区可跟踪开发分支并`git pull --ff-only`，核对HEAD/tree与PR。按README执行文档检查与diff，再按方案JSON和矩阵公开脚本校验示例/18摘要，原矩阵与调查blob应保持不变。
4. 仅继续本M0-3已授权范围的设计修正与审核交接；不得把预算当实测、JSON值检查当功能回放或把历史/合成记录当实时双机验证。M0-Gate独立审核及用户批准前不推进M1。
5. 若后续另获现场授权，先核实I0对象/任务来源/C1来源/存储/命令/安全边界；输入缺失报告阻塞，不能扫描未知作业、恢复清理或注入故障。

## 上下文与发布协议

- ChatGPT从自己的窗口首个用户问题计，每5问交接，上下文过长提前；输出可复制说明并核实GitHub可恢复，不能自动开窗，不用Codex轮数冒充外部计数。
- 主智能体要求6.1Sol/High，实际模型/档位无可靠回读，不声称核验。每小任务更新状态；约2/3/压缩前或难以追溯时，先保存安全工作、STATUS/HANDOFF并推送，再交回PR/commit/检查/阻塞，未完成不标完成。
- 子智能体仅明确委派时用6Luna/Max，配置不可用记录阻塞不擅换；指定输入/边界/DoD/证据/访问权限，不改最终共享STATUS/HANDOFF、不直接合并；接近限制提前交回证据/失败。本轮未委派。
- 终端历史缺GitHub推送凭据，可用已连接Git data创建tree/commit、创建开发分支或expected SHA/force=false更新，再fetch验证本地tree/祖先。无须用户发送秘密；发布失败须保留未推送内容并明确GitHub尚不可完整恢复。
- 状态用PASS/FAIL/NOT_RUN/INCONCLUSIVE，附命令、环境、内容/提交、退出码与证据。文档CI不是功能验收；本次精确head/tree/最终CI放PR描述，避免自引循环提交。

## 可复制到ChatGPT新窗口

```text
唯一仓库：https://github.com/Zwhao0/20261015
当前任务：https://github.com/Zwhao0/20261015/issues/8（母#1）。用户明确授权“启动M0-3”，仅设计与Draft PR；M1未授权。
先读README/AGENTS、STATUS/HANDOFF/M0_BASELINE/M0_3_SLICE、分支关联PR的diff/讨论/Checks。
分支：codex/m0-3-slice-acceptance；起点main=d36cdacb77b6b1b08392bf27b9b288952918aa98。精确交付head/tree/CI从PR描述核实。
前序PR #7已独立审核离线材料PASS并合并；审核head=7c9326b61bb539f1c2cf9435d41fb48a403772f4，评论#issuecomment-6189223408。Codex本轮未合并。
M0-3选定V0.1真实任务基础观测+权威进程异常退出；实际任务/完整身份/退出来源尚UNKNOWN。方案包含契约、UNKNOWN传播、14类未来回放、I0～I5双机验收/预算/回退和M1候选C1～C4；没有功能实现。
原18条调查证据与原矩阵不变；公开摘要哈希不证明现场真实性。本轮未读私密记录或凭据、未SSH/读metrics日志/查RAS触发FR/运行GPU训练collective。
T01～T14/CPU进程/I0～I5均NOT_RUN；合成payload值校验不是回放PASS，预算不是实测。M0-Gate及用户最终批准未完成，不进入M1。
C1通用运行时来源待确认；NCCL编译API2.29.7/探查库2.30.7差异保留，不换库。用户取消清理：不删除/停止/重启/新建容器，不删除镜像/卷。
请独立审查本PR精确head的设计与验收可执行性，按PASS/FAIL/INCONCLUSIVE结论；不要凭聊天摘要给功能或Gate PASS。外部ChatGPT五问计数由本窗口首问起维护。
PR #9旧head 16a8bee3a1de5f40674d0dc3983862d8a9dc18ad已收到评论#issuecomment-6189558036：要求两项修正，暂不批准合并。用户已授权修复，原分支追加提交，仅三份文档增量；精确新head/tree/CI从PR描述获取。
请优先复审来源合约PERIODIC/EVENT_DRIVEN（稀疏源健康读取无事件为IDLE，仅约定周期/心跳用15秒STALE）及process/attempt/run终态（全员0只代表attempt退出成功，run完成需权威终态/不会重启续跑的最终attempt证明）；T07/T10及T01/T14、I0/I2/I3/验收已同步。仍14类用例，功能测试NOT_RUN；不要把修正提交当独立审核PASS。
```

## 阻塞记录模板

```text
编号/阶段/日期；症状与脱敏证据位置；动作/命令/退出码/结果；
branch/commit/PR/未发布内容；影响与安全剩余工作；
候选方案/依据/风险；恢复条件/授权/路径。
原始敏感材料仅留授权位置，不能用公开摘要一致性代替现场真实性。
```
