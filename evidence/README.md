# M1-C1 验证证据

本目录仅保存合成离线验证证据。使用入口见 [M1-C1](../docs/M1_C1_OFFLINE.md)。最终精确HEAD/tree、对应CI和最新本地执行对象由Issue #11关联Draft PR记录；文档不循环引用包含自身的commit。

- [首次集成功能日志](local-initial-tests.txt)：29项，1失败（T09），测试进程exit1；后续cat exit0未作为测试结果。绝对本机仓库路径已替换为`<REPO>`。
- [初始T09输入](T09-initial.jsonl)及[初始期望快照](T09-initial.expected.json)：误复用source_seq=0，使同域age断言失败；修正fixture序号为0/1/2，保留断言[2.0,null]。
- [最终本地功能日志](local-tests.txt)：实际unittest输出，独立于文档检查。
- [首次文档失败](local-initial-docs.txt)：检查在证据目标文件尚未落盘时运行，两个本地链接检查失败，exit1；按生成顺序补齐后恢复，未降低检查要求。
- [最终本地文档日志](local-docs.txt)：原检查器与diff空白检查，不能证明功能。
- [执行元数据](local-validation.json)：环境、命令、测试对象代码/fixture内容哈希与退出码；精确提交对象以PR发布后重新执行记录为准。

首次子任务提前运行全套，26项中12项契约PASS，14项因fixtures施工尚缺报FileNotFoundError；其摘要完整保留于M1-C1文档。主集成另发现初版schema_version遗漏并补齐校验/反例。本目录不含服务器原始日志或真实训练记录；原M0失败未改写。

首轮远端 [CI元数据](ci-initial.json)记录实现head/tree、测试合并SHA及两个job实际结果。后续证据提交对应的新CI以PR #12为准；未把旧run作为新head验证。发布时缺新分支fetch refspec造成一次merge exit1及一次跟踪exit128，显式fetch和追加该分支refspec后恢复；未丢失远端commit、未改写历史。

## R1 最小修正证据

- [修复前回归可读日志](r1-before-tests.txt) / [原输出JSON存档](r1-before-tests.raw.json)：被审HEAD4624b7d…的代码加新增测试，8项、18个失败子断言、exit1；实际展示非Attempt清单可导致ATTEMPT_EXITED_OK及COMPLETED。未用旧44项PASS掩盖此失败。
- [修复后专项日志](r1-after-targeted-tests.txt)：同8项、0失败/错误/跳过、exit0。
- [修复后全套日志](r1-after-tests.txt)：52项、0失败/错误/跳过、exit0，包含全部T01～T14及原44项。
- [R1文档检查](r1-docs.txt)：独立执行原检查器；不等于功能验证。
- [R1元数据与差异检查](r1-validation.json)：环境、命令、退出码、被审提交/新测试哈希、修复内容哈希、原fixture及历史保真、有限敏感模式检查；最终修复commit/tree及CI见PR #12。

本轮日志将本机仓库绝对路径替换为<REPO>。修复前unittest日志含行尾空白，首次staged diff检查FAIL/exit2；原输出含空白逐字保存在JSON存档，txt只去行尾空白，异常/断言完整保留；随后重新检查。上方local-tests等44项日志和所有既有失败文件保持原样，属于旧实现对象；本轮新结果使用r1前缀单列，不覆盖历史。
