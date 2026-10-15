# M1-C2-A Owner 输入模板（空白）

2026-10-15（Asia/Shanghai），Issue #13 的 C2-A 现场输入模板。此文件是供任务所有者填写和复核的空白结构；本版本不含真实样本、主机/作业标识、PID/GPU UUID、路径、日志或凭据。未确认的单元格必须保留 UNKNOWN、BLOCKED 或 INCONCLUSIVE，不要用示例数据替代。

模板依据：[M0-2 能力矩阵](M0_2_CAPABILITIES.md)、[M0-3 切片验收方案](M0_3_SLICE.md)、[M1-C1 离线契约](M1_C1_OFFLINE.md) 与 [来源计划](M1_C2_SOURCE_PLAN.md)。填写本表仅记录审批输入，不自动授权访问服务器、运行任务、读取私有数据或实现适配器。所有实际接入命令与窗口须在另行授权的实施任务中审核。

## 填写规则

- 每项状态只能使用 CONFIRMED、UNKNOWN、BLOCKED 或 INCONCLUSIVE，并写明负责人、证据逻辑引用、确认时间/时区和适用版本。不得将“尚未询问”写为已确认。
- 身份原文和敏感证据只在所有者指定的受控位置填写/保存；公开副本中保持逻辑别名或 UNKNOWN。不要将真实值放入此仓库模板的提交版本。
- CONFIRMED 需引用受控证据，描述字段语义、来源和有效窗口；不能只引用口头猜测或日志文本。
- 必填范围缺失为 BLOCKED；即使某一来源读取成功，链路/验收仍可为 INCONCLUSIVE。禁止用合成值假装真实样本。
- 只有确认该 Job 属于本项目且不来自旧项目，才可进入后续任务来源评审。C1 仅收合成数据；真实适配需独立授权和独立实现/审查。

## I0 — 范围与权限输入

| 字段 | 所有者填写 |
| --- | --- |
| 当前状态（CONFIRMED / UNKNOWN / BLOCKED / INCONCLUSIVE） | UNKNOWN |
| 项目/实验的受控逻辑别名（不填公开真实名称） | UNKNOWN |
| Owner 责任角色与签署方式（不填个人凭据） | UNKNOWN |
| 是否属于本项目、是否明确排除旧项目（证据引用） | UNKNOWN |
| 是否为同一个获准 Job，且恰为两个节点（证据引用） | UNKNOWN |
| job_id 命名空间与来源（受控引用；公开副本留空） | UNKNOWN |
| run_id 与 job_id 的映射责任方/有效期 | UNKNOWN |
| 当前 attempt_id、重试/恢复语义和上游证据 | UNKNOWN |
| 两节点逻辑别名及有效窗口（实际 host 值只留受控索引） | UNKNOWN |
| Owner 批准的读取目的、字段、对象、窗口和结束条件 | UNKNOWN |
| 获准候选来源清单及各自状态/负责人 | UNKNOWN |
| 明确不在授权范围内的对象/字段/命令 | UNKNOWN |
| 是否有资格作为“真实任务来源证据”（否则 BLOCKED） | UNKNOWN |
| 本轮离线文档之外的实施/服务器权限是否另行批准 | BLOCKED |
| Owner 证据引用、确认时间、时区、批准版本/失效条件 | UNKNOWN |

**停止条件**：若 Job 所属项目、两个节点、读取对象或单任务范围任一为 UNKNOWN/BLOCKED，不要开始现场适配。无真实任务输入时保持 BLOCKED，离线设计可独立审查。

## V1 — Job → Run → Attempt → Worker → Process → GPU 身份链

以下表只允许在所有者受控副本中填写真实值；公开版本只保留状态、理由和不可解析的逻辑 evidence ref。每一行表示一个预期 Worker，不代表实际成员已经验证。

| Node alias | job_id evidence ref | run_id evidence ref | attempt_id / restart ordinal | world_size | rank | local_rank | Worker role | Process instance evidence ref（host/boot/ns/PID/start ticks/HZ） | PID namespace mapping proof ref | Visible GPU UUID set / mapping proof ref | 状态与 unknown reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Node A (logical) | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Node B (logical) | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

补充核对：

