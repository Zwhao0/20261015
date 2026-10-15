# M1-C2-A 离线验证与恢复证据

2026-10-15（Asia/Shanghai），[Issue #13](https://github.com/Zwhao0/20261015/issues/13)。基线 main `504d43b2c66ff1d79959a94fe75b053729cc72f2`，tree `dec625b9a2daf745a71515f32daab75f35ab2e0c`；交付分支 `codex/m1-c2-a-parallel-context`。精确最终 HEAD/tree、远端一致性和对应双 job CI 原始日志核对结果存关联 Draft PR，避免自引哈希。下述仅合成离线一致性验证，不是独立验收或现场能力证明。

## 已执行与失败恢复

- [baseline-tests.txt](baseline-tests.txt)：本地基线52项 PASS/exit0，0 fail/error/skipped，原断言未改。
- [initial-tests.raw.json](initial-tests.raw.json) / [initial-tests.txt](initial-tests.txt)：首次新增35项，34通过、1个 FileNotFoundError，FAIL/exit1，原因是 fixture manifest 尚未写入。JSON保留脱敏后完整输出；txt仅删除行末空白。不将随后 cat 日志的exit0当成测试成功。
- [recovered-tests.txt](recovered-tests.txt)：补齐六份合成 fixture 的 SHA manifest 后，相同35项原断言 PASS/exit0。没有删除负例或放宽断言。
- 子任务文档检查曾发现4行尾空格（已清理）及集成中3个尚未写入的目标链接；主窗口补齐目标后执行原全仓文档检查，不忽略链接规则。子任务原症状为交回报告，未捕获工具原日志，不冒称有该次原始日志。
- 起点命令 `gh issue view` FAIL/exit127（未安装 gh），改用已连接 GitHub API 读取 Issue/PR；未安装工具。两次定位命令对尚不存在的 `src` / `observability` 目录返回exit2，随后按实际 `observatory` 读取。远端 fetch 已先完成，不能把整组命令说成exit0。

失败日志仅将本机绝对仓库路径改为 `<REPO>`、Python系统库前缀改为 `<PYTHON_STDLIB>`；保留断言、异常与退出码。无真实训练日志、主机身份或凭据。

## 复现命令与内容范围

仓库根目录，Python3.9+ 标准库、Git，无依赖安装：

```sh
python3 -m unittest tests.test_parallel_context -v
python3 -m unittest discover -s tests -v
python3 scripts/check_docs.py
git diff --check
git diff 504d43b2c66ff1d79959a94fe75b053729cc72f2 --check
```

[fixture SHA manifest](../../tests/fixtures/parallel_context/manifest.json) 包含6份手工定义的合成输入（DP、混合相交组、缺映射、无来源、重入、非法成员），不是实现生成的golden；测试包含独立手写语义断言。正常化不自动生成期望结果或修改 fixture。

C1 的 `observatory/contract.py`、`engine.py`、`__main__.py`、`__init__.py`、原 tests/*.py 和 T01～T14/manifest、全部历史 M0/证据/AGENTS、工作流及文档检查器与起点字节一致。STATUS/HANDOFF 仅前置新记录，原全文后缀保留；README更新当前状态和入口，保留历史段落。有限模式扫描和人工diff审查不是通用DLP。

最终检查命令、环境、exit、内容SHA、受保护文件与旧状态保真结果由本目录 validation.json 登记。真实 launcher/scheduler/任务身份/权限/CPU wait/组/专家源/动态token路由、现场 I0～I5、GPU/collective、训练吞吐/CPU/RSS/I/O/低开销均 NOT_RUN/INCONCLUSIVE；C2-B BLOCKED 且未授权。无服务器/旧项目/环境/容器/训练代码操作。不合并、不强推、不进入 C2-B/C3。
