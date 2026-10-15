# M0-1 只读环境调查

依据：[Issue #3](https://github.com/Zwhao0/20261015/issues/3)。起点 main `41a30e011b3fb0074aaef7cb8c42070aef4562b1`，分支 `codex/m0-1-inventory`。只调查环境事实，不进入 M0-2/M0-3/M1。

## 访问门禁与采集前方案

2026-10-15（Asia/Shanghai），用户在当前会话明确启动 M0-1，并授权访问指定的仓库外 `服务器.md` 所列服务器。该文件仅在本地读取、解析，不进入公开仓库；A/B 仅为本次调查代号，不由真实身份计算。用户授予的权限在本任务中收敛为只读调查，不使用变更权限、不申请新权限。不接触旧项目代码、配置、日志或构建物，不读取第三方任务私有材料。

原始证据在本机授权工作区的 Git 忽略目录中保存，目录权限 0700、文件 0600；公开仅发布人工审查过的字段白名单摘要及其 SHA-256。原始索引位置仅私下交接。SSH 使用指定目标、禁用转发、限制连接/命令超时；首次主机密钥使用本地隔离 known_hosts 保存（TOFU，未获带外指纹验证），密钥变化即停止，不绕过校验。不创建 SSH 凭据；密码不放命令行、环境变量、输出或 Git。

每条命令单次、有超时、限制输出。先做平台清单，再按实际发现决定是否继续训练栈及观测来源调查。权限不足、目标不明、超时、意外敏感输出或需额外负载时停止对应项，记录退出码与 UNKNOWN。读取操作可能产生 SSH 审计记录和短暂 CPU 开销；不承诺主机绝对零写入。

| 组 | 命令/读取方式（执行前计划） | 目的及敏感字段 | 影响、失败判定及脱敏 |
| --- | --- | --- | --- |
| P1 | `date -u`、`uname -srm`、OS release 的 NAME/VERSION_ID、`nproc`、内存总量 | 平台版本；不取 hostname、机器 ID | 单次 CPU 读取；非零/超时逐项记失败，不外推 |
| P2 | `nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader`；有界 `nvidia-smi` 摘取 CUDA 声明 | GPU 数量/型号/驱动/显存；区分驱动宣称 CUDA 与运行时 | 不分配 GPU、不取 UUID/Serial；仅保留版本字段，不能作为 GPU 功能验收 |
| P3 | `systemd-detect-virt --container`、已知工具 `command -v`（仅记录存在性） | 当前登录命名空间/工具线索；路径留私密 | 不调用容器 exec、不枚举容器内部；非零不等同工具未安装 |
| S1 | 已有 Python `--version`；标准库 `importlib.metadata` 读取已知包版本；已知 Toolkit 的 `nvcc --version` | Python、Torch、框架、CUDA Toolkit/NCCL 包元数据 | 不导入 Torch、不初始化 CUDA；路径隐藏；包元数据不等于实际运行/加载版本 |
| S2 | 仅有已授权的当前任务来源后，读限定版本常量/已知运行元数据 | 区分 Torch 构建 CUDA/NCCL 与进程已加载 NCCL | 不读旧项目、不连接 NCCL、不 attach/profiler；证据不足 UNKNOWN，不为补证跑训练 |
| R1 | 进程 comm/类别计数（不取完整 args/env）；若有明确归属与授权，再读限定 Rank 字段 | 运行方式、Job/Run/PID/Rank/GPU 映射来源 | 不枚举私有数据、不公开 PID/作业名；第三方归属不明时不读环境/日志 |
| O1 | 已知观测工具存在性/包元数据/进程 comm 分类；已获许可的既有信号源 | 区分已安装、已配置、当前产信号 | 不启动服务、不探测端口、不访问 metrics/RAS/profiler，不以二进制存在证明信号 |
| T1 | `date -u`、`timedatectl show -p Timezone -p NTPSynchronized -p NTP`、`time.get_clock_info` | 时区/同步线索、墙钟/单调时钟语义 | 不改配置、不公开 NTP 对端；读取时间不证明跨机误差阈值 |

OBSERVED = 本次实际直接读取；REPORTED = 用户/元数据间接声明；UNKNOWN = 无足够事实；NOT_RUN = 未执行；INCONCLUSIVE = 已尝试但不能判定。执行结果另用 PASS/FAIL/NOT_RUN/INCONCLUSIVE，连接成功不等于全部调查 PASS。

## 首轮宿主机快照：结果、作用域与限制

实际采集窗口：2026-10-15 **16:08:10～16:12:18 Asia/Shanghai（UTC+08:00）**；逐条精确 UTC 起止时间见下表/摘要。A/B 各四个独立远程会话，SSH 均 exit 0；子命令失败单独保留，不能把 SSH 成功当作调查全通过。以上为首轮宿主机快照；后续新增授权的容器补证单列于文末，不覆盖此窗口。

- **OBSERVED / PASS（限定平台事实）**：A/B 均为 8×NVIDIA H800，驱动 580.178.04，单卡查询显存 81559 MiB，Ubuntu 24.04，192 个在线逻辑 CPU。内核 A = 6.8.0-146-generic，B = 6.8.0-139-generic。各自证据 E-A-01/E-B-01；没有 GPU 计算测试。
- **OBSERVED（当前登录命名空间）**：`systemd-detect-virt --container` 返回 `none` / exit 1；未见两个标准容器标记，Docker/容器运行进程存在（01/02）。这支持宿主机视图线索，不能证明所有任务的隔离方式。
- **OBSERVED / UNKNOWN（软件作用域）**：两台默认 Python 3.12.3；Torch、NCCL/CUDA Runtime 的指定 Python 包及列明的框架元数据未在该解释器发现，`torchrun` / `nvcc` / `srun` / `mpirun` 不在当前 PATH；已知默认 Toolkit 位置无标记（01/02）。不代表整机或容器未安装。驱动声明 CUDA 13.0，**实际 CUDA Runtime、Toolkit、Torch 构建版本/所用 NCCL、训练进程已加载 NCCL 及训练框架/启动器版本均 UNKNOWN**。
- **OBSERVED（现有组件）**：A/B 独立读到 DCGM core/proprietary 包 `1:4.6.1-1`、exporter 包 `4.8.4.3955-1`，Docker client `29.1.3`，系统 docker.io 包 `29.1.3-0ubuntu3~24.04.2`，容器 Toolkit 包 `1.20.1-1`（02/03/04）。这是安装元数据，不保证实际进程二进制来自同一包，更不等于可采集指标。
- **OBSERVED / INCONCLUSIVE（服务与来源）**：两台均看到 comm 为 dcgm-exporter、node_exporter、dockerd、containerd 的进程；03 的 DCGM 包查询成功。04 中精确命名的 `nvidia-dcgm.service` loaded/inactive；`dcgm-exporter.service`、`prometheus-node-exporter.service` not-found。不能把某个 unit 名 not-found 推断为 exporter 没运行；启动来源、容器归属、配置和实际 metrics 信号 UNKNOWN，未查端点。
- **OBSERVED（瞬时设备关联）**：02 时 A 的 compute-app 行数 0，B 为 8；04 时各有 8 行、8 个不同 PID、8 个不同 GPU UUID，实际值均在内存中聚合后丢弃。仅证明该次可读 PID/GPU 关联字段，不证明训练任务性质、数据归属或 Job/Run/Rank/Local Rank 映射。Python comm 计数包含调查进程；不以 comm 断言训练。
- **UNKNOWN / NOT_RUN（训练证据）**：没有识别到明确属于本项目且获准读取内容的真实训练任务/容器/日志。Job、Run、Rank、Local Rank、启动命令、分布式配置、训练日志/进度与时间戳格式均未知；未读任何进程完整 args/env、任务数据或旧项目文件，也未启动训练来补证。
- **OBSERVED / INCONCLUSIVE（时间）**：A/B 时区 Etc/UTC、NTP=yes、NTPSynchronized=yes（01），chrony 包 `4.5-1ubuntu4.2`（04）；`chronyc tracking` 失败（03）。Python time 为 CLOCK_REALTIME（可调整、非单调），monotonic/perf_counter 为 CLOCK_MONOTONIC（02）。这是宿主机时钟 API/报告状态，不代表训练事件时钟、不证明跨机误差阈值，不比较两次非同时查询来推断同步精度。
- **UNKNOWN / NOT_RUN（API/版本兼容）**：未导入 Torch、初始化 CUDA、调用 NCCL/RAS、启动 profiler/Flight Recorder 或探测 metrics。NCCL RAS 与 Flight Recorder 是否安装/配置/产出信号均 UNKNOWN。M0-2 的能力矩阵不在本次填写。

## 失败、未执行与恢复

| 编号 | 节点/证据 | 命令、退出码、脱敏症状 | 结论与恢复条件 |
| --- | --- | --- | --- |
| F-Docker | A/B，02/03 | `docker ps --format '{{.State}}'`，exit 1，permission denied | 容器清单与内部版本访问 BLOCKED；不提权、不改 socket 权限/用户组。后续由管理员提供批准的容器/解释器元数据或确认既有只读访问方式；不自行重试变更 |
| F-Chrony | A/B，02/03 | `chronyc tracking`，exit 1；03 捕获 `506 Cannot talk to daemon` | 详细同步偏差 UNKNOWN，不以该错误断言未同步。后续可由管理员提供跟踪状态；不改服务/时钟 |
| F-Packages | A/B，02/04 | 合并模式 dpkg 查询 exit 1；04 提示未匹配 prometheus-node-exporter | 02 因未匹配模式而整体非零，已返回的 installed 行只证明这些包；03 单独查 DCGM core/exporter 均 exit 0。缺少包名不等于不存在手动安装/容器版本 |
| I-Container | A/B，01 | `systemd-detect-virt --container` exit 1、输出 none | 工具的否定检测结果，记为 OBSERVED 线索，不按远程连接失败处理 |
| B-Workload | A/B，02/04 | 未获明确任务归属；内容读取 NOT_RUN，无退出码 | 不追踪现有 GPU 进程，不读旧项目/第三方数据；后续需本项目任务所有者提供可读任务、入口与允许字段，无需新建训练来完成本次 |
| B-Publish | 本地 | 首次 GitHub 工具 not available；`GIT_TERMINAL_PROMPT=0 git push --dry-run origin HEAD` exit 128，缺少用户名凭据 | 连接工具随后恢复；使用 Git data 接口发布，非强推。终端凭据仍未配置；远端精确 head/CI 以 Draft PR 描述为准 |

02 仅保留子命令 stderr 是否存在，未保留其文本；03 是另一次有时间戳的最小诊断复采，不冒称恢复了 02 的原始 stderr。04 的包查询未匹配症状有实际保留。调查没有配置/安装变更或需要服务器回退的部署；停止 SSH 即停止调查。仓库文档如需撤销，走审核后的 revert，不覆盖历史。

## 真实证据索引

全部作用范围为本次指定节点当前登录环境；执行=True。表中 exit 为远程 SSH/脚本退出码，**不覆盖摘要内各子命令退出码**。受控原始材料按逻辑编号 `LOCAL/<证据ID>` 私下定位，不公开实际路径；其中包含准确执行代码、时间、返回输出与失败文本。摘要并非主机签名证明，独立审核可要求受控复核或新采集，不从公开仓库获取凭据。

摘要哈希 = UTF-8 `json.dumps(summary, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n'` 的 SHA-256；下方每个 JSON 代码块就是参与哈希的单行摘要。仅对脱敏摘要做公开哈希，不对低熵身份/密码做哈希发布。原始材料、本地连接解析器、密码、known_hosts 均未提交。对应 Git commit/PR：首个调查提交 `e0527e67810916042b5c31d2d5bd125fa6a8388e` / [Draft PR #4](https://github.com/Zwhao0/20261015/pull/4)；避免文档自引自身 SHA，后续交接提交精确值以 PR 描述为准。

| ID | 节点 | 2026-10-15 UTC 开始～结束 | 命令组 / exit | 摘要 SHA-256 |
| --- | --- | --- | --- | --- |
| E-A-01 | A | 08:08:10.748236～08:08:13.522328 | P / 0 | `df7af16d70492c200f3fb5755b81d6f915f7f4312ff43f1d5c378f9757178c1c` |
| E-A-02 | A | 08:09:52.039415～08:09:53.296627 | S / 0 | `6b27d88e31a480aab6519ead172eebbdad73258f5ff8fa826ea2305f2a5525ee` |
| E-A-03 | A | 08:11:15.849573～08:11:16.767878 | F / 0 | `1e67f7e4ab1c1402194a897e1f0873c5781d02541da65cb25fda21522ea726df` |
| E-A-04 | A | 08:12:08.150529～08:12:08.929564 | O / 0 | `6651a3c2b13c28f76c669d3369a0d175d580bbbfa4071d6166946f175d12b862` |
| E-B-01 | B | 08:08:30.352839～08:08:32.133781 | P / 0 | `f276fcdb8710a0cec422c074e9e947408ef5ea829eb95574c2879fa7435e56da` |
| E-B-02 | B | 08:10:20.739842～08:10:22.157681 | S / 0 | `6aaf448042a1bca390fed5aa792b5275f4cfb69aa5515e16e031cb737af8e23b` |
| E-B-03 | B | 08:11:37.615188～08:11:38.268657 | F / 0 | `efdf8d07bdc105ade4f9e6ebac4012bf94d9ab291abb62a70d26a4ea4cd553de` |
| E-B-04 | B | 08:12:17.299618～08:12:18.077387 | O / 0 | `52df8459bc57a655161a2de881f3ab8e7fc502eab88502a5de7d02a9de6cef74` |

### 执行命令精确定义

所有命令均已在对应 A/B 执行；不因记录在这里而重复执行。P 为 shell 原文；S/F/O 均使用已有 `python3 -B -c <该组代码>`，`LC_ALL=C`，没有上传脚本到服务器。每次 SSH 本地总超时 45 秒、连接超时 10 秒、仅一次密码提示；S/F/O 每个子进程超时 6 秒。P 由总超时约束。SSH 参数与目标/凭据解析保留本地，公开不含连接身份。P 的 nvidia-smi 只摘取前四行版本头，未读取完整进程表。下面代码的标准系统路径不是内部项目路径。

<details>
<summary>P：平台、当前 PATH 与时间报告</summary>

```sh
export LC_ALL=C
probe() { label="$1"; shift; printf '\nBEGIN %s\n' "$label"; "$@"; code=$?; printf 'END %s RC=%s\n' "$label" "$code"; }
probe utc date -u '+%Y-%m-%dT%H:%M:%SZ'
probe kernel uname -srm
probe os sh -c '. /etc/os-release; printf "NAME=%s\nVERSION_ID=%s\n" "$NAME" "$VERSION_ID"'
probe cpu_count getconf _NPROCESSORS_ONLN
probe memory sh -c 'awk "/^MemTotal:/{print}" /proc/meminfo'
probe gpu nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
probe driver_cuda sh -c 'nvidia-smi | sed -n "1,4p"'
probe container systemd-detect-virt --container
probe python python3 -B --version
probe tools sh -c 'for name in python python3 nvcc nvidia-smi dcgmi nv-hostengine dcgm-exporter docker podman srun torchrun mpirun chronyc timedatectl; do if command -v "$name" >/dev/null 2>&1; then printf "%s=PRESENT\n" "$name"; else printf "%s=NOT_ON_PATH\n" "$name"; fi; done'
probe time timedatectl show -p Timezone -p NTPSynchronized -p NTP
```

</details>

<details>
<summary>S：当前解释器包元数据、comm 类别与基础来源（不导入 Torch）</summary>

```python
import importlib.metadata as md, importlib.util, json, os, pathlib, platform, subprocess, time, collections, ast
print('python_runtime='+platform.python_version())
packages=['torch','nvidia-nccl-cu11','nvidia-nccl-cu12','nvidia-nccl-cu13','nvidia-cuda-runtime-cu11','nvidia-cuda-runtime-cu12','nvidia-cuda-runtime-cu13','deepspeed','transformers','accelerate','lightning','pytorch-lightning','megatron-core']
for name in packages:
 try:
  d=md.distribution(name); print('package.'+name+'='+d.version)
  if name=='torch':
   p=d.locate_file('torch/version.py')
   if p.is_file():
    for node in ast.parse(p.read_text()).body:
     if isinstance(node,(ast.Assign,ast.AnnAssign)):
      targets=node.targets if isinstance(node,ast.Assign) else [node.target]
      for target in targets:
       if isinstance(target,ast.Name) and target.id in ['__version__','cuda','hip']:
        try: print('torch.version.'+target.id+'='+str(ast.literal_eval(node.value)))
        except Exception: print('torch.version.'+target.id+'=UNKNOWN')
 except md.PackageNotFoundError: print('package.'+name+'=NOT_IN_ACTIVE_PYTHON_METADATA')
for name in ['time','monotonic','perf_counter']:
 c=time.get_clock_info(name);print('clock.'+name+'='+json.dumps({'implementation':c.implementation,'monotonic':c.monotonic,'adjustable':c.adjustable,'resolution':c.resolution},sort_keys=True))
allowed={'python','python3','python3.12','torchrun','srun','slurmstepd','mpirun','orted','prted','nv-hostengine','dcgm-exporter','prometheus','node_exporter','chronyd','dockerd','containerd'}
counts=collections.Counter();unreadable=0
for p in pathlib.Path('/proc').glob('[0-9]*/comm'):
 try:
  name=p.read_text().strip()
  if name in allowed: counts[name]+=1
 except (OSError,PermissionError):unreadable+=1
print('process_comm_counts='+json.dumps(dict(sorted(counts.items()))))
print('process_comm_unreadable='+str(unreadable))
commands=[
 ('dpkg_stack',['dpkg-query','-W','-f=${binary:Package}\t${Version}\t${db:Status-Status}\n','libnccl*','cuda-cudart*','cuda-toolkit*','datacenter-gpu-manager*','*dcgm*']),
 ('docker_client',['docker','--version']),
 ('docker_running_count',['docker','ps','--format','{{.State}}']),
 ('gpu_compute_apps',['nvidia-smi','--query-compute-apps=pid,used_gpu_memory','--format=csv,noheader']),
 ('chrony_tracking',['chronyc','tracking']),
]
for label,args in commands:
 try:
  r=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=6,text=True)
  out=r.stdout;err=r.stderr
  if label=='docker_running_count':out=json.dumps({'running_entries':len(out.splitlines())}) if r.returncode==0 else 'UNKNOWN'
  if label=='gpu_compute_apps':out=json.dumps({'compute_app_rows':len(out.splitlines())}) if r.returncode==0 else 'UNKNOWN'
  if label=='chrony_tracking':
   fields=('Stratum','Ref time','System time','Last offset','RMS offset','Frequency','Residual freq','Skew','Root delay','Root dispersion','Update interval','Leap status')
   out='\n'.join(l for l in out.splitlines() if l.split(':')[0].strip() in fields)
  print('probe.'+label+'='+json.dumps({'exit_code':r.returncode,'stdout':out,'stderr_present':bool(err)},sort_keys=True))
  # This first pass records stderr presence only; F records later diagnostic text.
 except subprocess.TimeoutExpired: print('probe.'+label+'='+json.dumps({'exit_code':124,'status':'TIMEOUT'}))
 except FileNotFoundError: print('probe.'+label+'='+json.dumps({'exit_code':127,'status':'NOT_ON_PATH'}))
for path in ['/usr/local/cuda/bin/nvcc','/usr/local/cuda/version.json','/.dockerenv','/run/.containerenv']:
 print('known_marker.'+path+'='+str(pathlib.Path(path).exists()))
```

</details>

<details>
<summary>F：仅复采失败症状与两个包的独立退出码</summary>

```python
import subprocess,json
commands=[
 ('docker_access',['docker','ps','--format','{{.State}}']),
 ('chrony_tracking',['chronyc','tracking']),
 ('dcgm_core_package',['dpkg-query','-W','-f=${binary:Package}\t${Version}\t${db:Status-Status}\n','datacenter-gpu-manager-4-core']),
 ('dcgm_exporter_package',['dpkg-query','-W','-f=${binary:Package}\t${Version}\t${db:Status-Status}\n','datacenter-gpu-manager-exporter']),
]
for label,args in commands:
 try:
  r=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=6,text=True)
  out=r.stdout
  if label=='docker_access' and r.returncode==0:out='running_entries='+str(len(out.splitlines()))
  if label=='chrony_tracking' and r.returncode==0:out='\n'.join(l for l in out.splitlines() if not l.startswith('Reference ID'))
  print(json.dumps({'probe':label,'exit_code':r.returncode,'stdout':out,'stderr':r.stderr}))
 except subprocess.TimeoutExpired: print(json.dumps({'probe':label,'exit_code':124,'symptom':'TIMEOUT'}))
 except FileNotFoundError: print(json.dumps({'probe':label,'exit_code':127,'symptom':'NOT_ON_PATH'}))
```

</details>

<details>
<summary>O：瞬时关联字段聚合、包版本与指定 unit 状态</summary>

```python
import subprocess,json,collections
commands=[
 ('gpu_pid_mapping',['nvidia-smi','--query-compute-apps=pid,gpu_uuid','--format=csv,noheader']),
 ('host_packages',['dpkg-query','-W','-f=${binary:Package}\t${Version}\t${db:Status-Status}\n','chrony','docker.io','prometheus-node-exporter','nvidia-container-toolkit']),
 ('exporter_service',['systemctl','show','dcgm-exporter.service','-p','LoadState','-p','ActiveState','-p','SubState']),
 ('dcgm_service',['systemctl','show','nvidia-dcgm.service','-p','LoadState','-p','ActiveState','-p','SubState']),
 ('node_metrics_service',['systemctl','show','prometheus-node-exporter.service','-p','LoadState','-p','ActiveState','-p','SubState']),
]
for label,args in commands:
 try:
  r=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=6,text=True)
  out=r.stdout
  if label=='gpu_pid_mapping':
   # PID/UUID pairs are reduced in memory. Values never enter captured output.
   pairs=[tuple(v.strip() for v in line.split(',')) for line in out.splitlines() if line.strip()]
   out=json.dumps({'rows':len(pairs),'distinct_pids':len({p[0] for p in pairs}),'distinct_gpu_uuids':len({p[1] for p in pairs if len(p)==2})}) if r.returncode==0 else 'UNKNOWN'
  print(json.dumps({'probe':label,'exit_code':r.returncode,'stdout':out,'stderr':r.stderr}))
 except subprocess.TimeoutExpired: print(json.dumps({'probe':label,'exit_code':124,'symptom':'TIMEOUT'}))
 except FileNotFoundError: print(json.dumps({'probe':label,'exit_code':127,'symptom':'NOT_ON_PATH'}))
```

</details>

### 可复核脱敏摘要

以下为记录式证据，不是待执行脚本；代码注释的一处澄清不改变实际命令行为。S 首轮 stderr 的限制见失败记录。

<details>
<summary>E-A-01 / P</summary>

```json
{"command_group":"P","end_utc":"2026-10-15T08:08:13.522328+00:00","executed":true,"id":"E-A-01","node":"A","probes":{"container":{"exit_code":1,"value":"none"},"cpu_count":{"exit_code":0,"value":"192"},"driver_cuda":{"exit_code":0,"value":"driver_advertised_cuda=13.0"},"gpu":{"exit_code":0,"value":{"count":8,"rows":["NVIDIA H800, 580.178.04, 81559 MiB"]}},"kernel":{"exit_code":0,"value":"Linux 6.8.0-146-generic x86_64"},"memory":{"exit_code":0,"value":"MemTotal:       1056430708 kB"},"os":{"exit_code":0,"value":"NAME=Ubuntu\nVERSION_ID=24.04"},"python":{"exit_code":0,"value":"Python 3.12.3"},"time":{"exit_code":0,"value":"Timezone=Etc/UTC\nNTP=yes\nNTPSynchronized=yes"},"tools":{"exit_code":0,"value":"python=NOT_ON_PATH\npython3=PRESENT\nnvcc=NOT_ON_PATH\nnvidia-smi=PRESENT\ndcgmi=PRESENT\nnv-hostengine=PRESENT\ndcgm-exporter=PRESENT\ndocker=PRESENT\npodman=NOT_ON_PATH\nsrun=NOT_ON_PATH\ntorchrun=NOT_ON_PATH\nmpirun=NOT_ON_PATH\nchronyc=PRESENT\ntimedatectl=PRESENT"},"utc":{"exit_code":0,"value":"2026-10-15T08:08:12Z"}},"scope":"login host namespace; no workload/container content","ssh_exit_code":0,"start_utc":"2026-10-15T08:08:10.748236+00:00"}
```

</details>

<details>
<summary>E-A-02 / S</summary>

```json
{"command_group":"S","end_utc":"2026-10-15T08:09:53.296627+00:00","executed":true,"fields":{"clock.monotonic":{"adjustable":false,"implementation":"clock_gettime(CLOCK_MONOTONIC)","monotonic":true,"resolution":1e-09},"clock.perf_counter":{"adjustable":false,"implementation":"clock_gettime(CLOCK_MONOTONIC)","monotonic":true,"resolution":1e-09},"clock.time":{"adjustable":true,"implementation":"clock_gettime(CLOCK_REALTIME)","monotonic":false,"resolution":1e-09},"known_marker./.dockerenv":"False","known_marker./run/.containerenv":"False","known_marker./usr/local/cuda/bin/nvcc":"False","known_marker./usr/local/cuda/version.json":"False","package.accelerate":"NOT_IN_ACTIVE_PYTHON_METADATA","package.deepspeed":"NOT_IN_ACTIVE_PYTHON_METADATA","package.lightning":"NOT_IN_ACTIVE_PYTHON_METADATA","package.megatron-core":"NOT_IN_ACTIVE_PYTHON_METADATA","package.nvidia-cuda-runtime-cu11":"NOT_IN_ACTIVE_PYTHON_METADATA","package.nvidia-cuda-runtime-cu12":"NOT_IN_ACTIVE_PYTHON_METADATA","package.nvidia-cuda-runtime-cu13":"NOT_IN_ACTIVE_PYTHON_METADATA","package.nvidia-nccl-cu11":"NOT_IN_ACTIVE_PYTHON_METADATA","package.nvidia-nccl-cu12":"NOT_IN_ACTIVE_PYTHON_METADATA","package.nvidia-nccl-cu13":"NOT_IN_ACTIVE_PYTHON_METADATA","package.pytorch-lightning":"NOT_IN_ACTIVE_PYTHON_METADATA","package.torch":"NOT_IN_ACTIVE_PYTHON_METADATA","package.transformers":"NOT_IN_ACTIVE_PYTHON_METADATA","probe.chrony_tracking":{"exit_code":1,"stderr_present":false,"stdout":""},"probe.docker_client":{"exit_code":0,"stderr_present":false,"stdout":"Docker version 29.1.3, build 29.1.3-0ubuntu3~24.04.2\n"},"probe.docker_running_count":{"exit_code":1,"stderr_present":true,"stdout":"UNKNOWN"},"probe.dpkg_stack":{"exit_code":1,"stderr_present":true,"stdout":"datacenter-gpu-manager\t\tnot-installed\ndatacenter-gpu-manager-4-core\t1:4.6.1-1\tinstalled\ndatacenter-gpu-manager-4-proprietary\t1:4.6.1-1\tinstalled\ndatacenter-gpu-manager-exporter\t4.8.4.3955-1\tinstalled\n"},"probe.gpu_compute_apps":{"exit_code":0,"stderr_present":false,"stdout":"{\"compute_app_rows\": 0}"},"process_comm_counts":{"chronyd":2,"containerd":1,"dcgm-exporter":1,"dockerd":1,"node_exporter":1,"python3":10},"process_comm_unreadable":0,"python_runtime":"3.12.3"},"id":"E-A-02","node":"A","scope":"login host namespace; no workload/container content","ssh_exit_code":0,"start_utc":"2026-10-15T08:09:52.039415+00:00"}
```

</details>

<details>
<summary>E-A-03 / F</summary>

```json
{"command_group":"F","end_utc":"2026-10-15T08:11:16.767878+00:00","executed":true,"id":"E-A-03","node":"A","probes":[{"exit_code":1,"probe":"docker_access","stderr":"PERMISSION_DENIED","stdout":""},{"exit_code":1,"probe":"chrony_tracking","stderr":"","stdout":"506 Cannot talk to daemon\n"},{"exit_code":0,"probe":"dcgm_core_package","stderr":"","stdout":"datacenter-gpu-manager-4-core\t1:4.6.1-1\tinstalled\n"},{"exit_code":0,"probe":"dcgm_exporter_package","stderr":"","stdout":"datacenter-gpu-manager-exporter\t4.8.4.3955-1\tinstalled\n"}],"scope":"login host namespace; no workload/container content","ssh_exit_code":0,"start_utc":"2026-10-15T08:11:15.849573+00:00"}
```

</details>

<details>
<summary>E-A-04 / O</summary>

```json
{"command_group":"O","end_utc":"2026-10-15T08:12:08.929564+00:00","executed":true,"id":"E-A-04","node":"A","probes":[{"exit_code":0,"probe":"gpu_pid_mapping","stderr":"","stdout":"{\"rows\": 8, \"distinct_pids\": 8, \"distinct_gpu_uuids\": 8}"},{"exit_code":1,"probe":"host_packages","stderr":"dpkg-query: no packages found matching prometheus-node-exporter\n","stdout":"chrony\t4.5-1ubuntu4.2\tinstalled\ndocker.io\t29.1.3-0ubuntu3~24.04.2\tinstalled\nnvidia-container-toolkit\t1.20.1-1\tinstalled\n"},{"exit_code":0,"probe":"exporter_service","stderr":"","stdout":"LoadState=not-found\nActiveState=inactive\nSubState=dead\n"},{"exit_code":0,"probe":"dcgm_service","stderr":"","stdout":"LoadState=loaded\nActiveState=inactive\nSubState=dead\n"},{"exit_code":0,"probe":"node_metrics_service","stderr":"","stdout":"LoadState=not-found\nActiveState=inactive\nSubState=dead\n"}],"scope":"login host namespace; no workload/container content","ssh_exit_code":0,"start_utc":"2026-10-15T08:12:08.150529+00:00"}
```

</details>

<details>
<summary>E-B-01 / P</summary>

```json
{"command_group":"P","end_utc":"2026-10-15T08:08:32.133781+00:00","executed":true,"id":"E-B-01","node":"B","probes":{"container":{"exit_code":1,"value":"none"},"cpu_count":{"exit_code":0,"value":"192"},"driver_cuda":{"exit_code":0,"value":"driver_advertised_cuda=13.0"},"gpu":{"exit_code":0,"value":{"count":8,"rows":["NVIDIA H800, 580.178.04, 81559 MiB"]}},"kernel":{"exit_code":0,"value":"Linux 6.8.0-139-generic x86_64"},"memory":{"exit_code":0,"value":"MemTotal:       1056419436 kB"},"os":{"exit_code":0,"value":"NAME=Ubuntu\nVERSION_ID=24.04"},"python":{"exit_code":0,"value":"Python 3.12.3"},"time":{"exit_code":0,"value":"Timezone=Etc/UTC\nNTP=yes\nNTPSynchronized=yes"},"tools":{"exit_code":0,"value":"python=NOT_ON_PATH\npython3=PRESENT\nnvcc=NOT_ON_PATH\nnvidia-smi=PRESENT\ndcgmi=PRESENT\nnv-hostengine=PRESENT\ndcgm-exporter=PRESENT\ndocker=PRESENT\npodman=NOT_ON_PATH\nsrun=NOT_ON_PATH\ntorchrun=NOT_ON_PATH\nmpirun=NOT_ON_PATH\nchronyc=PRESENT\ntimedatectl=PRESENT"},"utc":{"exit_code":0,"value":"2026-10-15T08:08:31Z"}},"scope":"login host namespace; no workload/container content","ssh_exit_code":0,"start_utc":"2026-10-15T08:08:30.352839+00:00"}
```

</details>

<details>
<summary>E-B-02 / S</summary>

```json
{"command_group":"S","end_utc":"2026-10-15T08:10:22.157681+00:00","executed":true,"fields":{"clock.monotonic":{"adjustable":false,"implementation":"clock_gettime(CLOCK_MONOTONIC)","monotonic":true,"resolution":1e-09},"clock.perf_counter":{"adjustable":false,"implementation":"clock_gettime(CLOCK_MONOTONIC)","monotonic":true,"resolution":1e-09},"clock.time":{"adjustable":true,"implementation":"clock_gettime(CLOCK_REALTIME)","monotonic":false,"resolution":1e-09},"known_marker./.dockerenv":"False","known_marker./run/.containerenv":"False","known_marker./usr/local/cuda/bin/nvcc":"False","known_marker./usr/local/cuda/version.json":"False","package.accelerate":"NOT_IN_ACTIVE_PYTHON_METADATA","package.deepspeed":"NOT_IN_ACTIVE_PYTHON_METADATA","package.lightning":"NOT_IN_ACTIVE_PYTHON_METADATA","package.megatron-core":"NOT_IN_ACTIVE_PYTHON_METADATA","package.nvidia-cuda-runtime-cu11":"NOT_IN_ACTIVE_PYTHON_METADATA","package.nvidia-cuda-runtime-cu12":"NOT_IN_ACTIVE_PYTHON_METADATA","package.nvidia-cuda-runtime-cu13":"NOT_IN_ACTIVE_PYTHON_METADATA","package.nvidia-nccl-cu11":"NOT_IN_ACTIVE_PYTHON_METADATA","package.nvidia-nccl-cu12":"NOT_IN_ACTIVE_PYTHON_METADATA","package.nvidia-nccl-cu13":"NOT_IN_ACTIVE_PYTHON_METADATA","package.pytorch-lightning":"NOT_IN_ACTIVE_PYTHON_METADATA","package.torch":"NOT_IN_ACTIVE_PYTHON_METADATA","package.transformers":"NOT_IN_ACTIVE_PYTHON_METADATA","probe.chrony_tracking":{"exit_code":1,"stderr_present":false,"stdout":""},"probe.docker_client":{"exit_code":0,"stderr_present":false,"stdout":"Docker version 29.1.3, build 29.1.3-0ubuntu3~24.04.2\n"},"probe.docker_running_count":{"exit_code":1,"stderr_present":true,"stdout":"UNKNOWN"},"probe.dpkg_stack":{"exit_code":1,"stderr_present":true,"stdout":"datacenter-gpu-manager\t\tnot-installed\ndatacenter-gpu-manager-4-core\t1:4.6.1-1\tinstalled\ndatacenter-gpu-manager-4-proprietary\t1:4.6.1-1\tinstalled\ndatacenter-gpu-manager-exporter\t4.8.4.3955-1\tinstalled\n"},"probe.gpu_compute_apps":{"exit_code":0,"stderr_present":false,"stdout":"{\"compute_app_rows\": 8}"},"process_comm_counts":{"chronyd":2,"containerd":1,"dcgm-exporter":1,"dockerd":1,"node_exporter":1,"python3":2},"process_comm_unreadable":0,"python_runtime":"3.12.3"},"id":"E-B-02","node":"B","scope":"login host namespace; no workload/container content","ssh_exit_code":0,"start_utc":"2026-10-15T08:10:20.739842+00:00"}
```

</details>

<details>
<summary>E-B-03 / F</summary>

```json
{"command_group":"F","end_utc":"2026-10-15T08:11:38.268657+00:00","executed":true,"id":"E-B-03","node":"B","probes":[{"exit_code":1,"probe":"docker_access","stderr":"PERMISSION_DENIED","stdout":""},{"exit_code":1,"probe":"chrony_tracking","stderr":"","stdout":"506 Cannot talk to daemon\n"},{"exit_code":0,"probe":"dcgm_core_package","stderr":"","stdout":"datacenter-gpu-manager-4-core\t1:4.6.1-1\tinstalled\n"},{"exit_code":0,"probe":"dcgm_exporter_package","stderr":"","stdout":"datacenter-gpu-manager-exporter\t4.8.4.3955-1\tinstalled\n"}],"scope":"login host namespace; no workload/container content","ssh_exit_code":0,"start_utc":"2026-10-15T08:11:37.615188+00:00"}
```

</details>

<details>
<summary>E-B-04 / O</summary>

```json
{"command_group":"O","end_utc":"2026-10-15T08:12:18.077387+00:00","executed":true,"id":"E-B-04","node":"B","probes":[{"exit_code":0,"probe":"gpu_pid_mapping","stderr":"","stdout":"{\"rows\": 8, \"distinct_pids\": 8, \"distinct_gpu_uuids\": 8}"},{"exit_code":1,"probe":"host_packages","stderr":"dpkg-query: no packages found matching prometheus-node-exporter\n","stdout":"chrony\t4.5-1ubuntu4.2\tinstalled\ndocker.io\t29.1.3-0ubuntu3~24.04.2\tinstalled\nnvidia-container-toolkit\t1.20.1-1\tinstalled\n"},{"exit_code":0,"probe":"exporter_service","stderr":"","stdout":"LoadState=not-found\nActiveState=inactive\nSubState=dead\n"},{"exit_code":0,"probe":"dcgm_service","stderr":"","stdout":"LoadState=loaded\nActiveState=inactive\nSubState=dead\n"},{"exit_code":0,"probe":"node_metrics_service","stderr":"","stdout":"LoadState=not-found\nActiveState=inactive\nSubState=dead\n"}],"scope":"login host namespace; no workload/container content","ssh_exit_code":0,"start_utc":"2026-10-15T08:12:17.299618+00:00"}
```

</details>

### 公开摘要完整性检查

在仓库根目录使用已有 Python 标准库执行；现核验 18 个独立 ID 和表中哈希（首轮 8 条摘要保持原文不变），不验证原始主机真实性，也不访问服务器：

```python
from pathlib import Path
import hashlib, json, re
report = Path('docs/M0_1_INVENTORY.md').read_text()
index = dict(re.findall(r'\| (E-[AB]-0[1-9]) \|[^\n]*`([0-9a-f]{64})`', report))
blocks = re.findall(r'```json\n([^\n]+)\n```', report)
assert len(index) == len(blocks) == 18
seen = set()
for block in blocks:
    data = json.loads(block)
    assert data['id'] not in seen
    seen.add(data['id'])
    canonical = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n'
    assert hashlib.sha256(canonical.encode()).hexdigest() == index[data['id']]
print('PASS: eighteen unique evidence summaries and hashes')
```

本地另与受控副本逐字比对、检查证据目录权限、五份交付文档的已知敏感值/身份/密钥模式，exit 0。上述扫描有模式覆盖限制，已补人工审查。文档生成阶段临时辅助脚本的源编码诊断失败及恢复见 STATUS 的 F-Local，未影响服务器或改动工程检查器。

## 首轮决定与交付边界（后续补证见下）

| 问题 | 选项与选择 | 依据 | 风险与验证 |
| --- | --- | --- | --- |
| 缺少训练版本时如何补证 | 保留 UNKNOWN；不遍历旧项目/容器构建物，不导入 Torch，不启动训练 | 当前解释器无元数据、Docker 权限拒绝、任务归属不明 | M0-1 训练层仍有缺口，需管理员/任务所有者受控提供证据 |
| 二进制/进程存在是否足够 | 只记录安装与进程线索；配置/实际信号另列 UNKNOWN | 指定 unit 状态和进程 comm 并不一致 | 不把线索填成 M0-2 兼容性 PASS |
| 非零混合查询如何解释 | 保留整体失败及已返回事实；最小独立复采 | 02 的 dpkg 非零、03 单项成功，Docker/Chrony 重现失败 | 不掩盖失败，不跨时间拼装一次成功 |

本次交付为真实只读环境调查及明确缺口，**不自评双机训练环境全量 PASS**。A/B 平台证据已具备；训练层/信号配置仍 INCONCLUSIVE，等待 ChatGPT 独立审核。M0-Gate 仍 INCONCLUSIVE，M0-2/M0-3/M1 未执行且未授权。文档、摘要哈希、敏感信息与 CI 验证见 [STATUS](STATUS.md) 及 Draft PR；新会话按 [HANDOFF](HANDOFF.md) 恢复。

## 容器补证：授权、范围与结果

**最新授权与用户决定**：2026-10-15（Asia/Shanghai），用户进一步明确允许所有现有容器访问，指定使用已有账户/机器/容器凭据，优先复用既有 PyTorch。先写 C1 采集清单，再使用现有 sudo 权限执行限定查询，没有修改 sudoers、用户组或 Docker socket。密码只从指定本地文件读取，经 SSH stdin 供 sudo 认证，不放命令参数/环境变量/日志。用户随后提出清理并确认每台保留一个，但在任何删除前明确取消：“先不清理了，找到一个可用的就行”。**清理 CANCELLED，删除/停止/重启/新建容器均为 0**；只发生清理前元数据盘点，没有执行 rm/prune/stop/restart、删除镜像或卷。

采集窗口 **2026-10-15 16:36:01～16:42:26 Asia/Shanghai（UTC+08:00）**。A/B 各自保留已运行且未暂停的 C1，仅从 `/` 读取系统/第三方发行包元数据；不读取旧项目源码/配置/构建内容、完整容器配置/Env 或任务日志。Docker exec 只启动短暂查询进程，不启动训练；这会产生容器 exec/SSH/sudo 审计事件，不承诺运行时绝对零状态变化。隔离 Python `-I -S -B` 避免当前目录、用户 site、启动 hook 与字节码写入；CPU 导入显式隐藏 GPU、限制线程。未下载/上传/构建/安装任何环境：已有候选，用户条件分支未触发。

| 环境事实（OBSERVED） | A / C1 | B / C1 | 独立证据与边界 |
| --- | --- | --- | --- |
| 当前候选 | 已运行、未暂停，Python import 成功 | 同状态，独立采集 | 07/08/09；仅系统和第三方包，不继承旧工程 |
| OS / Python | Ubuntu 24.04 / 3.12.3 | 同版本，独立采集 | 07；与宿主机默认 Python 分开记录 |
| PyTorch | 2.13.0+cu130，元数据/常量/import 一致 | 同版本，独立采集 | 07/08/09；CPU 导入成功不是 GPU 或训练验收 |
| Torch 构建 CUDA | 13.0 | 13.0 | 07/09；构建声明，不冒充 Runtime 完整版本 |
| CUDA Toolkit | nvcc release 13.0，V13.0.88 | 同版本，独立采集 | 07；编译器版本读取，没有编译程序 |
| CUDA Runtime | 导入进程映射 libcudart.so.13；完整补丁版本 UNKNOWN | 同左，独立采集 | 08/09；映射主版本，未调用 CUDA 初始化/分配/内核 |
| NCCL Python 包 / header | nvidia-nccl-cu13=2.30.7 / 2.30.7 | 同版本，独立采集 | 07；不等于 Torch 版本 API 或真实训练进程加载版本 |
| Torch NCCL 版本 API | (2,29,7)，raw 8591835143 | 同值，独立采集 | 09；公开摘要把原始字段名 nccl_linked_version 澄清为 torch_nccl_api_raw，不能仅凭旧字段名认定运行库版本 |
| 本次导入进程已映射 NCCL | libnccl.so.2；RTLD_NOLOAD + ncclGetVersion exit 0/code 23007（2.30.7） | 同值，独立采集 | 09；仅查询自己的已映射库，不 attach 他人进程、不创建 communicator |
| Transformers / Accelerate | 5.17.0 / 1.15.0 | 同版本，独立采集 | 07，已装元数据；未执行框架训练 |
| 分布式构建 / GPU 初始化标记 | distributed.is_available=True；is_initialized 在导入/版本查询前后均 false | 同值，独立采集 | 08/09；未执行 rendezvous、collective、GPU 或双机训练 |

**判断**：现有 C1 可作为后续工作的环境候选，已证明可读版本且 PyTorch 可导入；用户决定保留现状。Torch NCCL API 2.29.7 与已安装/查询到的库 2.30.7 不同，保留事实，不自评兼容/不兼容。真实训练任务的进程加载库、Job/Run/Rank、launcher、日志/指标及跨机时钟精度仍 UNKNOWN。M0-2/M0-3/M1 未执行，M0-Gate 仍 INCONCLUSIVE。

[官方 ncclGetVersion 语义](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/api/comms.html#ncclgetversion) 仅用于说明版本查询返回所链接库的编码，不从最新文档推断本机功能支持；上述数值来自各节点实际调用。没有复制外部实现代码。

### 补证命令与失败记录

| 组 / 执行 | 命令与影响 | 结果 / 脱敏与限制 |
| --- | --- | --- |
| C1 / A05、B05 | sudo 下已有 Python；docker ps --all 的 ID/state/image 与 image ls 的 ID/tag；8 秒子命令、60 秒 SSH | A sudo/root 与读取成功；容器输出 16 KiB 截断，只能描述完整前缀；B sudo 认证失败，exit 1，原始症状留受控区 |
| C2 / A06、B06 | docker ps 仅运行容器；全量 state 聚合；不读配置内容 | 各 exit 0；各 1 running / 245 exited / 1 created。B 改用已提供的登录账户密码后成功；不修改权限、不枚举未知密码 |
| C3 / A07、B07 | 对当前运行且未暂停的最多 4 个容器，docker exec --user 0 --workdir / --env PYTHONDONTWRITEBYTECODE=1；只读 OS/nvcc 与隔离 Python 发行元数据/版本常量 | 实际各 1 个 C1，所有子命令 exit 0；不读项目目录，容器/镜像身份仅受控记录 |
| C4 / A08、B08 | 清理前 state/选定 mount 字段；隐藏 GPU 的 Torch import 与版本 API；无删除动作 | import exit 0；mount 模板 .Name 在部分 bind mount 缺失，exit 1，stderr 文本截断；不能据其判断卷可删 |
| C5 / A09、B09 | mount 模板仅取 Type 修复；镜像 ID/卷名计数；再次隔离 import、Torch NCCL API；对本进程已映射 NCCL 以 RTLD_NOLOAD 调 ncclGetVersion | 所有子命令 exit 0；各 247 条选定容器元数据；镜像数 A13/B8、Docker volume 对象数各0，但有 bind mount，**0 volume 对象不等于无数据**。用户取消清理，未修改任何对象 |

失败补充：本地读取 A05 截断前缀时曾因末尾不完整行触发 IndexError / exit 1；改为只统计三字段完整行后 exit 0，不重写原始数据。A05 的运行数前缀与 A06 的后续快照不同，不能混成同一时刻。以上缺陷与 sudo 认证失败均保留；没有把 SSH exit 0 当成子命令全部成功。

可用性判断限定 CPU 导入和版本查询；真实 GPU、NCCL collective、双机训练、RAS/Flight Recorder 均 NOT_RUN。初次 Docker 权限拒绝是历史事实，在本轮明确授权使用现有 sudo 后，**B-Container 已对系统/第三方版本查询解除**。B-Workload 仍未解决。

### 补证索引与脱敏摘要

公开逻辑 `LOCAL/<证据ID>` 对应同一授权本机受控索引（含准确命令与原始返回），不公开服务器身份/容器 ID/镜像名/卷名/内部路径。C1..C5 的程序与命令在受控记录中；下列核心 Python 代码为实际版本/导入查询，外围只做表中 Docker 元数据读取、状态校验、超时与输出限长。C4 失败模板和 C5 修正分别记录，不能以 C5 成功覆盖 C4。公开摘要仍用前述规范 JSON SHA-256；所有 18 条由更新后的公开校验代码检查，首轮 8 条保持原文/哈希不变。

| ID | 节点 | 2026-10-15 UTC 开始～结束 | 命令组 / exit | 摘要 SHA-256 |
| --- | --- | --- | --- | --- |
| E-A-05 | A | 08:36:01.055233～08:36:02.172722 | C1 / 0 | `4b1e1e4f13d680f0d351107f6666e434ee539d840e28ea563e09149fcdeeafbd` |
| E-A-06 | A | 08:37:06.600292～08:37:07.333893 | C2 / 0 | `9c334aca58040cfa764cadeac131cabb74e5613e6b63b890c9b8dc0c8f7bed47` |
| E-A-07 | A | 08:38:35.997030～08:38:36.980750 | C3 / 0 | `aa727e5ed8ff215f3582756683a4254a61352c3d3e50e038bb71b90c26007915` |
| E-A-08 | A | 08:40:37.252437～08:40:41.912740 | C4 / 0 | `eccf0d426f790801346615fa3e95631135e0fa4484b39383e0be96e7dd3ea5ac` |
| E-A-09 | A | 08:42:09.218724～08:42:13.737733 | C5 / 0 | `1412ba72449ab61ca254019e9f173ea8555d51d238db0f3f8b34d8aa69a7a6fb` |
| E-B-05 | B | 08:36:32.219984～08:36:34.817049 | C1 / 1 | `1094da21d4b967aca3d920011842323d59ee9cbfc7290dabb6cb910af633925a` |
| E-B-06 | B | 08:37:35.852751～08:37:36.702385 | C2 / 0 | `860f9d5427af762f144d60602ece55d82608dfb5b92fff5d1060e762c4a66984` |
| E-B-07 | B | 08:39:07.746836～08:39:08.989995 | C3 / 0 | `ebb0d94f4351e8910fc4d5b96279c54ae97c4285c9271d333c37794b72a81036` |
| E-B-08 | B | 08:40:50.707557～08:40:55.428107 | C4 / 0 | `d8f54b03352ed59dcd63db47db5d51495f7c2c4a0a2140397cd7617e13ca0473` |
| E-B-09 | B | 08:42:22.043914～08:42:26.769107 | C5 / 0 | `ed619a5b45ddf52763aac804c27f693b2dfffdceca00aa38f11eddd15bcf7ce8` |

<details>
<summary>C3：隔离 Python 的系统/第三方发行元数据查询</summary>

```python
import sys,sysconfig,pathlib,glob,json,ast,importlib.metadata as md
result={'python':sys.version.split()[0],'packages':{},'torch_build':{},'nccl_headers':[]}
allowed={'torch','nvidia-nccl-cu11','nvidia-nccl-cu12','nvidia-nccl-cu13','nvidia-cuda-runtime-cu11','nvidia-cuda-runtime-cu12','nvidia-cuda-runtime-cu13','deepspeed','transformers','accelerate','lightning','pytorch-lightning','megatron-core'}
paths={sysconfig.get_path('purelib'),sysconfig.get_path('platlib')}
for pattern in ['/usr/local/lib/python*/site-packages','/usr/lib/python3/dist-packages','/opt/conda/lib/python*/site-packages']:
 paths.update(glob.glob(pattern))
dists={}
for d in md.distributions(path=sorted(p for p in paths if p)):
 name=d.metadata.get('Name','').lower().replace('_','-')
 if name in allowed:
  result['packages'][name]=d.version;dists[name]=d
for name in sorted(allowed):result['packages'].setdefault(name,'NOT_IN_SCOPED_METADATA')
if 'torch' in dists:
 p=pathlib.Path(dists['torch'].locate_file('torch/version.py'))
 if p.is_file() and p.stat().st_size<65536:
  for node in ast.parse(p.read_text()).body:
   if isinstance(node,(ast.Assign,ast.AnnAssign)):
    targets=node.targets if isinstance(node,ast.Assign) else [node.target]
    for t in targets:
     if isinstance(t,ast.Name) and t.id in ['__version__','cuda','hip']:
      try:result['torch_build'][t.id]=ast.literal_eval(node.value)
      except (ValueError,TypeError):result['torch_build'][t.id]='UNKNOWN'
for p in [pathlib.Path('/usr/include/nccl.h')]+[pathlib.Path(d.locate_file('nvidia/nccl/include/nccl.h')) for n,d in dists.items() if n.startswith('nvidia-nccl-')]:
 if p.is_file() and p.stat().st_size<131072:
  import re
  s=p.read_text();v={key:re.search(r'^#define\s+NCCL_'+key+r'\s+(\d+)',s,re.M) for key in ['MAJOR','MINOR','PATCH']}
  if all(v.values()):result['nccl_headers'].append('.'.join(v[k].group(1) for k in ['MAJOR','MINOR','PATCH']))
print(json.dumps(result,sort_keys=True))
```

</details>


<details>
<summary>C5：GPU 隐藏下的 Torch 导入和本进程 NCCL 版本查询</summary>

```python
import sys,sysconfig,os,json,pathlib
os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
for p in {sysconfig.get_path('purelib'),sysconfig.get_path('platlib'),'/usr/lib/python3/dist-packages'}:
 if p and p not in sys.path:sys.path.append(p)
import torch
out={'torch_imported':True,'torch_version':torch.__version__,'torch_build_cuda':torch.version.cuda,'cuda_initialized_before':torch.cuda.is_initialized(),'distributed_build_available':torch.distributed.is_available()}
f=getattr(torch._C,'_nccl_version',None)
try:out['nccl_linked_version']=f() if callable(f) else 'UNKNOWN'
except Exception as e:out['nccl_linked_version']='UNKNOWN';out['nccl_query_error_type']=type(e).__name__
out['torch_nccl_api_version']=list(torch.cuda.nccl.version())
out['cuda_initialized_after']=torch.cuda.is_initialized()
names={}
nccl_paths=set()
for line in pathlib.Path('/proc/self/maps').read_text().splitlines():
 if '/' not in line:continue
 name=pathlib.PurePosixPath(line.split()[-1]).name
 if name.startswith(('libnccl.so','libcudart.so')):names[name]=True
 if name.startswith('libnccl.so'):nccl_paths.add(line.split()[-1])
out['probe_mapped_library_basenames']=sorted(names)
import ctypes
out['already_mapped_nccl_queries']=[]
for path in sorted(nccl_paths):
 try:
  lib=ctypes.CDLL(path,mode=os.RTLD_NOLOAD|os.RTLD_LOCAL)
  value=ctypes.c_int();fn=lib.ncclGetVersion;fn.argtypes=[ctypes.POINTER(ctypes.c_int)];fn.restype=ctypes.c_int
  rc=fn(ctypes.byref(value));out['already_mapped_nccl_queries'].append({'exit_code':rc,'version_code':value.value})
 except Exception as e:out['already_mapped_nccl_queries'].append({'error_type':type(e).__name__})
out['cuda_initialized_after_version_query']=torch.cuda.is_initialized()
print(json.dumps(out,sort_keys=True))
```

</details>

<details>
<summary>E-A-05 / C1</summary>

```json
{"command_group":"C1","end_utc":"2026-10-15T08:36:02.172722+00:00","executed":true,"id":"E-A-05","node":"A","probes":[{"effective_root":true,"probe":"sudo_identity","time_utc":"2026-10-15T08:36:02.048267+00:00"},{"exit_code":0,"probe":"docker_containers","retained_complete_prefix_rows":114,"retained_prefix_states":{"exited":112,"running":2},"truncated":true},{"exit_code":0,"probe":"docker_images","retained_image_tag_rows":13,"truncated":false}],"scope":"authorized existing container inventory; vendor metadata/probe process only","ssh_exit_code":0,"start_utc":"2026-10-15T08:36:01.055233+00:00"}
```

</details>

<details>
<summary>E-A-06 / C2</summary>

```json
{"command_group":"C2","end_utc":"2026-10-15T08:37:07.333893+00:00","executed":true,"id":"E-A-06","node":"A","probes":[{"exit_code":0,"probe":"running_candidates","running_count":1,"truncated":false},{"exit_code":0,"probe":"container_states","states":{"created":1,"exited":245,"running":1}}],"scope":"authorized existing container inventory; vendor metadata/probe process only","ssh_exit_code":0,"start_utc":"2026-10-15T08:37:06.600292+00:00"}
```

</details>

<details>
<summary>E-A-07 / C3</summary>

```json
{"command_group":"C3","end_utc":"2026-10-15T08:38:36.980750+00:00","executed":true,"id":"E-A-07","node":"A","probes":[{"count":1,"probe":"running_count","probe_limit":4},{"container_alias":"C1","state_check":{"exit_code":0,"probe":"state","stderr":"","stdout":"true\tfalse\n","truncated":false}},{"container_alias":"C1","exit_code":0,"interpreter_candidates":1,"nvcc":{"release":"13.0","version":"13.0.88"},"os":{"OS_NAME":"Ubuntu","OS_VERSION":"24.04"},"probe":"os_interpreters_toolkit","truncated":false},{"container_alias":"C1","exit_code":0,"facts":{"nccl_headers":["2.30.7"],"packages":{"accelerate":"1.15.0","deepspeed":"NOT_IN_SCOPED_METADATA","lightning":"NOT_IN_SCOPED_METADATA","megatron-core":"NOT_IN_SCOPED_METADATA","nvidia-cuda-runtime-cu11":"NOT_IN_SCOPED_METADATA","nvidia-cuda-runtime-cu12":"NOT_IN_SCOPED_METADATA","nvidia-cuda-runtime-cu13":"NOT_IN_SCOPED_METADATA","nvidia-nccl-cu11":"NOT_IN_SCOPED_METADATA","nvidia-nccl-cu12":"NOT_IN_SCOPED_METADATA","nvidia-nccl-cu13":"2.30.7","pytorch-lightning":"NOT_IN_SCOPED_METADATA","torch":"2.13.0+cu130","transformers":"5.17.0"},"python":"3.12.3","torch_build":{"__version__":"2.13.0+cu130","cuda":"13.0","hip":null}},"probe":"vendor_metadata","stderr_present":false,"truncated":false}],"scope":"authorized existing container inventory; vendor metadata/probe process only","ssh_exit_code":0,"start_utc":"2026-10-15T08:38:35.997030+00:00"}
```

</details>

<details>
<summary>E-A-08 / C4</summary>

```json
{"command_group":"C4","end_utc":"2026-10-15T08:40:41.912740+00:00","executed":true,"id":"E-A-08","node":"A","probes":[{"exit_code":0,"probe":"read_only_state_snapshot","states":{"created":1,"exited":245,"running":1}},{"exit_code":1,"probe":"selected_mount_metadata","raw_stderr_truncated":true,"symptom":"DOCKER_TEMPLATE_MISSING_NAME_FIELD"},{"container_alias":"C1","exit_code":0,"facts":{"cuda_initialized_after":false,"cuda_initialized_before":false,"distributed_build_available":true,"probe_mapped_library_basenames":["libcudart.so.13","libnccl.so.2"],"torch_build_cuda":"13.0","torch_imported":true,"torch_nccl_api_raw":8591835143,"torch_version":"2.13.0+cu130"},"probe":"torch_cpu_import","stderr_present":false,"truncated":false}],"scope":"authorized existing container inventory; vendor metadata/probe process only","ssh_exit_code":0,"start_utc":"2026-10-15T08:40:37.252437+00:00"}
```

</details>

<details>
<summary>E-A-09 / C5</summary>

```json
{"command_group":"C5","end_utc":"2026-10-15T08:42:13.737733+00:00","executed":true,"id":"E-A-09","node":"A","probes":[{"exit_code":0,"probe":"read_only_state_snapshot","states":{"created":1,"exited":245,"running":1}},{"exit_code":0,"mount_types":{"bind":736},"probe":"selected_mount_metadata","rows":247,"truncated":false},{"exit_code":0,"probe":"image_ids","truncated":false,"unique_entries":13},{"exit_code":0,"probe":"volume_names","truncated":false,"unique_entries":0},{"container_alias":"C1","exit_code":0,"facts":{"already_mapped_nccl_queries":[{"exit_code":0,"version_code":23007}],"cuda_initialized_after":false,"cuda_initialized_after_version_query":false,"cuda_initialized_before":false,"distributed_build_available":true,"probe_mapped_library_basenames":["libcudart.so.13","libnccl.so.2"],"torch_build_cuda":"13.0","torch_imported":true,"torch_nccl_api_raw":8591835143,"torch_nccl_api_version":[2,29,7],"torch_version":"2.13.0+cu130"},"probe":"torch_cpu_import","stderr_present":false,"truncated":false}],"scope":"authorized existing container inventory; vendor metadata/probe process only","ssh_exit_code":0,"start_utc":"2026-10-15T08:42:09.218724+00:00"}
```

</details>

<details>
<summary>E-B-05 / C1</summary>

```json
{"command_group":"C1","end_utc":"2026-10-15T08:36:34.817049+00:00","executed":true,"id":"E-B-05","node":"B","probes":[],"scope":"authorized existing container inventory; vendor metadata/probe process only","ssh_exit_code":1,"start_utc":"2026-10-15T08:36:32.219984+00:00","symptom":"SUDO_AUTHENTICATION_FAILED"}
```

</details>

<details>
<summary>E-B-06 / C2</summary>

```json
{"command_group":"C2","end_utc":"2026-10-15T08:37:36.702385+00:00","executed":true,"id":"E-B-06","node":"B","probes":[{"exit_code":0,"probe":"running_candidates","running_count":1,"truncated":false},{"exit_code":0,"probe":"container_states","states":{"created":1,"exited":245,"running":1}}],"scope":"authorized existing container inventory; vendor metadata/probe process only","ssh_exit_code":0,"start_utc":"2026-10-15T08:37:35.852751+00:00"}
```

</details>

<details>
<summary>E-B-07 / C3</summary>

```json
{"command_group":"C3","end_utc":"2026-10-15T08:39:08.989995+00:00","executed":true,"id":"E-B-07","node":"B","probes":[{"count":1,"probe":"running_count","probe_limit":4},{"container_alias":"C1","state_check":{"exit_code":0,"probe":"state","stderr":"","stdout":"true\tfalse\n","truncated":false}},{"container_alias":"C1","exit_code":0,"interpreter_candidates":1,"nvcc":{"release":"13.0","version":"13.0.88"},"os":{"OS_NAME":"Ubuntu","OS_VERSION":"24.04"},"probe":"os_interpreters_toolkit","truncated":false},{"container_alias":"C1","exit_code":0,"facts":{"nccl_headers":["2.30.7"],"packages":{"accelerate":"1.15.0","deepspeed":"NOT_IN_SCOPED_METADATA","lightning":"NOT_IN_SCOPED_METADATA","megatron-core":"NOT_IN_SCOPED_METADATA","nvidia-cuda-runtime-cu11":"NOT_IN_SCOPED_METADATA","nvidia-cuda-runtime-cu12":"NOT_IN_SCOPED_METADATA","nvidia-cuda-runtime-cu13":"NOT_IN_SCOPED_METADATA","nvidia-nccl-cu11":"NOT_IN_SCOPED_METADATA","nvidia-nccl-cu12":"NOT_IN_SCOPED_METADATA","nvidia-nccl-cu13":"2.30.7","pytorch-lightning":"NOT_IN_SCOPED_METADATA","torch":"2.13.0+cu130","transformers":"5.17.0"},"python":"3.12.3","torch_build":{"__version__":"2.13.0+cu130","cuda":"13.0","hip":null}},"probe":"vendor_metadata","stderr_present":false,"truncated":false}],"scope":"authorized existing container inventory; vendor metadata/probe process only","ssh_exit_code":0,"start_utc":"2026-10-15T08:39:07.746836+00:00"}
```

</details>

<details>
<summary>E-B-08 / C4</summary>

```json
{"command_group":"C4","end_utc":"2026-10-15T08:40:55.428107+00:00","executed":true,"id":"E-B-08","node":"B","probes":[{"exit_code":0,"probe":"read_only_state_snapshot","states":{"created":1,"exited":245,"running":1}},{"exit_code":1,"probe":"selected_mount_metadata","raw_stderr_truncated":true,"symptom":"DOCKER_TEMPLATE_MISSING_NAME_FIELD"},{"container_alias":"C1","exit_code":0,"facts":{"cuda_initialized_after":false,"cuda_initialized_before":false,"distributed_build_available":true,"probe_mapped_library_basenames":["libcudart.so.13","libnccl.so.2"],"torch_build_cuda":"13.0","torch_imported":true,"torch_nccl_api_raw":8591835143,"torch_version":"2.13.0+cu130"},"probe":"torch_cpu_import","stderr_present":false,"truncated":false}],"scope":"authorized existing container inventory; vendor metadata/probe process only","ssh_exit_code":0,"start_utc":"2026-10-15T08:40:50.707557+00:00"}
```

</details>

<details>
<summary>E-B-09 / C5</summary>

```json
{"command_group":"C5","end_utc":"2026-10-15T08:42:26.769107+00:00","executed":true,"id":"E-B-09","node":"B","probes":[{"exit_code":0,"probe":"read_only_state_snapshot","states":{"created":1,"exited":245,"running":1}},{"exit_code":0,"mount_types":{"bind":736},"probe":"selected_mount_metadata","rows":247,"truncated":false},{"exit_code":0,"probe":"image_ids","truncated":false,"unique_entries":8},{"exit_code":0,"probe":"volume_names","truncated":false,"unique_entries":0},{"container_alias":"C1","exit_code":0,"facts":{"already_mapped_nccl_queries":[{"exit_code":0,"version_code":23007}],"cuda_initialized_after":false,"cuda_initialized_after_version_query":false,"cuda_initialized_before":false,"distributed_build_available":true,"probe_mapped_library_basenames":["libcudart.so.13","libnccl.so.2"],"torch_build_cuda":"13.0","torch_imported":true,"torch_nccl_api_raw":8591835143,"torch_nccl_api_version":[2,29,7],"torch_version":"2.13.0+cu130"},"probe":"torch_cpu_import","stderr_present":false,"truncated":false}],"scope":"authorized existing container inventory; vendor metadata/probe process only","ssh_exit_code":0,"start_utc":"2026-10-15T08:42:22.043914+00:00"}
```

</details>

### 发布与审核状态

PR #4 的 [ChatGPT 独立审核](https://github.com/Zwhao0/20261015/pull/4#issuecomment-6187891676) 只覆盖旧 HEAD `1dced3bdbbdf8a091c9bfde74fede838c56406c8` 的宿主机快照。恢复时 PR #4 已是 Ready/Open/Unmerged；尝试恢复 Draft 被 GitHub GraphQL 以 FORBIDDEN 拒绝。因此保留 PR #4/head，另用分支 `codex/m0-1-container-inventory` 提交**补证 Draft PR**，base 为 `codex/m0-1-inventory @ 1dced3b…`，只展示新增补证，等待新的独立审核；不自动合并、关闭旧 PR 或推进阶段。最新 PR/HEAD/CI 在 STATUS/HANDOFF 与补证 PR 描述定位。

用户使用入口仅在本地受控指南中，包含连接与现有 C1 定位，不包含密码，不推送 GitHub。清理取消的记录同样留受控索引；本轮没有服务器环境部署或需要回滚的配置变更。
