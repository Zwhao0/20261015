# M1-C2-A 离线验证与恢复证据

2026-10-15（Asia/Shanghai），[Issue #13](https://github.com/Zwhao0/20261015/issues/13)。基线 main `504d43b2c66ff1d79959a94fe75b053729cc72f2`，tree `dec625b9a2daf745a71515f32daab75f35ab2e0c`；交付分支 `codex/m1-c2-a-parallel-context`。精确最终 HEAD/tree、远端一致性和对应双 job CI 原始日志核对结果存关联 Draft PR，避免自引哈希。下述仅合成离线一致性验证，不是独立验收或现场能力证明。

## 已执行与失败恢复

- [baseline-tests.txt](baseline-tests.txt)：本地基线52项 PASS/exit0，0 fail/error/skipped，原断言未改。
- [initial-tests.raw.json](initial-tests.raw.json) / [initial-tests.txt](initial-tests.txt)：首次新增35项，34通过、1个 FileNotFoundError，FAIL/exit1，原因是 fixture manifest 尚未写入。JSON保留脱敏后完整输出；txt仅删除行末空白。不将随后 cat 日志的exit0当成测试成功。
- [recovered-tests.txt](recovered-tests.txt)：补齐六份合成 fixture 的 SHA manifest 后，相同35项原断言 PASS/exit0。没有删除负例或放宽断言。
- 子任务文档检查曾发现4行尾空格（已清理）及集成中3个尚未写入的目标链接；主窗口补齐目标后执行原全仓文档检查，不忽略链接规则。子任务原症状为交回报告，未捕获工具原日志，不冒称有该次原始日志。
- 起点命令 `gh issue view` FAIL/exit127（未安装 gh），改用已连接 GitHub API 读取 Issue/PR；未安装工具。两次定位命令对尚不存在的 `src` / `observability` 目录返回exit2，随后按实际 `observatory` 读取。远端 fetch 已先完成，不能把整组命令说成exit0。

失败日志仅将本机绝对仓库路径改为 `<REPO>`、Python系统库前缀改为 `<PYTHON_STDLIB>`；保留断言、异常与退出码。无真实训练日志、主机身份或凭据。

## 只读反例审查与修复

主窗口内子智能体审查发现证据只有attempt scope、无逐worker/process绑定；来源冲突键包含attempt可能漏掉全局cursor冲突；观测时刻参与不可变来源比较会误隔离重读；结构有效输出缺少显式覆盖状态。不是外部ChatGPT独立验收。

修复前草案保留为 commit `090b87fd51bf9131c06dfef436755f545b08d55e`，tree `829cd986191f1a1dd2b873bdeb7b84d95f6a8138`，其父即起点main。该历史快照不能作为最终交付。只在本地添加5个新断言后，原代码实际产生 **4失败+1错误/5项/exit1**：[binding-before.txt](binding-before.txt) / [完整脱敏原输出](binding-before.raw.json)。两项证据跨worker复用误被接受、跨attempt同槽冲突漏隔离、重读误隔离均实际复现；缺coverage字段抛KeyError。

修复：证据增加合成source profile和worker/process subject；逐worker字段核对subject，GPU必须有同一完整process；来源槽按全局source_id/epoch/seq隔离，读时clock/tick独立；输出覆盖/真实性/epoch连续性明确UNKNOWN。新增4项profile/实例映射正负例。初次集成恢复48项仍有2失败+1错误/exit1：[binding-first-recovery.txt](binding-first-recovery.txt)；原因是三个旧合成变体缺少新的显式前提（跨attempt来源需显式新namespace、进程改变须同步证据绑定、缺process时GPU也须UNKNOWN）。保留原语义断言，修正合成输入前提；没有改原C1任何断言。该轮52项新增测试 PASS/exit0：[binding-after.txt](binding-after.txt)。随后主窗口与子复查均发现rank引用可携带旧process实例，新增专项实际FAIL/exit1：[stale-rank-before.txt](stale-rank-before.txt) / [原输出](stale-rank-before.raw.json)；修复为携带实例时必须匹配当前process，并补充worker-only rank正例，最终54项专项PASS：[final-targeted-tests.txt](final-targeted-tests.txt)。新fixture SHA更新仅限新sidecar目录，旧C1 manifest/golden不变。

本地checkpoint的Git自动提交身份含不适合发布的机器元数据，因此没有推送该本地commit；通过GitHub Git data从相同tree/相同main父提交创建上面的公开checkpoint。未发布机器元数据，不对远端强推或改史；最终远端HEAD保留此公开checkpoint为祖先。最终同步保留本地checkpoint在独立安全分支。

最终全量 **106项（原52+新增54），0失败/0错误/0跳过，PASS/exit0**，见 [final-tests.txt](final-tests.txt)。独立文档检查 PASS/exit0，见 [docs-check.txt](docs-check.txt)，不作为功能验证；最终diff/范围/有限敏感模式及内容哈希见validation/scope-check。子智能体复查时实际52新测试通过，主窗口随后补齐两项stale rank正负例；不是外部ChatGPT独立审查。

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

最终检查命令、环境、exit、内容SHA、受保护文件与旧状态保真结果由 [validation.json](validation.json) 与 [scope-check.json](scope-check.json) 登记。真实 launcher/scheduler/任务身份/权限/CPU wait/组/专家源/动态token路由、现场 I0～I5、GPU/collective、训练吞吐/CPU/RSS/I/O/低开销均 NOT_RUN/INCONCLUSIVE；C2-B BLOCKED 且未授权。无服务器/旧项目/环境/容器/训练代码操作。不合并、不强推、不进入 C2-B/C3。
