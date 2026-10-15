# 可恢复交接

## 当前授权与恢复锚点

- 唯一仓库：[Zwhao0/20261015](https://github.com/Zwhao0/20261015)。当前[Issue #1 — M0-Gate 正式审核记录](https://github.com/Zwhao0/20261015/issues/1)。用户2026-10-15明确授权启动正式记录，并追加“批准执行M0-GATE”；仅作为执行授权，最终验收批准未取得，M1未授权。
- 从最新 main `42bce13c5bd925c74856f96de64f431526d142bf` 新建分支 `codex/m0-gate-review-record`，基线 tree `b83c0ed32dfac917701b81be53ea5de37c75b2af`。精确交付head/tree/CI查询该分支关联PR描述与Checks，不猜SHA。
- PR #9已合并，审核head `1ef24fe27a63791857c8bf8fb2b59b715b61e542` 与main树相同；[设计复审PASS](https://github.com/Zwhao0/20261015/pull/9#issuecomment-6189756035)。旧head两项修正与失败仍可从[原交接快照](https://github.com/Zwhao0/20261015/blob/1ef24fe27a63791857c8bf8fb2b59b715b61e542/docs/HANDOFF.md)、[STATUS历史记录](STATUS.md)和PR #9恢复。
- [独立 M0-Gate 技术审查](https://github.com/Zwhao0/20261015/issues/1#issuecomment-6189883744)已完成；[正式记录](M0_GATE.md)登记离线设计/离线M1-C1技术准备PASS、真实接入/兼容/开销INCONCLUSIVE、整体Gate INCONCLUSIVE待用户最终批准。Codex仅核对并记录，不冒充独立审核或用户批准。
- 本轮五份文档；原18条调查、能力矩阵、M0-3方案、AGENTS/检查器/CI不改。Issue #1同步事实和入口，Gate仍未勾选；Issue/PR不自动关闭或合并。

## 恢复顺序

1. 读README/AGENTS、Issue #1及评论6189883744、当前分支PR的diff/讨论/Checks、STATUS/M0_GATE/M0_BASELINE；有需要再读Issue #8/PR #9评论6189756035及原调查/矩阵/方案。来源冲突先记录，不从历史“待审核”自行反推最新事实。
2. `git status --short --branch`、`git remote -v`，保留现有修改。`git fetch origin`，核对main、当前PR head/tree/base及祖先；main变化先审差异，不reset/强推/覆盖。干净工作区方可跟踪本开发分支并ff-only同步。
3. 按README运行 `python3 scripts/check_docs.py`、`git diff --check`，按正式记录核对五文档范围和受保护文件字节不变。精确交付tree/CI从本轮PR取得，文档CI不是功能CI。
4. 核对用户批准栏：没有明确指令/日期/范围/来源则整体Gate保持INCONCLUSIVE、M1未授权。本轮“启动审核记录”及“批准执行M0-GATE”只明确了执行授权，不据此填最终验收批准或授权M1-C1。批准离线C1也不能扩展到C2～C4真实来源/服务器/现场；后续单独任务须明确DoD和授权。
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
当前任务：Issue #1 — M0-Gate正式审核记录。用户明确启动记录并“批准执行M0-GATE”，属于执行授权，最终验收批准仍待明确；M1未授权。
先读README/AGENTS、Issue #1及独立技术审查评论6189883744、STATUS/HANDOFF/M0_GATE/M0_BASELINE和当前Draft PR diff/Checks。
分支codex/m0-gate-review-record，从main=42bce13c5bd925c74856f96de64f431526d142bf建立，基线tree=b83c0ed32dfac917701b81be53ea5de37c75b2af；精确交付head/tree/CI从分支关联PR获取。
PR #9已获评论6189756035设计复审PASS并合并；head=1ef24fe27a63791857c8bf8fb2b59b715b61e542，与上述main树相同。M0-0～M0-3各自限定交付PASS。
独立Gate技术审查认为离线设计/M1-C1离线编码技术准备PASS，真实接入/兼容/开销INCONCLUSIVE；整体M0-Gate仍INCONCLUSIVE，待用户最终批准。技术准备PASS不等于M1执行授权。
本轮仅正式审核记录与四份入口/状态文档，原18条证据/矩阵/方案/工程文件不改；不自动合并/关闭Issue或勾Gate。请独立审核本轮精确head的记录与范围，之后由用户决定。
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
