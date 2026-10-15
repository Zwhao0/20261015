# M0-2 观测能力与兼容性矩阵

2026-10-15（Asia/Shanghai）。任务：[Issue #6](https://github.com/Zwhao0/20261015/issues/6)，母 [Issue #1](https://github.com/Zwhao0/20261015/issues/1)。用户明确指令“启动 M0-2”，取代历史文档的未授权状态。本轮交付离线分析与补证条件，等待独立审核；实际信号/训练兼容性仍 `INCONCLUSIVE`，M0-Gate 未通过。

## 输入、执行与结论口径

- 分支 `codex/m0-2-capability-matrix` 初始从main 4ae0555…建立，发布前已快进至main `4d93a08d76a10ff9a52fba68b84cba2d5fc6475a`。PR #4 已合并；[PR #5](https://github.com/Zwhao0/20261015/pull/5) 启动时 Open/Ready/Unmerged（API draft=false，与旧描述不同），发布前已在GitHub合并为上述main，Codex未操作合并。
- 补证输入固定为 PR #5/head `f15050dc1c4b8bf5cd5e49d75576f19ecf7b269d` 的[18 条证据与命令](https://github.com/Zwhao0/20261015/blob/f15050dc1c4b8bf5cd5e49d75576f19ecf7b269d/docs/M0_1_INVENTORY.md)（以下称 E）。发布前最新main已包含同一完整18条，本分支本地 M0_1_INVENTORY 随快进同步，原证据未修改；保留固定快照供复现。
- [M0-1 独立审核](https://github.com/Zwhao0/20261015/pull/5#issuecomment-6188441126) 为调查交付限定 PASS，未独立验证主机原始记录。这里只重新核对公开摘要/版本和官方资料，不冒称重新访问主机。
- 首轮实际采集：16:08:10～16:12:18；容器补证：16:36:01～16:42:26，均 2026-10-15 UTC+08:00。A/B 独立采集；全部机器事实仅适用于各自历史快照，当前仍然可读与否未复测。
- 本轮 SSH、凭据读取、metrics/任务日志读取、RAS 查询、FR 触发、GPU/训练/collective、配置变更均 `NOT_RUN`。不接触旧项目，不清理容器。C1 来源仍需环境所有者确认可合法复用的通用运行时，确认前不作为开发/测试运行时。

“直接可得”仅表示指定字段在历史证据中实际成功获取；“需配置或版本支持”表示有官方支持路径但本地启用/输出未验证；“不可得”须有当前范围内明确不支持的证据；缺证据为 `UNKNOWN`。本轮没有足够证据将任何完整能力判为“不可得”。可用性与测试结果分开；未运行不是 FAIL，缺失信号不是健康。

## 版本适用范围

| 层次 | A / 独立证据 | B / 独立证据 | 可推断及限制 |
| --- | --- | --- | --- |
| 平台 | 8×H800、Driver 580.178.04，E-A-01 | 同规格/版本，E-B-01 | 字段读取成功；驱动 CUDA 声明 13.0 不等于 Runtime 或 GPU 兼容测试 |
| 候选 C1 | Python 3.12.3、Torch 2.13.0+cu130、构建 CUDA 13.0、nvcc 13.0.88，E-A-07/09 | 同版本，E-B-07/09 | CPU 导入成功、CUDA 初始化 false；不等于任何现有训练的运行时 |
| NCCL 三层 | 包/header 2.30.7；Torch API 2.29.7；本次探查进程映射库 ncclGetVersion=23007，E-A-07/09 | 同结果，E-B-07/09 | 编译版本与探查进程库分列；真实训练进程加载库 UNKNOWN；ABI/collective 兼容性 INCONCLUSIVE |
| DCGM / Exporter | core/proprietary 4.6.1、exporter 4.8.4.3955-1，E-A-03 | 同版本，E-B-03 | 官方 exporter 4.8.4 release 使用 DCGM 4.6.1 [S7]，只支持版本组合候选；发行包补丁来源、运行二进制和配置尚未核实 |

上游 PyTorch v2.13.0 的 NCCL `version()` 按编译宏组成版本值 [S4]，与 E09 的 raw/tuple 语义相符；这解释了两种版本查询可不同，不证明本地包等同上游源码或混用库安全。禁止为消除差异直接换库。RAS 的文档判断使用 2.30.7 归档 [S1/S2]；PyTorch 2.13 文档页本轮访问失败，改查官方 v2.13.0 源码 [S3/S4/S5]，没有把 2.14/stable 教程默认值套到本地包。

## 能力矩阵

| ID / 能力 | A：现场证据 | B：现场证据 | 可用性 / 版本或配置条件 | 失败降级 / 最小补证 |
| --- | --- | --- | --- | --- |
| C01 Host / GPU 身份字段 | E-A-01 的设备字段查询 exit 0；公开 A 与设备计数 | E-B-01 exit 0；公开 B 与设备计数 | 直接可得（历史设备快照）；真实 Host/UUID 仅受控使用，不公开。持久身份/重启边界 UNKNOWN | 只保留节点代号与来源时间，不将 GPU index 当永久身份；V1 核对受控设备映射 |
| C02 PID ↔ GPU UUID | E-A-04 query exit 0，8行/8 PID/8 GPU | E-B-04 query exit 0，8行/8 PID/8 GPU | 直接可得（单机瞬时关联字段）[S8]；公开仅聚合，不能重建完整映射或认定属于本项目 | 无任务归属时仅设备/进程视图；缺字段记 UNKNOWN，不把消失当退出；V1 |
| C03 Job/Run/Host/PID/Rank/Local Rank/GPU 完整关联 | E-A-02/04 未取得获准任务/launcher/Rank | E-B-02/04 同缺口，各自独立 | UNKNOWN；若采用 torchrun，上游提供 RANK/LOCAL_RANK/WORLD_SIZE/TORCHELASTIC_RUN_ID [S5]；实际 launcher 未证实，Run ID 不自动等于调度 Job ID | 不猜 Rank=GPU index，不通过裸 PID 跨容器连接；V1 提供任务来源、PID 命名空间、进程开始/重启身份、可见设备映射与启动器字段白名单 |
| C04 时间戳与跨机时钟 | E-A-02：REALTIME/MONOTONIC；01 同步报告 yes；03 tracking exit 1/506 | E-B-02/01/03 独立同结果 | API 语义直接可得 [S6]；真实事件时间源/跨机误差 UNKNOWN。同步布尔值不证明精度 | 单机持续时间仅在相同单调时钟域比较；跨机不做严格先后/延迟归因，显示误差未知；V2 |
| C05 训练进度 | E-A-02/04 无获准 step/样本数/进度事件 | E-B-02/04 同缺口 | UNKNOWN；需任务所有者提供明确 step 语义、重启边界及获准来源；GPU 利用率/PID 存活不替代训练进度 | 无样本/采集失败与“step 未变”分开；不宣告 hang/fail-slow；V3 |
| C06 DCGM / 主机 metrics | E-A-03 包已安装；02 exporter comm；04 指定 service inactive/not-found | E-B-03/02/04 各自同类线索 | UNKNOWN（当前信号）；需核实实际 exporter/hostengine、字段配置和受控端点。安装、进程和服务名结果不能替代 /metrics 样本；文档支持路径 [S7/S9] | 不把空输出、权限拒绝、哨兵/错误值当 0；保留基础历史设备事实；V4 |
| C07 已有日志 / 异常退出来源 | E-A-02/04 未读任务私有日志/启动器退出事件 | E-B-02/04 同缺口 | UNKNOWN；需明确获准任务的 launcher/结构化日志来源、时区、轮转/完整性与退出码语义 | 日志缺失不等于无错误；轮转/权限/进程退出未知分别报告；不读取旧项目；V3 |
| C08 NCCL RAS | E-A-09 探查库 2.30.7；无 communicator/RAS 信号 | E-B-09 独立同结果 | 需配置或版本支持（文档路径）；实际任务 UNKNOWN。RAS 自 2.24；默认 enabled 但随 NCCL 初始化启动 [S1/S2]，CPU import 不证明其运行 | 未连接/无权限/超时均 UNKNOWN，不当作 NCCL 故障；无 RAS 时保留基础身份事实；V5 |
| C09 PyTorch Flight Recorder | E-A-07/09 Torch 2.13.0+cu130；无 PG/缓冲/导出证据 | E-B-07/09 独立同结果 | 需配置或版本支持（上游 v2.13.0 有相关实现 [S3]）；本地构建、配置及有效输出 UNKNOWN。不能靠 CPU 导入证明 FR | 没有 dump 不证明无异常；FR 为可选增强，基础观测降级继续；V6 |

C01/C02 的“直接可得”不延伸到 C03。C08/C09 的文档支持不延伸为 A/B 训练信号 PASS。所有 V 项均为后续补证条件，本轮 `NOT_RUN`；本表不选择 M0-3 切片或定义其完整数据契约。

## 关键兼容性边界与补证条件

| 验证项 | 需要的对象/条件与最小方法（尚未执行） | 通过证据 / 失败处理 |
| --- | --- | --- |
| V1 身份 | 任务所有者明确一个本项目可读任务；按白名单提供 Job/Run、launcher、Rank/Local Rank、重启次数、Host 与容器/宿主 PID 对应、实际可见 GPU；受控比对同一采集窗口 | A/B 各自形成可追溯链并解释重启/PID 重用；缺任一链接保留局部字段与 UNKNOWN；不扫描全量 env/args |
| V2 时间 | 管理员提供 A/B 同一窗口的实际同步源、偏差/误差界和事件时间源说明；允许时只读查询获准时钟接口，不调时 | 能标出采集时间/事件时间、时区、时钟域、误差来源/适用窗口；无误差界不声称跨机排序精度；不预设验收阈值 |
| V3 进度/日志 | 所有者提供明确获准的最少日志/事件字段样本，含 step 定义、Run/重启边界、源时间/接收时间、成功/异常退出来源 | 能解释缺样、轮转、重启与实际 step 更新；只读最小样本并脱敏，不读模型/数据/旧项目。无法取得即 UNKNOWN |
| V4 metrics | 管理员确认现有 exporter 来源、配置、字段白名单和目标端点后，批准一次限时/限量读取；不枚举端口、不启动 hostengine/profiling | A/B 分别有可解析样本、字段单位/错误状态、受控 GPU 关联、采集时间和新鲜度信息；无来源或身份链则仅主机级，失败不记零 |
| V5 RAS | 先确认目标任务实际加载 NCCL、已启用 RAS、所属任务/容器网络命名空间与专属受控地址；单独授权后才限时查询状态 | 仅解析实际版本支持的输出与 communicator 局部 Rank；缺失/超时 UNKNOWN。2.30.7 文档提供 JSON（自 2.28.7）[S1]，解析格式仍须以实际版本样本验证 |
| V6 FR | 所有者确认合法通用运行时与本地 PyTorch 构建；逐项核对缓冲、导出机制/写入位置、容量、Rank 关联；只对另行批准的隔离测试任务验证，不能注入现有任务 | 获得受控、版本可识别、逐 Rank 可关联的输出，说明截断/丢失；导出/解析失败保留原因。启用或触发均另需授权，不以故障注入取样 |
| V7 运行库兼容 | 所有者确认运行时来源；另行批准有资源/超时/退出边界的最小 GPU/双机测试方案，核实测试进程实际库，不继承任意现有训练 | 在单独实施任务记录真实 GPU/collective 结果；本轮只保留 NCCL 差异，不升级环境，也不把任一测试推广到全部拓扑/训练 |

RAS 默认监听 localhost:28028；共享节点可能有多作业，文档建议不同地址区分 [S2]。容器与宿主 localhost 不必相同；默认端口不能视为获准任务端点。RAS 涉及后台线程/网络查询，不作为本轮离线核验命令。输出中的 communicator Rank 不自动等于训练全局 Rank；collective 计数不等于 optimizer step，单次不一致也不直接定性为故障 [S1]。

FR 的缓冲收集、计时、超时导出和监控线程是不同开关。上游 v2.13.0 头文件注释将超时 dump 与 monitoring、正值 trace buffer 关联，并说明 monitoring 可能终止进程 [S3]；因此不向现有任务推荐直接粘贴环境变量。具体默认值、导出变量/格式、开销和本地补丁仍需 V6 验证。未主动调用私有 API、写 pipe 或信号触发 dump。

## 决策与风险

| 问题 | 选择与依据 | 风险 / 验证 |
| --- | --- | --- |
| 是否以缺少真实训练阻塞全部矩阵 | 先交付已有证据范围的矩阵与 V1～V7，完整能力保留 UNKNOWN；Issue #1 允许未知，不要求本轮新训练 | 文档完整不代表部署就绪；独立审核逐行核对 E 与 S 引用 |
| 发布期间main发生变化 | PR #5启动时未合并，先固定SHA；发布前发现已合并，保存草稿、快进main并整合M0-2入口 | 最终diff只含M0-2，原18条证据保持不变；核对父提交/tree，不强推或操作GitHub合并 |
| 版本不同如何处理 | 分列编译 API、探查库、真实任务未知，用对应版本上游资料判断候选支持 | 版本号不能证明本地构建一致或 GPU 兼容；V6/V7，失败不换库掩盖 |
| 最小依赖范围 | 不新增训练/观测实现、依赖、服务器变更或测试脚架 | 不产生新现场证据；本轮只验证文档和公开证据完整性，恢复可用后续修正文档/revert |

## 资料核验（2026-10-15）

仅参考官方文档与上游源码，未复制外部实现或安装依赖；项目许可证未指定。NCCL 文档遵循 NVIDIA 文档条款；PyTorch 上游为 BSD-style、DCGM Exporter 为 Apache-2.0，具体以各链接版本的 LICENSE 为准。本轮适用范围是事实解释/兼容性候选分析。

- S1：[NCCL 2.30.7 RAS](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2307/user-guide/docs/troubleshooting/ras.html)：初始化、状态查询及输出语义；未采用更新版本才有的诊断指令。
- S2：[NCCL 2.30.7 环境变量](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2307/user-guide/docs/env.html#nccl-ras-enable)：RAS 开关、监听地址和共享作业边界。
- S3：[PyTorch v2.13.0 ProcessGroupNCCL.hpp](https://github.com/pytorch/pytorch/blob/v2.13.0/torch/csrc/distributed/c10d/ProcessGroupNCCL.hpp)、[ProcessGroupNCCL.cpp](https://github.com/pytorch/pytorch/blob/v2.13.0/torch/csrc/distributed/c10d/ProcessGroupNCCL.cpp)：FR/monitoring 开关和 dump 路径；[LICENSE](https://github.com/pytorch/pytorch/blob/v2.13.0/LICENSE)。上游标签不是本地二进制来源证明。
- S4：[PyTorch v2.13.0 nccl.cpp](https://github.com/pytorch/pytorch/blob/v2.13.0/torch/csrc/cuda/nccl.cpp)：`version()` 编译宏语义。
- S5：[PyTorch v2.13.0 torchrun](https://github.com/pytorch/pytorch/blob/v2.13.0/torch/distributed/run.py)：launcher 身份字段和弹性重启行为；不假定实际任务使用此 launcher。
- S6：[Python 3.12 time](https://docs.python.org/3.12/library/time.html)：墙钟可调整、单调时间只在对应时钟域比较；文档补丁版不替代本地 3.12.3 实测。
- S7：[DCGM Exporter 4.8.4 release](https://github.com/NVIDIA/dcgm-exporter/releases/tag/4.8.4)：发布组合 DCGM 4.6.1；[LICENSE](https://github.com/NVIDIA/dcgm-exporter/blob/4.8.4/LICENSE)。不等同现场包/进程来源证明。
- S8：[NVIDIA System Management Interface](https://docs.nvidia.com/deploy/nvidia-smi/index.html)：设备/compute-app 查询接口；滚动文档不替代 E01/E04 的实际字段/权限证据。
- S9：[DCGM Exporter 官方仓库](https://github.com/NVIDIA/dcgm-exporter)：metrics 与配置入口；滚动文档仅作来源导航，不据此断言本机字段支持。

资料查询失败亦保留：最初错误的 NCCL `/docs/ras.html` 路径访问失败，后改为 2.30.7 `/docs/troubleshooting/ras.html` 成功；PyTorch 2.13 两个文档页访问失败（工具报告 inaccessible，未取得 HTTP 码），改查 v2.13.0 官方标签源码成功；未将访问失败解释为功能不支持。旧 prototype FR / DCGM 导航页内容不足、FlightRecorderDetail.cpp 与 DCGM configuration 候选路径未成功读取，均未作为结论来源。工具失败不等于远端 HTTP 404。

## 验证记录

本轮只做文档分析。执行命令、环境、退出码、公开摘要复核与人工审查结果见 [STATUS](STATUS.md)；最终交付 SHA/tree、CI run/job/log 与 Draft 状态由本任务 PR 描述保存，避免文档循环引用自身提交。公开摘要一致性不证明原始证据真实性；没有重新登录 A/B。独立审核尚未执行，M0-3/M1 未授权。

公开摘要复核（仓库根目录，标准库；本轮实际运行同等逻辑，exit 0）：

```sh
python3 - <<'PY'
import hashlib, json, re, subprocess

def read(ref):
    report = subprocess.check_output(
        ['git', 'show', ref + ':docs/M0_1_INVENTORY.md'], text=True)
    index = dict(re.findall(
        r'\| (E-[AB]-0[1-9]) \|[^\n]*`([0-9a-f]{64})`', report))
    result = {}
    for block in re.findall(r'```json\n([^\n]+)\n```', report):
        data = json.loads(block)
        key = data['id']
        assert key not in result
        canonical = json.dumps(data, ensure_ascii=False,
                               sort_keys=True, separators=(',', ':')) + '\n'
        assert hashlib.sha256(canonical.encode()).hexdigest() == index[key]
        result[key] = (block, index[key])
    assert len(result) == len(index)
    return result

full = read('f15050dc1c4b8bf5cd5e49d75576f19ecf7b269d')
old = read('4ae0555c6fca24a6082e8e6af4ac40f107cb6716')
assert len(full) == 18 and len(old) == 8
assert all(full[k] == v for k, v in old.items())
print('PASS: 18 hashes; original 8 byte/hash pairs unchanged')
PY
```