| 核对项 | 所有者填写 |
| --- | --- |
| 完整预期 worker 清单来源、schema/version、内容摘要引用 | UNKNOWN |
| rank 集合与 world size 的一致性、重复/缺失 rank 检查 | UNKNOWN |
| 各 worker 的 PID 是容器内、宿主还是其他 namespace 的 PID | UNKNOWN |
| host_id + boot_id + pid_namespace_id + pid + process_start_ticks + start_ticks_hz 完整性证据 | UNKNOWN |
| 同一 worker respawn 如何关联到新 process instance | UNKNOWN |
| 重启/恢复创建新 attempt 的明确规则、来源与生效时刻 | UNKNOWN |
| GPU UUID 是实际映射还是 index/local_rank 推测（必须为实际映射证据） | UNKNOWN |
| MIG/设备重映射身份粒度、配置变更与生效窗口 | UNKNOWN |
| V1 每条链完整性与未闭合边列表 | INCONCLUSIVE |

V1 链条要求：Job 和 Run 分开；每次 attempt/重启独立识别；worker 清单完整；每个 process 事件绑定完整实例；GPU 需独立 UUID 映射。缺项保持局部字段并将依赖结论标 UNKNOWN。不能把 rank=GPU index、local_rank=GPU UUID 或 PID 单字段作为映射。

### Group / Expert 并行元数据（可选、逐项批准）

不需要组/专家诊断时填写 UNKNOWN 并注明“本切片未使用”；不得读取模型 checkpoint、路由样本、训练 batch 或配置私密内容来推导拓扑。

| 元数据 | 是否必要 / 批准状态 | Schema / topology version | 生产者与 scope | 字段/映射定义及受控证据引用 | 脱敏和窗口 |
| --- | --- | --- | --- | --- | --- |
| Data parallel group / rank / members | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Tensor parallel group / rank / members | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Pipeline parallel group / rank / members | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Context parallel group / rank / members | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Expert parallel group / rank / members | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Expert ID → owner worker/rank 映射 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| membership epoch / topology epoch 的来源与生效窗口 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| 专家静态副本 / expert-tensor / virtual PP 元数据 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| token 级动态 routing / expert load（本阶段不采集） | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| 重叠 group、动态迁移或弹性拓扑规则 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| 组/专家字段缺失时依赖它的验收项 | INCONCLUSIVE | — | — | — | — |

可执行离线格式见 [ParallelContext 协议](M1_C2_PARALLEL_CONTEXT.md)。静态专家归属、专家通信组与动态 token routing 分开登记，不能互相推导；动态 routing/load 在 C2-A 固定 UNKNOWN。Group ID 不假设全局唯一或稳定，但必须在明确 scope/epoch 内可唯一引用；成员列表要说明排序语义、有效时间窗口和重叠规则。Expert ID 不能按 rank、模型顺序或均匀分配推断。未授权的拓扑/专家元数据按“不采集”处理。

## V3 — 进度、事件与权威退出来源

| 字段 | 所有者填写 |
| --- | --- |
| 每一条进度/事件/退出 source 的逻辑 ID、owner 和状态 | UNKNOWN |
| 生产者类型（scheduler / launcher / parent wait / approved event file / other）及实际名称版本 | UNKNOWN |
| 结构化 schema、schema version、字段白名单及兼容政策 | UNKNOWN |
| source_mode（PERIODIC / EVENT_DRIVEN / UNKNOWN） | UNKNOWN |
| PERIODIC 的 interval / heartbeat 定义、发送方与 freshness timeout | UNKNOWN |
| EVENT_DRIVEN 的读取到末尾语义、producer 活性如何获知 | UNKNOWN |
| source epoch / sequence / cursor 起点与连续性证明 | UNKNOWN |
| append/rename/copy-truncate/rotation 语义、检测方式、保留期 | UNKNOWN |
| 读取方式（单一对象/文件/只读端点）、精确 scope 和 byte/行/time 上限 | UNKNOWN |
| 读取身份/最小权限、拒绝权限后的行为 | UNKNOWN |
| progress step 定义、何时递增、对应的数据/优化阶段语义及其证据 | UNKNOWN |
| 进度事件绑定到 job/run/attempt/rank 的证据 | UNKNOWN |
| 退出事件的 scope（process/worker/launcher/attempt/run）及生产者定义 | UNKNOWN |
| 退出码原始格式（POSIX wait / subprocess returncode / scheduler field / other） | UNKNOWN |
| 退出码映射规则；signal、正常退出码与 shell 结果如何区分 | UNKNOWN |
| process exit 如何绑定完整实例键及 child/wait 或审计证明 | UNKNOWN |
| launcher/scheduler 事件如何证明事件来源、实例绑定、schema 与 cursor | UNKNOWN |
| scheduler 的 run-terminal 权威字段及 retry/resume 完结语义 | UNKNOWN |
| final-attempt 证据、final_attempt_id 与 no_restart_or_resume=true 的证明 | UNKNOWN |
| 普通日志是否仅作非权威线索（必须明确） | CONFIRMED: 普通日志不升级为权威退出 |
| 是否有任何必要字段尚无合法来源 | UNKNOWN |
| V3 对每个来源的结论与阻塞项 | INCONCLUSIVE |

