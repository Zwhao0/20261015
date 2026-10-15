# M1-C2-A 来源计划（离线设计）

2026-10-15（Asia/Shanghai），Issue #13 的 C2-A 文档交付。本文件只定义来源候选、字段白名单、权威边界和以后现场审批输入；当前没有任何真实 launcher、scheduler、任务、监控端点或运行时被确认。仅依据仓库已有的 [M0-2 能力矩阵](M0_2_CAPABILITIES.md)、[M0-3 切片方案](M0_3_SLICE.md) 与 [M1-C1 离线契约](M1_C1_OFFLINE.md)。不做外部新调研。

本轮是离线设计，不实现真实适配器，不读取 H800、SSH、真实进程、日志、私有数据，不使用旧项目，不安装或升级环境，不运行容器或训练源码。M1-C1 的入口拒绝 REAL origin；本文件中的字段清单不是把真实来源送入 C1 的授权或实现说明。任何实际接入都须另行明确授权及所有者确认。

## 当前结论与设计约束

- 所有候选来源的实际存在、版本、权限、字段、稳定性和性能均为 UNKNOWN。M0 历史快照只能说明当时的字段查询，不证明这些来源属于当前任务。
- 所有者 manifest 是经过批准的任务范围与身份映射声明；它本身不证明进程仍存活、进程已经退出或 run 已完成。
- 普通文本日志、stderr、grep 结果、退出样式文字和监控空白不是权威终止证据。只有精确绑定完整进程实例且由父进程 wait 取得的结果，或有可审计证明将结构化事件绑定到该实例的 launcher/scheduler 来源，才可作相应范围的权威终止事实。
- 对不是本程序创建的子进程不调用 wait，不 attach/reap 任意进程，不以 PID 复用进程身份。/proc 消失、查询空行、GPU 空闲、采集超时仅是未观测，不能推出退出。
- 进程退出、attempt 结果和 run 终态是三个不同结论。单个 worker 或一个节点 launcher 退出不能扩展到全部 worker、attempt 或 run。全员 0 只可得到 attempt 退出成功；run 成功还需权威 run 终态，或有证据的最终 attempt 且明确不会重启/续跑。
- 任一身份链、授权、字段语义、时钟域、序号连续性或来源版本不明时，保留已知局部事实，将受影响字段标 UNKNOWN；无法取得现场输入标 BLOCKED，证据不足以判定验收标 INCONCLUSIVE。不得用空值填零、猜测 Rank、补齐成员或默认权威性。

## 来源候选与最小字段

表内字段是未来申请的最小候选白名单，并非现有来源字段的事实声明。来源输出应先进入受控索引，再由批准的映射生成规范事件；身份原文、日志原文和令牌不进入公开摘要。

