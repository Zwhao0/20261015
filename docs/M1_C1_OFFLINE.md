# M1-C1：合成离线契约与确定性回放

2026-10-15（Asia/Shanghai），[Issue #11](https://github.com/Zwhao0/20261015/issues/11)。用户已明确授权“启动 M1-C1 离线开发”；[PR #10](https://github.com/Zwhao0/20261015/pull/10)已合并。起点 main `801fd156c2d39f696efa38811b0c0b433209b2d3`，tree `1f0136752f63cc2b9bca5a2ce0e2c2bac11394e3`。冻结依据为 [M0-3 方案](M0_3_SLICE.md)，M0原文/历史证据保持不变。交付尚待 ChatGPT 独立审查及用户验收；不能据单元测试宣告阶段通过。

## 使用

仓库根目录、Python 3.9+，仅标准库；不安装依赖。运行时不访问网络、不读取进程/GPU、不打开证据引用。使用本仓库合成 fixture：

```sh
python3 -m observatory tests/fixtures/T01.jsonl
python3 -m observatory - < tests/fixtures/T01.jsonl
python3 -m unittest discover -s tests -v
python3 scripts/check_docs.py
git diff --check
```

CLI向stdout输出UTF-8 JSONL：规范事件、隔离诊断、最后一行SUMMARY；固定键序/无随机数/无真实时钟。未发生输入隔离时exit 0；坏行/冲突/截断/超限仍输出可用结果但exit 1；输入不可读或输出失败/超过100MiB则exit 2。`--max-records N`接受1～1000，默认1000；这是有限离线批次上限，超限不继续消费尾部，不将部分批次聚合为attempt/run终态。处理成功不表示训练健康或覆盖完整，必须检查摘要中的UNKNOWN/GAP等状态。

单行包括LF不得超过16KiB。有限文件的EOF非LF帧隔离为INCOMPLETE_FRAME，后续合法完整行继续处理；离线批次没有真实时间等待或活跃文件tailing。超长帧最多丢弃1MiB寻LF，找到后继续；超过该上限则FRAME_READ_LIMIT并停止该批次。空行/重复JSON键/无效UTF-8/NaN/Infinity/未知字段/版本/类型/枚举被隔离，不回显原始坏行。没有新字节就是EOF，不产生STALE/GAP。在线帧完成期限、周期读、磁盘权限/轮转监控、实时队列背压属于M1-C3，未实现。

## 模块与接口

- [contract.py](../observatory/contract.py)：`validate_record(record)` 返回独立规范化副本；失败抛 `InvalidRecord`，错误只包含固定字段路径/原因。区分字段缺失、null、0与枚举UNKNOWN。
- [engine.py](../observatory/engine.py)：`Replay.feed(bytes)`接收一个LF帧；`result()`返回可序列化的规范事件、诊断和三层摘要。`replay(iterable,max_records=1000)`有界消费。没有I/O或全局状态，可在输入之间调用result观察更正。
- [命令行](../observatory/__main__.py)：有界读取及确定性JSONL导出，不打开输入内的任何引用；读取入口文件由调用者明确指定。
- [测试](../tests/test_replay.py)提供T01～T14精确快照与独立语义断言；[边界测试](../tests/test_boundaries.py)及[契约测试](../tests/test_contract.py)补充攻击输入及正反例。

本接口仅用于公开合成离线数据：schema保留origin枚举含义，但入口安全门拒绝REAL。身份/来源/时钟/证据逻辑标识要求`SYN_`前缀（最长132字符，ASCII字母数字及`_.:-`）；PID和start ticks为合成整数。它不是真实身份真实性验证，也不允许把真实数据加前缀后输入。自由文本拒绝路径/常见credential模式，未知字段拒绝；有限模式检查不等于通用脱敏系统。真实适配/受控存储/授权来源及保留策略留给后续另行授权任务。

## v0.1 可执行字段说明

完整输入见 [T01 JSONL](../tests/fixtures/T01.jsonl) 与 [T07 JSONL](../tests/fixtures/T07.jsonl)。所有公共/identity/time字段必需；null必须有`unknown_reasons`的对应路径及非空原因。路径使用`identity.rank`、`payload.members[0].rank`等语法。字段缺失不能用null理由代替。GPU映射null和有依据空数组分开。`scope`明确对象为worker/launcher/attempt/run。

公共封装沿用M0-3表，另将其证据表中的`source_cursor`和`content_sha256`放在顶层；后者为被引用记录的SHA-256字符串，示例值仅占位，不是自包含封装的循环哈希，不证明来源真实性。`evidence_ref`是不可解析的合成逻辑引用。输入event_id为来源标识；规范输出按`(source_id,source_epoch,source_seq)`的规范JSON SHA-256生成`evt_`标识。去重内容哈希使用**校验前原始JSON对象的规范字节**，包括输入event_id、证据与unknown_reasons；键序/空白不影响。无真实证据解析或密码学权威校验；已批准的合成authority标签仅模拟权威来源。

以下将冻结表格中的对象展开为固定结构，未新增推断：

| payload | 字段 |
| --- | --- |
| IDENTITY | `scope,members,membership_complete`；members为完整identity对象列表；attempt清单使用顶层identity.scope=attempt，成员scope=worker |
| SNAPSHOT | `process_presence,device_samples,progress`；sample为`{gpu_uuid,metrics}`；metrics白名单memory_used/memory_total（bytes）、utilization（percent），各为`{value,unit,status}`；status=OK/UNKNOWN/ERROR |
| progress | null或`{step,semantics,source_id}`；step为非负整数或有理由的null；来源/语义不可推测，step=0和未变化均保留，不生成hang结论 |
| PROCESS_EXIT | M0-3定义全部字段；authority=parent_wait/launcher/scheduler/log_unverified/UNKNOWN；raw_status_format=posix_wait/subprocess_returncode/shell_unverified/UNKNOWN；原始编码必须与声明的kind/code/signal一致 |
| RUN_TERMINAL | `scope,authority,proof_kind,outcome,final_attempt_id,no_restart_or_resume`；authority=scheduler/launcher/UNKNOWN；已知outcome需要完整且匹配的权威proof；缺证据的合法null保留UNKNOWN，互斥字段/错误类型隔离 |
| SOURCE_STATUS | `source_mode,expected_interval_ms,freshness_timeout_ms,last_successful_read_monotonic_ns,last_record_age_ms,status,read_status,reason,affected_source_id`；本离线结构为来源自报告，affected_source_id必须等于source_id，跨源代报拒绝 |

PERIODIC要求正周期及15000ms阈值；EVENT_DRIVEN/UNKNOWN的两项周期为null。`last_successful_read_monotonic_ns`由采集者在**observed_clock_domain_id**内记录，`last_record_age_ms`是在该次成功读取时已测得的年龄；因此只在该本地域内加上读取后经过时间，不把event_clock_domain_id中的源时间当成本地读取时间。未知域、负差或不能可靠表示的超大差值返回null/UNKNOWN。快照age仅在event和observed的两个非空域相等时计算。无跨域时长、先因或墙钟顺序推断；无法解析的UTC文本降null并附原因。

SOURCE_STATUS正常EVENT_DRIVEN空闲保持IDLE，producer_liveness始终UNKNOWN。同一epoch内不同mode/周期合约冲突。PERIODIC源仅在同域年龄严格大于15000ms时STALE，未证实的STALE声明降UNKNOWN。读取失败、历史GAP/UNAVAILABLE和已隔离关联记录不被恢复IDLE清除。source_seq检查仅报告批次可见的最小/最大序号之间缺口；批次可能从任意cursor开始，不声称证明首条之前完整，也不把大序号展开成巨型列表。新epoch单独去重/检查，旧epoch缺口仍保留。

指标ERROR/UNKNOWN及哨兵（-1、2^32−1、2^64−1）值降null并注明原因，哨兵原OK状态降UNKNOWN。无有效值不填0；不从设备指标推测训练健康。非法单位/范围隔离。time、metric与progress的UNKNOWN不删除已有可信历史退出事实。

## 三层状态与冲突

无法归属来源的坏帧或超限会保守降级本批已见来源和实体覆盖，已有可信历史进程退出仍保留。counts.accepted为已入槽位数（含后来隔离的冲突槽位），duplicates为同内容重读次数，invalid为隔离诊断数。

process键为job/run/attempt/scope/host/boot/namespace/pid/start，只有完整实例及worker关联链可更新；launcher可以没有rank/GPU字段，但仍需绑定attempt。部分身份事件只留来源层，不能后来用PID猜归属。成员清单与退出的完整映射必须一致，PID重用、boot/namespace/attempt变化各自隔离。NOT_OBSERVED无退出含义；旧快照不复活终止进程。

完整成员无冲突且全员可信退出时，attempt仅得ATTEMPT_EXITED_OK或ATTEMPT_EXITED_WITH_FAILURE。缺成员保持UNKNOWN但保留已知失败；终态证据引用成员退出记录，另有terminal_evidence_refs列出全部退出证据，多成员时单字段为该引用集合的派生哈希。

run键只有(job_id,run_id)。COMPLETED需独立权威run成功记录，或明确final_attempt_id/no_restart_or_resume=true且该attempt完整全员0。权威run终态不补造成员退出。互斥终态、实例/成员冲突或同源明确出现证明之后的新attempt使run UNKNOWN。跨源记录不凭到达顺序宣称重启先后。run成员计数是已知各attempt实例计数之和，不是推测的最终world_size。

相同源epoch/seq相同规范内容仅接收一次；不同内容的槽位整体隔离，输出CONFLICT_EVENT及变体哈希，关联对象UNKNOWN，不保留“第一条获胜”的规范事件。跨来源同实例同终止事实在exits摘要仅一条通知，附全部证据；互斥退出事实为UNKNOWN。输出保留到达序号，最终摘要按逻辑键排序。同一输入重复执行逐字相同；改变到达顺序会改变审计事件顺序，但完整等价证据的事实摘要一致。源序号不证明跨源因果。

## 测试和证据

[fixture manifest](../tests/fixtures/manifest.json)登记14组输入与精确期望快照的SHA-256；test_T01～test_T14分别比较完整输出对象并进行手写语义断言。期望快照初版由实现结果生成后逐类核对，不能单凭快照一致自证正确；独立断言曾识别T09输入序号冲突，失败及原输入保留。测试运行不会重生成期望文件；修改需审查输入、精确输出和独立断言。

[功能失败日志](../evidence/local-initial-tests.txt)为首次集成29项、1失败（T09），测试进程exit1；后续打印日志的cat命令exit0不代表测试PASS。原输入/期望保存 [T09初始输入](../evidence/T09-initial.jsonl) / [初始快照](../evidence/T09-initial.expected.json)。日志仅将本机绝对仓库路径替换为`<REPO>`，保留异常和断言。

契约子任务首次在fixtures尚未建立时运行发现26项，其中12项契约PASS、14项FileNotFoundError；主集成发现初版遗漏schema_version校验，修复为必需且严格0.1并加入版本断言，不能把初版契约测试PASS当完整性证明。后按模块15项PASS；子任务配置请求6Luna/Max，但无可靠运行时回读，不声称已核验。主智能体未声称切换配置。

最终测试对象commit、tree、环境、命令、退出码、数量、CI run/job/实际日志及限制由Draft PR和 [evidence记录](../evidence/README.md)登记，避免文档自引commit。功能、文档、敏感模式/范围检查分开报告。首次文档检查因两个证据目标文件尚未落盘而FAIL/exit1，原日志保存于evidence/local-initial-docs.txt；补齐目标后重新执行原命令恢复。现场/CPU实际子进程/I0～I5/实时采集/训练/GPU/开销均NOT_RUN；不能以本离线输入代替现场验收。M1-C2及后续阶段未启动，不合并本PR。