若没有经审计绑定的 launcher/scheduler 结构化来源或本程序自有子进程 wait，所有退出字段都只可 UNKNOWN。不得 attach/reap 非子进程，也不得从 137、日志中的“killed”、PID 消失或监控空闲推断信号/OOM/退出。

## 时钟、来源版本与重启边界

| 字段 | 所有者填写 |
| --- | --- |
| 每一来源 event timestamp 的格式、时区、生产者与语义 | UNKNOWN |
| 采集/观察 timestamp 的生成方、UTC/时区、是否可调整 | UNKNOWN |
| monotonic clock 类型、domain ID 构成（host/boot/namespace/clock） | UNKNOWN |
| monotonic 计时分辨率、适用进程/namespace 与来源证明 | UNKNOWN |
| 两节点同步服务/状态、该窗口偏差/误差界及证据 | UNKNOWN |
| 是否可对跨节点事件排序或计算延迟（没有误差界应为 NO/UNKNOWN） | UNKNOWN |
| scheduler / launcher / monitor / exporter / event producer 版本 | UNKNOWN |
| schema/API/client 版本、兼容策略、未知版本处理方式 | UNKNOWN |
| 节点 reboot、容器/namespace 变化如何产生新实例/source epoch | UNKNOWN |
| launcher restart、worker respawn、scheduler retry/resume 如何建新 attempt | UNKNOWN |
| 版本变化、cursor reset、轮转断点与历史 GAP 的保留规则 | UNKNOWN |

时间必须分开保存 event time、observed time 和本地 monotonic 读时；只在同一个已证明 clock domain 内计算时间差。节点时钟同步布尔值不等同于精度证明。来源版本、epoch 或 PID 实例变化无法解释时，对应关联为 UNKNOWN。

## 退出权限与证据登记

| 退出来源/证明 | 状态 | 受控证据引用 | 证明 scope | 绑定的 process instance / attempt / run | 编码与原始字段 | cursor/版本完整性 |
| --- | --- | --- | --- | --- | --- | --- |
| Parent wait（仅本程序自有 child） | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Launcher 结构化事件 + 审计证明 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Scheduler 结构化 terminal/event + 审计证明 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| 普通日志/文本（标记为非权威） | UNKNOWN | UNKNOWN | 非权威线索 | UNKNOWN | UNKNOWN | UNKNOWN |

若没有完整实例绑定，不写“已退出”。任何来源若只能证明 launcher/task 的退出，不把它展开成各 worker 的退出。attempt 结论要按完整预期成员逐个核验；run COMPLETED 需权威 run 成功，或最终 attempt 且成员全员可信 0 退出并有不会重启/续跑证明。

## 来源读取、隐私与存储审批

| 字段 | 所有者填写 |
| --- | --- |
| 每个来源精确对象/只读端点的受控定位引用（不在公开模板填路径/IP） | UNKNOWN |
| 允许的读取主体、最小权限、授权起止时间 | UNKNOWN |
| 每源字段白名单及禁止字段列表 | UNKNOWN |
| 读取周期、单次 timeout、最大 bytes/行、最大并发 | UNKNOWN |
| 可能的共享资源或训练影响及最小评估办法 | UNKNOWN |
| 原始数据敏感等级/分类与脱敏规则版本 | UNKNOWN |
| 原始数据受控存储位置的逻辑引用和 ACL | UNKNOWN |
| 公开摘要字段、人工复核责任人和发布准则 | UNKNOWN |
| 原始与摘要分别的 hash 语义/算法/版本 | UNKNOWN |
| 访问审计、读取记录与安全事件责任方 | UNKNOWN |
| 保留期限、到期检查责任人和处置/删除授权流程 | UNKNOWN |
| 是否禁止跨 run 复用脱敏 token 或身份映射 | UNKNOWN |
| 目录/文件权限与存储容量上限 | UNKNOWN |
| 未经确认时是否不持久化真实样本（应为 YES） | UNKNOWN |