| 来源候选 | 申请的最小字段 | 权限及读取边界 | 可证明的权威范围 | 时间、轮转、版本与重启 | 最小读取、敏感级别、成本及缺失降级 |
| --- | --- | --- | --- | --- | --- |
| 所有者任务 manifest（人工填写或所有者导出） | 批准编号/范围；任务逻辑别名；job_id、run_id、attempt_id；两个节点的受控别名；预期 worker 成员数和每成员 rank/local_rank；每个成员的完整进程实例键或待补状态；可见 GPU UUID 映射或未知原因；组/专家拓扑版本；每个来源 ID、模式、周期/心跳、序号规则；所允许的源字段、窗口、退出证明、读取命令/接口；批准的时钟信息、脱敏、存储、访问、保留、预算及回退人 | 由任务所有者确认并签署；读取一份由所有者指定的单任务 manifest。不得枚举任务、账户、全局调度队列或节点目录。manifest 只授权明确的读取，不提供凭据。 | 确定本项目的授权范围、预期成员和逻辑身份映射。不能独立证明观察值真实、进程存活/退出或任何终态。 | 含 manifest schema/version、批准时间/有效期、生成者、内容摘要、修订序号和替代关系；对任务重启新增 attempt 修订，不覆盖已读版本。时间带时区并另列单调域（如适用）。 | 一次性读取最小文件/对象；敏感级别高（作业/节点/拓扑元数据），受控保存。成本低但人工确认成本由所有者评估。缺批准、过期、字段矛盾或签署缺失：来源范围及相关身份为 UNKNOWN，接入为 BLOCKED。 |
| Scheduler 结构化状态/事件（如果现场存在且获准） | scheduler 名称与版本/API schema；外部 Job ID 和受控别名映射；run/attempt/retry ID；节点分配及 worker/rank 映射；事件 ID/版本/序号/cursor；状态与状态语义；事件对象 scope；结束原因、原始退出码及编码；run terminal/final-attempt/no-restart 证明引用；事件时间、时区、时钟域；接收时间、源 epoch、内容摘要 | 仅只读单 Job 查询或所有者指定 event cursor；scope 限单 Job/Run，不能列出其他 Job。使用已有受控只读身份；不请求写权限，不启动、取消、重排或修改任务。具体接口由所有者填写。 | 可审计的 scheduler run-terminal 记录可证明其声明范围内的 run 终态；单个 allocation/worker 状态只证明该 allocation 范围。若要证明一个 OS 进程的退出，事件须有证据绑定完整进程实例和退出语义；仅 Job/节点终态不能伪造每个进程退出记录。 | 固定 scheduler/API/event schema 版本；保留单调 cursor/event revision、epoch、分页起点与轮转保留期。重启、重排、重试必须明确映射到新 attempt；失去 cursor 连续性或 schema 未知时标 GAP/UNKNOWN。事件时间与采集时钟分别记录。 | 只读取获准 Job 的有限字段和最小时间窗，限制响应字节、次数、timeout、分页；高敏感（Job/节点/退出元数据），控制访问和留存。轮询/接口成本未知，需实测审批。无 API、无权限、事件未保留或 scope 不清：不以队列扫描补救，相关终态/覆盖 UNKNOWN。 |
| Launcher 结构化事件及其父进程 wait（若为本项目新任务且获准） | launcher 名称/版本/schema；父子关系；spawn 产生的 PID、host、boot、PID namespace、process start ticks/HZ；job/run/attempt/rank/local_rank；可见 GPU UUID 映射；spawn token/子进程句柄的受控关联；等待对象、原始 wait 值与编码（POSIX wait / subprocess returncode 等）、规范结果、wait 取得时间；source epoch/seq/cursor；launcher 自身与 worker 的 scope；是否预期停止及其证据 | 对本程序自行创建、登记为获准任务的子进程，只等待其自身 child handle；不 wait 任意非子进程，不向运行中的任务 attach/reap，不读取任意环境变量/命令行。若消费现有 launcher 事件，仅读所有者指定文件/接口且受字段白名单约束。不得假定 torchrun 或其他 launcher 正在使用。 | 父进程 wait 只对确为其 child 且实例键匹配的那一个进程权威。Launcher 结构化终止事件只有审计证明（事件生成路径、实例绑定、退出码编码、序号完整性、schema/版本）时可作为该进程的权威终止来源；launcher 自己退出只证明 launcher。run 终态仍需单独的权威 run 证明。 | 捕获 spawn 与 wait 两端时刻，记录 monotonic clock domain 和 UTC/时区；seq/cursor/epoch 抵御重复与轮转。launcher 重启、worker respawn、PID 重用创建新的进程实例/attempt 关联。版本未知、记录丢失、编码不清时不解释退出码。 | 优先在新批准的最小 CPU 隔离验证任务中验证字段和退出编码；本轮不启动进程。只消费被明确授权的记录，限制事件/文件大小与读取周期。敏感级别高（PID、任务拓扑、退出）；有运行时成本，需要单独预算及回退方案。缺 child 关系、完整实例键或审计证明：退出结论 UNKNOWN；普通日志不能晋升为权威。 |
| 本机只读 /proc 进程快照（仅白名单 PID） | 采集节点受控别名和 boot ID；PID 与 /proc/PID/stat 中 PPID/state/starttime ticks；start_ticks_hz；可选 /proc/PID/status 的 NSpid；本地 PID namespace 标识；读取时 realtime/UTC、monotonic ns、clock domain；读取结果、错误类型、文件 cursor/采集窗口 | 只访问所有者 manifest 指定的 PID 列表及明确批准的 procfs 字段；当前用户权限范围内只读，拒绝访问即记失败。不提权，不遍历 /proc，不读 cmdline、environ、fd、maps、凭据或任意 cgroup 文件。是否能读受 procfs mount/hidepid 和权限影响，现场未知。 | 瞬时辅助关联和存在性采样；可以提供与另一个来源对齐的 PID/父 PID/开始时刻证据。它不是退出码来源，不证明训练健康，也不能仅凭 PID 或采样消失证明进程终止。 | starttime 按本机启动以来的 tick 解释，必须记录 HZ、boot ID 和 namespace；节点重启/namespace 变化改变实例域。一次采样需有 monotonic 读取时刻。procfs 不提供稳定事件 cursor；周期之间的变化可能漏过，不能声称连续完整。 | 逐个读取精确 PID 的少量小文件；采样周期、timeout、上限需现场批准和测量。敏感级别高（进程关联与节点身份）；仅受控存储。无权限、文件消失、解析不完整均记 UNAVAILABLE/UNKNOWN 或 NOT_OBSERVED，绝不生成退出。 |
| 监控候选：既有 DCGM Exporter/已批准 metrics endpoint | 仅获准 metrics 白名单字段：GPU UUID（受控）、metric 名、数值、单位、状态/哨兵语义、样本时间；endpoint/exporter/schema 版本和配置摘要；采集时间/clock domain；节点别名及 endpoint 与授权 Job 的绑定证据；响应 cursor/窗口 | 只读单个所有者指定的现有端点和 GPU 字段，不扫描端口、不启动/重配 exporter 或 hostengine、不触发 profiling。认证使用已配置的受控方式，不读取或写出凭据。 | 设备/节点指标观察；没有明确 PID/进程绑定证据时不证明 Job/Rank/GPU 归属，也不证明进程退出、训练进度或 run 终态。GPU 空闲不是退出。 | 记录 exporter/DCGM 与指标 schema 版本、配置摘要、抓取时间、样本时间及 clock domain、轮转/保留/降采样。新 exporter/配置或节点重启要有新 source epoch；采样缺口不可用旧值填补。 | 每次只取必要字段、限响应字节/超时/频率；真实开销 UNKNOWN，需先获批再测量。敏感级别中至高（资源状态及 UUID）；端点/字段未落实时不以监控安装记录代替可用性，指标缺失为 UNKNOWN。 |
| 监控候选：本机 nvidia-smi 的批准字段查询 | 若所有者证明必要，仅申请 device UUID、允许的显存/利用率字段、（需另批准时）compute-app 的 PID ↔ UUID 关联、命令/驱动版本、查询时间；不申请完整输出 | 仅执行所有者指定、只读且限时的一次白名单字段查询；不查全量设备/其他作业，不启动 profiling 或改变 GPU 状态。命令、字段、调用频率必须在现场表中逐项批准。 | 设备或瞬时进程 ↔ GPU 关联线索；不会证明该 PID 属于授权 Job，也不提供权威退出。与完整身份链缺任一链接时只作来源原始观测。 | 记录 CLI/driver 版本、字段语义、调用时刻与时钟域；快照不具事件 cursor，按每次读取单独 epoch/seq 处理。GPU/MIG 配置变更或 reboot 后需重新映射。 | 一次小范围查询，不循环高频执行；实际耗时/输出大小待现场测量。敏感级别高（PID/GPU UUID/其他作业关联），禁止公开原始输出。未批准 PID 关联或字段不存在则忽略该能力并记 UNKNOWN。 |
| 所有者指定的结构化进度/退出事件文件（如果有） | schema/生产者版本；白名单 Job/Run/Attempt、rank、event ID/seq；step 值与准确语义/更新点；源时间与时钟域；收到时间；退出 scope、实例键、原始退出码格式和审计链；文件名只留受控逻辑 ID；rotation/epoch/cursor/hash | 只读单一已批准文件/对象的白名单记录，不读普通任务日志目录或任意行；限定 bytes、窗口、字段、脱敏规则。路径/对象 URI 由所有者在受控表确认，不复制到公开材料。 | progress event 可证明其定义的进度样本，不代表训练健康或 hang。退出文字或格式自由日志不权威。若结构化终止记录需用于进程退出，仍须完整绑定实例且具 launcher/scheduler 审计证明；否则仅是未验证线索。 | 生产者/schema 版本必须明确；每条保留 seq/offset、epoch、时间戳及文件 rotation/truncation 规则。append、rename、copy-truncate、对象版本等实际方式未知。无法证明连续读取就记 GAP。 | 仅取必要尾段或 owner-export 的最小事件切片；不 grep、不搜索旧日志。敏感级别高（可能含样本路径、用户、配置或数据内容）；先字段级脱敏与审查。无明确结构、轮转/版本/完整性规则或退出证据时 UNKNOWN/INCONCLUSIVE，不解析自由文本根因。 |

