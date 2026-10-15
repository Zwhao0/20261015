# M1-C2-A ParallelContext 0.1：合成离线 sidecar

2026-10-15（Asia/Shanghai），[Issue #13](https://github.com/Zwhao0/20261015/issues/13)。用户已明确授权 C2-A，C2-B 未授权。本协议独立使用 `context_version=0.1`；不是 C1 的 `schema_version=0.1` 扩展，不嵌入旧 JSONL，不改变旧回放/终态。来源设计见 [SOURCE_PLAN](M1_C2_SOURCE_PLAN.md)，现场门禁见 [OWNER_INPUT](M1_C2_OWNER_INPUT.md)。

## 决策与边界

| 问题 | 选项及选择依据 | 风险与验证 |
| --- | --- | --- |
| 冻结 C1 如何兼容 | 选择独立 sidecar 和独立 Python API；不扩展 C1 解析器 | C2-A 不提供自动事件连接；原52测试、源码、golden逐字保留并回归 |
| 如何表达并行 | 显式列出每个有序通信组，按 worker 实例引用；不使用维度乘积 | 不证明覆盖了所有组；合法子集不等于完整拓扑；混合/相交/非笛卡尔合成测试 |
| 有字段但没有来源 | 非 null claim 必须引用允许语义的同 attempt 合成证据；无证据用 null+理由 | 标签和哈希不是鉴权；仅检验输入一致性，不声称现场真实性 |
| epoch 与重启 | attempt 分区内显式双 epoch；同 epoch 的不同成员/拓扑全部隔离 | 不按到达顺序挑赢家、不补 latest；重建/resize 需新 epoch；冲突与重入测试 |

## API 与输入

[parallel_context.py](../observatory/parallel_context.py) 仅接收已解码 Python 对象，无 I/O、网络、时钟、进程或设备操作，不解析证据引用。`validate_context(obj)` 返回独立副本，非法输入抛 `InvalidContext`，错误仅为固定字段路径/原因；`normalize_contexts(list)` 有界校验、去重和冲突隔离，返回可用 contexts、diagnostics、批次 status 和 duplicates。不是在线 reader、真实适配器或来源鉴权器。只接受 `origin=SYNTHETIC`；给真实数据加前缀不构成授权或脱敏。

所有对象字段严格必需，额外字段拒绝；标识只允许 `SYN_` 加 ASCII 字母数字/`_.:-`（总长5～132）；整数排除 bool，范围0～2^63−1，PID/频率为正数。数组有界：批次128，成员/组/专家各256，证据64，每个引用列表最多256。上限属于离线输入保护，不是现场性能预算。输入须为有限的普通 dict/list/JSON 标量树，不含循环；验证按固定结构遍历，不运行输入对象代码。

顶层字段为 `context_version,origin,scope,membership_epoch,topology_epoch,members,groups,experts,routing,evidence`。scope 严格为 `job_id/run_id/attempt_id`；不允许仅靠 PID、rank 或 GPU 连接不同 scope。

通用 Claim 为 `{value,evidence,unknown_reason}`：

- 已知值：`value != null`，`evidence` 非空且引用本记录 evidence_id，`unknown_reason=null`。这是 SYNTHETIC_SUPPORTED 一致性证据，不是真实置信度。
- 未知值：`value=null,evidence=[],unknown_reason` 为 `NO_SOURCE/MISSING_MAPPING/EPOCH_UNKNOWN/NOT_OBSERVED/NOT_SUPPORTED/CONFLICT` 之一。不用空数组或0代替未知。
- 允许有证据空列表，语义为来源明确声明该列表为空；members/group members 本身要求非空。没有 epoch 的精确成员/组/专家拒绝，不通过猜测修补。

## 字段与证据

| 字段 | 已知 value 结构 / 约束 |
| --- | --- |
| membership_epoch | 非负整数；绑定本 attempt 的成员版本 |
| topology_epoch | 非负整数；绑定本 attempt 的组及静态专家版本，与 membership epoch 同时已知才允许具体拓扑 |
| members | worker列表：`worker_id,process,global_rank,local_rank,gpu_ids`；后四项为 Claim。成员列表需 membership epoch；worker_id 不重复，已知 global rank 不重复，完整 process 实例不重复 |
| process | `host_id,boot_id,pid_namespace_id,pid,process_start_ticks,start_ticks_hz`；缺任何字段则整个 process 为 UNKNOWN。容器/宿主不同 namespace 不用 PID 直接连接 |
| global_rank / local_rank | 非负整数，分别由来源声明；local rank 只在已知 host/boot/namespace 内校验唯一。未知 process 时不能确认本地 rank 唯一性，整体 status 为 UNKNOWN |
| gpu_ids | 合成稳定设备ID有序列表；有证据空列表可代表来源明确无GPU。缺映射为 null。设备ID不生成 rank；允许显式多GPU/共享GPU，不假定一进程一GPU |
| groups | 列表：`group_id,group_type,member_ids,membership_epoch,topology_epoch,evidence`。类型 DP/PP/TP/EP/CP/VIRTUAL_PP/EXPERT_TENSOR。成员为有序 worker_id，每个位置是 group rank，不等于 global rank；每组非空且不重复，均须在本记录 members；双 epoch 必须与顶层一致，ID只在本 scope/epoch 内唯一 |
| experts | 列表：`layer_id,expert_id,replica_id,owner_worker_ids,communication_group_ids,evidence`。三个ID组成静态专家副本键；owners是非空成员子集；communication_group_ids为可 UNKNOWN 的Claim，仅引用 EP/EXPERT_TENSOR 组，已知时 owners 必须落在所声明组成员并集内。不推断专家数量/副本/路由 |
| routing | `token_routing,expert_load` 两个 Claim，本阶段都只接受 UNKNOWN；没有获准 token 来源，不允许静态归属推算动态流量/负载或故障 |

每个 evidence 严格包含 `evidence_id,source_id,source_epoch,source_seq,kind,scope,evidence_ref,content_sha256,clock_domain_id,observed_tick`。所有标识为合成逻辑ID；SHA为64位小写十六进制，仅记录引用内容摘要，不自动读取/验证被引用内容。clock/tick 是同一合成时钟域中的观测点，不作跨机排序；无现场时钟精度结论。scope必须与顶层完全相同。相同 source_id/epoch/seq 在批次中出现不同证据内容时，相关 context 全部隔离。

| evidence kind | 允许支撑的 Claim 语义（仅模拟） |
| --- | --- |
| OWNER_MANIFEST | membership epoch / members / rank / process |
| LAUNCHER | membership epoch / members / rank / process / GPU映射 |
| SCHEDULER | membership epoch / members |
| LOCAL_PROCESS | process |
| DEVICE_MONITOR | GPU映射 |
| GROUP_MANIFEST | topology epoch / groups |
| EXPERT_MANIFEST | experts / 专家通信组引用 |
| LOG_UNVERIFIED / UNKNOWN | 不允许支撑任何精确 Claim |

证据种类不包含退出判决接口，不能凭此 sidecar 声明进程/Attempt/Run 终态。parent wait/launcher/scheduler 的现场可信性仍须 OWNER_INPUT 独立门禁。

## 缺失、冲突与隔离

UNKNOWN claim 逐项保留，规范化不填默认rank/GPU/epoch，不用数组长度推 world size。单条 status 为 SYNTHETIC_SUPPORTED 仅表示所有非 routing 字段具体且一致；routing永远未知，完整现场覆盖/真实性仍 INCONCLUSIVE。其它缺项使状态 UNKNOWN；提供 `unknown_paths` 明确所有 null 路径（含 routing）。

批次不推断时间先后，也不挑“最大epoch”为当前状态。相同规范内容只计 duplicate；证据不同的相同事实各自保留，不合并权限。相同 scope+membership epoch 的 members 结构不同，或相同 scope+topology epoch 的 membership epoch/groups/experts 不同，所有关联版本隔离。未知与具体的同 epoch 表述不同也保守隔离，不以部分来源拼成精确事实。不同 epoch 或不同 attempt 分开保存；process/worker/rank 可在新 membership epoch 中重新加入，不继承旧退出状态。group_id 重用只在明确新 topology epoch 下成立。epoch为UNKNOWN的记录无精确成员/拓扑，不连接其它记录。

隔离记录不出现在可用 `contexts` 中；diagnostics仅有固定code、输入索引及规范内容SHA，不回显非法输入。批次存在非法/冲突/任何非routing缺项时 status=UNKNOWN；否则 SYNTHETIC_SUPPORTED。下游必须检查 diagnostics，不能把空 contexts 当空任务、退出或无故障。

## 合成验证与恢复

[fixtures](../tests/fixtures/parallel_context/mixed.json) 为公开纯合成输入；[测试](../tests/test_parallel_context.py) 包含独立语义断言，不能只对实现生成的快照自证。最终环境/命令/失败恢复/fixture SHA见 [C2-A 证据](../evidence/c2-a/README.md)；精确交付HEAD/tree及对应双job CI存关联Draft PR，避免自引哈希。

```sh
python3 -m unittest tests.test_parallel_context -v
python3 -m unittest discover -s tests -v
python3 scripts/check_docs.py
git diff --check
```

本阶段只验证离线结构与合成身份一致性；真实来源、字段可得性、权限、CPU launcher、I0～I5、吞吐/CPU/RSS/I/O预算、MoE动态路由和现场适配均 NOT_RUN/INCONCLUSIVE。C2-B=BLOCKED，待所有者来源与另行授权；不能以本协议或CI替代现场证据。