公开仓库只允许经过批准的合成样本、逻辑别名、允许导出的白名单摘要和去标识化引用。原始日志、作业/主机 ID、PID、GPU UUID、路径、环境变量、命令行、token、样本/数据内容不得写入本文件或公开证据。哈希仅用于内容一致性，不代表来源真实性。

## 性能预算与安全回退

下列为 M0-3 中的候选设计预算，必须由 owner 确认适用性；它们不是现场测量、现成实现或默认许可。若 owner 需要不同阈值，填写依据和测量方案，并在实施任务审查。

| 指标/限制 | 候选上限或目标 | Owner 确认值、证据/依据、状态 |
| --- | --- | --- |
| 每节点采集进程数 | 1 | UNKNOWN |
| 周期读取间隔 | 5 s；仅已确认 PERIODIC 源 | UNKNOWN |
| 单次读取 timeout | 1 s | UNKNOWN |
| 同时读取数 | 1 | UNKNOWN |
| 每周期最大输入 | 1 MiB | UNKNOWN |
| 单行最大大小 | 16 KiB | UNKNOWN |
| 待处理事件队列 | 1,000 行 | UNKNOWN |
| 本地输入就绪到输出延迟 | 目标 5 s；验收至少 20 对同源同单调域样本，p95 ≤5 s、max ≤10 s | UNKNOWN |
| 每节点采集 CPU | 均值 ≤1 个逻辑核的 1%（按采集进程 CPU 秒/墙钟秒） | UNKNOWN |
| 每节点采集 RSS | 峰值 ≤128 MiB | UNKNOWN |
| 本项目输出 | 每节点硬上限 100 MiB；写满停止写入并报告，不截断旧记录 | UNKNOWN |
| 存储访问模式 | 目录 0700、文件 0600；由 owner 的 OS/存储策略复核 | UNKNOWN |
| 有获准真实 step 时训练吞吐比较 | 3 对相近阶段窗口，每对降幅 ≤2%；否则 INCONCLUSIVE | UNKNOWN |
| 回退 | 仅停止本项目的采集器；≤30 s 退出；不向训练/launcher/容器发信号 | UNKNOWN |

**回退联系人/值班角色：** UNKNOWN
**回退触发阈值（权限、时延、CPU、RSS、磁盘、训练影响）：** UNKNOWN
**本项目采集器停止/重启的唯一批准方法：** UNKNOWN
**确认不会清理/停止/重启容器、训练任务或共享服务：** UNKNOWN
**回退后缺口记录、受控证据保留与复核责任人：** UNKNOWN

预算缺少、无法测量或训练影响无法区分时，现场性能结论为 INCONCLUSIVE；不要为了达成预算改环境、调度任务、启动 hostengine/profiling 或删除历史。回退只操作本项目自身进程和输出，若 owner 未给出可行回退方式则接入保持 BLOCKED。

## Owner 审批结论（填写）

| 审核项 | 状态与签署 |
| --- | --- |
| I0 范围、任务来源、双节点及权限已确认 | BLOCKED |
| V1 身份链及成员清单已确认 | BLOCKED |
| V3 结构化进度/终止来源和权威边界已确认 | BLOCKED |
| 时间、轮转、schema/version、重启规则已确认 | BLOCKED |
| 隐私、存储 ACL、保留期和发布脱敏已确认 | BLOCKED |
| 资源预算、停止方式与回退责任人已确认 | BLOCKED |
| 允许进入单独现场实施任务（该审批不替代实施授权） | BLOCKED |
| Owner role / 受控签名引用 / 时间 / 时区 / 有效期 | UNKNOWN |

## 既有文档入口

- [M0-2 能力与兼容性矩阵](M0_2_CAPABILITIES.md)
- [M0-3 切片与验收方案](M0_3_SLICE.md)
- [M1-C1 合成离线契约与回放](M1_C1_OFFLINE.md)
- [README 工程入口](../README.md)