任何候选都不是默认选择。所有者须按 docs/M1_C2_OWNER_INPUT.md 确认来源、合法性、字段、访问方式和预算；出现新的候选或字段时，先更新审批清单，不能由采集器自动探测。

## 身份链：Job → Run → Attempt → Worker → Process → GPU

    Job（调度任务身份）
      └─ Run（一次逻辑训练运行）
          └─ Attempt（某次执行/重试/恢复）
              └─ Worker（成员 rank / local_rank）
                  └─ Process（host, boot, pid namespace, pid, start ticks, HZ）
                      └─ GPU（该进程实际可见并经来源证明的 GPU UUID 集合）

1. **Job → Run**：需 owner/scheduler 明确 ID 映射、命名空间和有效期。scheduler Job ID 不自动等于 Run ID；launcher rendezvous ID 也不自动等于 Job ID。
2. **Run → Attempt**：每次 restart/retry/resume 使用不同 attempt_id 或有证据说明的单调 attempt 序号；记录 parent attempt、重启原因/时间（若获准）、创建来源与 cursor。不可从 PID 变化或时间间隔推测 attempt。
3. **Attempt → Worker**：完整清单列出 world_size 与每个 worker 的全局 rank、local rank、节点逻辑别名、角色及成员范围。rank 不能由 GPU index 推断；弹性 membership 变动需新的清单版本和明确生效窗口。
4. **Worker → Process**：一个 worker 可因重启关联多个不同 process instance，但在任一事件上须明确具体实例。实例键必须包含 host_id + boot_id + pid_namespace_id + pid + process_start_ticks + start_ticks_hz；使用 /proc 证据时还需说明采集 PID namespace 与该 PID 的可见关系。PID 单字段、PPID 单字段、容器名或时间邻近均不足以绑定。
5. **Process → GPU**：只登记来源实际证明的可见 GPU UUID 集合和映射方式/窗口；MIG 或设备重映射的身份粒度需由 owner 指定。local_rank、ordinal、GPU index 不能代替 UUID。无映射证据用 null 加原因，不能把空集合解释为“无 GPU”。
6. **组与专家元数据**：只接收 owner 明确提供且有 schema/version 的训练拓扑字段。候选包括 data/tensor/pipeline/context/expert parallel 的 group ID、group rank、group membership、expert ID 到 owner worker/rank 的映射、拓扑生效版本/窗口。每个字段记录生产者、scope 和更新时间。分组可重叠；不能假设 group ID 唯一、rank 连续、expert 数等于 world size，也不能按进程顺序推导专家归属。未提供时可保留局部 Worker 身份，组/专家字段为 UNKNOWN；不影响基础 Job/Run/Attempt/Process 链，但任何依赖此元数据的结论为 INCONCLUSIVE。

