---
标识: 2026-03-24-Harness design for long-running application development
标题: Harness design for long-running application development
来源: https://www.anthropic.com/engineering/harness-design-long-running-apps
作者: www.anthropic.com
发布方: www.anthropic.com
日期: 2026-03-24
优先级: P2
评估理由: 资料具备明确主题与一手上下文，但当前更适合先做一阶归档，等待与同主题资料形成交叉验证后再升级。
状态: 已归档
关联概念: [Harness Engineering, Managed Agents]
关联主题: [Harness Engineering 与 Agent 运行时设计]
---

# Harness design for long-running application development

## 1. 为什么先收录 (Why Keep This Clip)
- **当前保留价值**：它保留的是长任务应用开发里 Harness 设计的原始一手入口，可作为 Managed Agents 与运行时边界的旁证。
- **暂不升级原因**：当前抽取质量还不足，只能先保留主题方向，等待更完整内容或第二来源补强。
- **图谱挂点**：当前先挂到 [[Concepts/Harness Engineering]]、[[Concepts/Managed Agents]]，并作为 [[Topics/Harness Engineering 与 Agent 运行时设计]] 的补充线索。

## 2. 当前可确认的关键信息 (Confirmed Signal)
- **当前线索**：可以确认这篇文章在继续推进 Anthropic 的 long-running harness 方向，但重点从“基础壳层有效”转向“如何通过多 Agent 结构继续突破质量上限”。
- **可确认事实 1**：文章明确承接了早期 harness 工作里的两条经验：把大任务拆成可处理的块，以及用结构化 artifact 在不同 session 之间交接上下文。
- **可确认事实 2**：它进一步引入了 planner / generator / evaluator 的三代理结构，把生成和评估拆开，用外部 evaluator 替代 agent 自评的乐观偏差。
- **当前证据状态**：目前仍以单篇资料为主，只能确认主题方向和局部信号，尚不足以沉淀成稳定 Source。

## 3. 后续升级条件 (Upgrade Trigger)
- **需要第二来源**：需要补回更完整的正文或第二来源，确认这篇文章在 session、sandbox、恢复策略上的具体观点。
- **需要补齐机制 / 数据**：需要提取真实设计原则、失败模式或案例数据，才能升级为 Source。
- **升级后归位**：若补齐交叉证据，可升级为 Source，并稳定挂到 [[Topics/Harness Engineering 与 Agent 运行时设计]]。
