# 老笔记扫描报告 - 2025面试

## 1. 扫描范围
- 输入路径：`/Users/norven/workspace/MyObsidian/13沉淀笔记/2025面试`
- 输出目录：`/Users/norven/workspace/MyObsidian/Distill/99-Meta/legacy-notes/2026-04-11-184855-2025面试`
- 扫描文件数：8
- Manifest：`/Users/norven/workspace/MyObsidian/Distill/99-Meta/legacy-notes/2026-04-11-184855-2025面试/manifest.json`

## 2. 成熟度分布
- fragment: 5
- synthesis-note: 3

## 3. 默认落点建议
- Clipping: 5
- Topic: 3

## 4. 风险摘要
- attachments: 5

## 5. 需优先人工复核
- `AMS.md` → attachments
- `Binder.md` → attachments
- `Handler.md` → attachments
- `渲染绘制.md` → attachments
- `进程启动.md` → attachments

## 6. 高重复候选（建议 merge / compare）
- 无

## 7. 逐文件清单
| 文件 | 成熟度 | 候选目标 | 动作 | 风险 | 重复候选 |
|------|--------|----------|------|------|----------|
| `AMS.md` | fragment | Clipping | write | attachments | 无 |
| `Android任务调度与拓扑排序：从理论到实践.md` | synthesis-note | Topic | write | 无 | 无 |
| `Binder.md` | fragment | Clipping | compare | attachments | concept:Binder IPC(0.75) |
| `Handler.md` | fragment | Clipping | write | attachments | concept:Binder IPC(0.471) |
| `IMS.md` | synthesis-note | Topic | write | 无 | 无 |
| `WMS.md` | synthesis-note | Topic | write | 无 | 无 |
| `渲染绘制.md` | fragment | Clipping | write | attachments | 无 |
| `进程启动.md` | fragment | Clipping | write | attachments | 无 |

## 8. 人工纠偏与实际落地（2026-04-12）
- 扫描器把 `AMS.md`、`Handler.md`、`渲染绘制.md`、`进程启动.md` 判成 `fragment`，但人工复核后确认：这些笔记的正文成熟度高于 scan 结果，误判主因是标题统计偏向 `##`，对大量使用 `#` 的旧笔记不友好。
- 本次迁移**没有机械接受默认的 Clipping/Topic 建议**，而是按“去重优先、学习资产优先”的原则重构为：
  - 新增 Concepts：
    - `[[Concepts/ActivityManagerService]]`
    - `[[Concepts/WindowManagerService]]`
    - `[[Concepts/Handler 消息机制]]`
    - `[[Concepts/启动任务拓扑调度]]`
  - 新增 Topic：
    - `[[Topics/Android Framework 进程、消息、窗口与渲染主线]]`
  - 去重吸收而非重复新建：
    - `Binder.md` → 复用既有 `[[Concepts/Binder IPC]]`
    - `IMS.md` → 复用既有 `[[Concepts/InputManagerService]]`
    - `渲染绘制.md` 的渲染链材料 → 进入新 Topic，并与既有 `[[Concepts/RenderThread]]` 衔接
- 这次落地的原则不是“一篇旧笔记对应一篇新笔记”，而是“让 8 篇旧材料共同沉淀成更强的 learner-facing 资产”，同时避免把现有图谱打碎或重复造轮子。