**链完整条件**：每条用于聚合的 worker 记录须可沿链追溯至同一个批准 Job/Run/Attempt；每次进程终止须绑定完整 process instance；GPU 归属需要独立的 UUID 映射证据。清单中预期成员和观察成员逐项对照。缺一个链接仅降该链接及依赖结论，禁止“最佳猜测”补链或将某节点 launcher 退出传播给 worker。

## 权威性与退出判定

| 输入证据 | 可写入的事实 | 禁止推断 |
| --- | --- | --- |
| 父进程 wait 的直接结果 | 由本程序创建且持有 child handle 的那个完整实例的退出码/信号，前提是 wait 编码正确解析、实例绑定未冲突 | 其他 worker、attempt、run 状态；对非子进程调用 wait；将 shell 137 单独解释成 SIGKILL/OOM |
| 有审计证明的 launcher 结构化终止事件 | 事件明确绑定完整实例、attempt 和退出编码时，可记录该 process exit；launcher 自身 scope 只影响 launcher | 从 launcher 退出广播所有 worker 退出；从一个 attempt 失败得到 run 最终 FAILED |
| 有审计证明的 scheduler 记录 | 记录声明的 Job/Run 状态；有实例级绑定和退出语义时才可证明该具体进程/worker 的终止 | 以 Job 状态代填每个 worker 的 process exit；重试仍可能发生时标 run COMPLETED |
| 普通日志/应用栈/文本错误/监控快照 | 若获准可作为有来源的非权威线索，记录原始 scope、时间和未验证状态 | 不升格为权威退出，不解析自由文本推断 exit code、signal、OOM/NCCL 根因或 run 终态 |
| /proc 查询空行、权限错误、timeout、PID 消失 | 该次查询的 NOT_OBSERVED / UNAVAILABLE 与本地读取时刻 | 不声明已退出、仍存活、训练 hang、attempt 结束或源健康 |
| 完整 Attempt 成员均有可信 EXITED/0 | ATTEMPT_EXITED_OK，同时保留成员和进程证据 | 没有独立权威 run terminal 或 final-attempt/no-restart 证明时，不得得到 RUN COMPLETED |
| 权威 run terminal 或受控 final-attempt 证明 | 按 scope/结局/证明绑定记录 run terminal；final attempt 路径还须 attempt 成员全员可信 EXITED/0 且 no_restart_or_resume=true | run 终态不补造成员退出事实；证明含混/冲突时不选择有利一条 |

