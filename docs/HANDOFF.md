# 可恢复交接

## 当前授权、入口与停止点

- 唯一仓库：[Zwhao0/20261015](https://github.com/Zwhao0/20261015)，当前 [Issue #3](https://github.com/Zwhao0/20261015/issues/3)，只做 M0-1。最新 main `4ae0555c6fca24a6082e8e6af4ac40f107cb6716`（PR #4 合并）；初始历史起点为 `41a30e0…`。
- 用户本轮允许访问所有既有容器、使用已提供凭据与现有 sudo，优先复用 PyTorch；实际只查系统/第三方包和 CPU 导入，没有改权限、安装依赖、下载/上传/构建、运行训练。已找到 A/B 各自运行 C1，候选可导入，不需构建新环境。
- **最新用户决定：“先不清理了，找到一个可用的就行。”清理取消，删除/停止/重启/新建容器均为 0。不得恢复先前清理请求；不执行 rm/prune/stop/restart。**
- 原 [PR #4](https://github.com/Zwhao0/20261015/pull/4) 的宿主机快照 1dced3bdbbdf8a091c9bfde74fede838c56406c8 已获 [独立文档交付 PASS](https://github.com/Zwhao0/20261015/pull/4#issuecomment-6187891676)，训练验收仍 INCONCLUSIVE。初读 #4 为 Ready，Draft 操作返回 FORBIDDEN；后续 fetch/API 核实已合并为上述 main，未变更旧分支/旧 HEAD，未自行合并。不能把该错误笼统视为开放 PR 的权限限制。
- 当前分支 `codex/m0-1-container-inventory` → 最新 main；[Draft PR #5](https://github.com/Zwhao0/20261015/pull/5) 已发布，Draft/Open/Unmerged。首个补证提交 `7ee7cc57c99e1af97e7d01eea7dc427975e72ea2`，交接提交整合新 main 的父关系；只展示旧快照之后的增量，不将旧审核/CI 套到新 head。精确 head/tree/CI 保存于 PR #5 描述。
- M0-2/M0-3/M1 未授权、未执行；M0-Gate 仍 INCONCLUSIVE。当前停在容器补证交付/独立审核门禁，不进行 GPU/训练验收。

## 事实、证据与缺口

- 首轮 8 条 E-A/B-01～04（16:08:10～16:12:18），新增 10 条 E-A/B-05～09（16:36:01～16:42:26），均 2026-10-15 Asia/Shanghai。完整 UTC、命令、执行状态、分层退出码、规范摘要/哈希见 [调查记录](M0_1_INVENTORY.md)，机器/容器事实见 [基线](M0_BASELINE.md)。原 8 条摘要字节/哈希不变，现公开校验覆盖 18 条。
- A/B 容器均为 Ubuntu 24.04、Python 3.12.3、Torch 2.13.0+cu130、nvcc 13.0.88、Transformers 5.17.0、Accelerate 1.15.0。只查第三方发行包，不读旧项目代码/配置/日志/构建内容。CPU 导入和版本查询 exit 0；CUDA 初始化标记始终 false；GPU/双机训练 NOT_RUN。
- NCCL 包/header 2.30.7；Torch NCCL API (2,29,7)；本进程已映射库 RTLD_NOLOAD + ncclGetVersion 返回23007/exit0（2.30.7）。保留差异，不声明兼容性；真实训练进程库版本、任务归属/launcher/Rank/日志/metrics/RAS/FR/时间精度仍 UNKNOWN。
- B05 sudo 失败、A05 截断、本地前缀 IndexError、A/B08 mount 模板缺键均保留；06/09 修复或凭据对应后的成功是另一次证据，不能覆盖失败。清理只到元数据盘点，已取消，不能声称回收空间。
- 原始证据、节点/容器定位、密码解析器与**用户本地使用指南**仅在授权本机 Git 忽略受控目录，公开用 LOCAL/<证据ID>。使用指南不含密码；若需原始材料/连接入口，应通过用户私下取得受控索引，不能从公开 GitHub 找凭据或公开内部身份。TOFU 无带外校验的来源信任限制仍保留。
- Github 终端无推送凭据，使用已连接 Git data 创建 tree/commit、以 expected SHA/force=false 仅更新开发分支，fetch 后校验树与祖先关系。推送失败须记录未发布内容，不能声称 GitHub 可完整恢复。

## 新会话恢复顺序

1. 先读唯一仓库 README/AGENTS、Issue #3、原 PR #4 的独立审核及当前补证 Draft PR（diff/讨论/Checks）、STATUS/HANDOFF/M0_BASELINE/M0_1_INVENTORY。
2. `git status --short --branch`、`git remote -v`；非干净先保留调查，不 reset/覆盖。fetch main、codex/m0-1-inventory、codex/m0-1-container-inventory，核对 PR #5 的 main base/head，不强推。
3. 干净工作区跟踪当前补证分支后 pull --ff-only，核对 HEAD/tree 与补证 PR；旧 #4 的 CI/审核不是新提交验证；#4 已合并。若后续 main/PR/分支状态变化，先核对 GitHub 最新状态，不擅自重定向/合并。
4. 复核 18 条公开摘要只证明摘要完整性；无原始材料不冒称现场复测。未经新明确授权不继续 SSH、重新执行探针、扫描/删除容器或读任务内容。
5. 只修复当前补证审核指出的问题；用户已取消清理。ChatGPT 独立审核及用户批准前，不推进 M0-2/M0-3/M1。

## 三类角色的上下文检查点

- **ChatGPT**：自己的窗口从首个用户问题计，每5问交接；上下文过长提前。输出可复制说明并核实 GitHub 已保存，不能自动开窗；Codex轮数不替代外部ChatGPT计数。
- **Codex 主智能体（要求6.1 Sol/High）**：每小任务写状态；约2/3、压缩前或难追溯决定时，先写STATUS/HANDOFF、提交/推送安全工作，再汇总PR/commit/测试/阻塞。不靠自动压缩保存唯一进度；模型/档位无可靠回读，不能声称已核验。
- **子智能体（要求6 Luna/Max）**：仅明确委派，限定输入、可改范围、DoD和证据/访问边界；不得并发擅自操作服务器，不改共享最终状态、不直接合并。接近限制先交回安全改动/失败/证据/风险/未完成项/恢复点，配置不可用记录阻塞，不擅自替换。本轮未启动子智能体。
- 完整规则见[AGENTS](../AGENTS.md)；失败、阻塞与检查结果见[STATUS](STATUS.md)。

## 可复制到 ChatGPT 新窗口

```text
唯一仓库：https://github.com/Zwhao0/20261015
当前：https://github.com/Zwhao0/20261015/issues/3；仅审核M0-1容器补证。
请读README/AGENTS、docs/STATUS、HANDOFF、M0_BASELINE、M0_1_INVENTORY，以及补证Draft PR和旧PR #4独立审核。
分支codex/m0-1-container-inventory；PR：https://github.com/Zwhao0/20261015/pull/5（Draft）。
base/main=4ae0555c6fca24a6082e8e6af4ac40f107cb6716，原PR #4已合并；旧审核只覆盖原1dced3b…快照。
当前PR/精确HEAD/tree/CI：从补证分支关联Draft PR描述与Checks核实，不猜测。
18条证据：原8条摘要不变，新增A/B各05～09。现有PyTorch导入成功；NCCL API 2.29.7与探查进程库2.30.7差异保留。
用户已取消清理，没有删除/停止/重启/新建容器；不得恢复删除请求。
真实训练/Rank/信号/同步精度仍UNKNOWN；GPU/collective/双机训练NOT_RUN，不给全量PASS。
原始材料/使用入口仅私下受控索引；公开哈希不是现场真实性证明。
旧PR #4审核只覆盖旧快照；补证需重新独立审核，用户批准前不推进M0-2/M0-3/M1，不自动合并。
ChatGPT窗口计数由外部旧窗口填入；新窗口从自己的首个问题计数。
```

## 阻塞记录模板

```text
编号/阶段/日期；症状与脱敏证据位置；动作/命令/退出码/结果；
branch/commit/PR/未推送内容；影响与安全剩余工作；
候选方案/依据/风险；恢复条件/授权/路径。
结果用PASS/FAIL/NOT_RUN/INCONCLUSIVE，原始敏感材料只留授权位置。
```