退出记录必须保留原始编码格式并分别解析 EXITED / SIGNALED。不同编码不能混解；未知格式、冲突或身份绑定失败均为 UNKNOWN。expected_stop 仅从获准终止意图来源取得；缺失时为 UNKNOWN。退出原因与根因另列，不由退出码自行命名。

## 时间、轮转与源版本的共用合约

- 每一条记录区分来源 event_time、本地 observed_time、同域 monotonic_ns、时钟域、时区、误差/不确定度；采集者不得重写来源时间。只有 clock domain 相同且单调时钟已确认时才算时长。无跨机误差界时不做精确跨机排序。
- 每个源登记 schema/producer/API/client 版本、配置摘要、source ID、source epoch、sequence/cursor 语义、读起点及连续性依据。版本变更、节点 boot、源重建、序号复位、rotation 无连续 cursor、权限中断和解析失败都显式留痕。
- source epoch 更换不能清除旧 epoch 中的 GAP、UNAVAILABLE、冲突和已知退出；收到恢复后的新记录只关闭新窗口，不补写历史。重复事件按稳定 source ID + epoch + seq 去重；同槽不同内容为 conflict。
- PERIODIC 只有已由 owner 确认的间隔/心跳才可用约定 freshness 阈值；EVENT_DRIVEN 正常读取到末尾且无新事件为 IDLE，不因静默变 STALE/GAP。模式未知则状态 UNKNOWN。权限错误、源消失、cursor 断层或确认截断独立报告。
- 有限读取只保存授权字段和逻辑 evidence ref/hash；引用不作为路径自动打开。原始数据若获批保存在受控位置，公开摘要只保留批准的脱敏字段/哈希，不能以摘要哈希声称原始来源真实性。

## 现场批准清单与停用条件

每个来源的现场输入应在 [OWNER 模板](M1_C2_OWNER_INPUT.md)逐项填完，并至少包括：

- 两节点、同一 Job 的 owner 证明及“属于本项目、非旧项目”的确认；
- 每条字段的合法目的、精确查询方式、读权限、单次/周期读上限和是否可能影响训练；
- schema/producer 版本与重启、轮转、时钟域、cursor 的真实语义；
- 退出来源的 scope、进程绑定证明、wait/退出码编码或 scheduler terminal 证明；
- group/expert 字段的需要性、schema 与脱敏；默认不采集任意拓扑或模型数据；
- 存储 ACL、保留期、到期处置、脱敏和人工公开审核；
- 两节点资源/延迟预算及回退责任人、只停止本项目采集器的办法。

若任何必要批准、来源位置、字段 schema、身份绑定、读权限或预算缺失：该适配器维持 BLOCKED，已知局部证据继续标注来源但链路/退出为 UNKNOWN，现场验收为 INCONCLUSIVE。不得扫描、猜源、改配置、安装服务、升级依赖、启动容器/训练、发信号或访问 H800 补齐空缺。经审批后实际源仍不可读、超限、轮转不明、权限拒绝、进程映射冲突或影响预算时，立刻停止本项目自身读取，保留错误摘要与缺口，保持训练状态不变，并按 owner 指定恢复点提交人工复核。

组/专家的可执行离线约束及双 epoch 隔离见 [ParallelContext 协议](M1_C2_PARALLEL_CONTEXT.md)。本计划不宣称已取得现场组/专家或动态路由来源。

## 既有文档入口

- [M0-2 能力与兼容性矩阵](M0_2_CAPABILITIES.md)
- [M0-3 切片与验收方案](M0_3_SLICE.md)
- [M1-C1 合成离线契约与回放](M1_C1_OFFLINE.md)
- [README 工程入口](../README.md)
