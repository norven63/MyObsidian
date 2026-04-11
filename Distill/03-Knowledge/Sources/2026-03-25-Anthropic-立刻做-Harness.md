---
标识: 2026-03-25-Anthropic-立刻做-Harness
标题: Anthropic说：不要在等下一代模型了，立刻马上做Harness！
来源: https://mp.weixin.qq.com/s/iTLZQHw9Dkt6AsDumZZJNQ
作者: 猕猴桃
发布方: 探索AGI
日期: 2026-03-25
优先级: P1
评估理由: 数据密度高，适合做“为什么当前阶段要先优化运行时而不是等模型升级”的证据库。
状态: 已归档
关联概念: [Harness Engineering, 独立评估器]
关联主题: [Harness Engineering 与 Agent 运行时设计]
---

# Anthropic说：不要在等下一代模型了，立刻马上做Harness！

## 1. 为什么值得保存 (Why Save This)
- **保存理由**：数据密度高，适合做“为什么当前阶段要先优化运行时而不是等模型升级”的证据库。
- **知识挂点**：优先挂到 [[Concepts/Harness Engineering]]、[[Concepts/独立评估器]]。
- **专题位置**：当前更直接服务于 [[Topics/Harness Engineering 与 Agent 运行时设计]]。

## 2. 核心机制与论证链 (Core Logic)
### 方案推导链条 (AI分析)
- **初始痛点**：同一个模型、同一份提示词，在不同运行方式下表现差距极大，说明瓶颈已经从模型能力转向系统外壳。
- **演进尝试**：行业先经历 Prompt Engineering，再经历 Context Engineering，最终走到 Harness Engineering——把约束、反馈和验收机制提升为主角。
- **底层逻辑**：只要任务仍在模型能力边界附近，就必须把生成和评估拆开，用独立 evaluator、可执行验收和严格反馈闭环去抵消模型的自我高估。

### 反事实推演 (Counterfactual Timeline)
- **第 1 周**：团队误以为“换下一代模型就能解决问题”，忽略运行时设计。
- **第 4 周**：工具、CI、评估器和上下文管理仍然失控，昂贵模型也只是更快地产生错误。
- **第 12 周**：组织发现自己买到了更强的模型，却没有买到更可靠的交付。

## 3. 关键证据 / 案例 / 事实 (Evidence)
| 指标 | 数值 | 来源/条件 | 可信度评级 |
|------|------|----------|-----------|
| 同模型换壳收益 | 42% → 78% | Nate B Jones 对比不同 Harness 的成功率 | ⭐⭐⭐ |
| OpenAI Codex 产出规模 | 5 个月 / 约 100 万行代码 / 1500 个 PR | Agent 生成、人工不直接写代码 | ⭐⭐⭐ |
| Stripe 约束策略 | 每周 1300+ PR，CI 最多两轮 | 失败一次自动修复，再失败就转人类 | ⭐⭐⭐ |

## 4. 适用边界与反模式 (Boundaries)
- **反模式**：让 generator 自己宣布“我已经写好了”，再把这句话当作验收结果。
- **适用边界**：模型边界以内的任务，旧 Harness 约束可能会被淘汰；但边界附近任务仍需要 evaluator 和反馈系统。
- **利益冲突/偏见**：文章是行业案例综述，部分数字来自二手研究或公司博客，适合用来建方向判断，不适合做严格 benchmark 复现实验。
- **替代方案对比**：等模型升级可能会淘汰一部分旧护栏，但不会消灭“边界附近任务”对评估器和运行时的需求。
- **最大陷阱**：把 Noam Brown 的“拐杖论”理解成今天就不做 Harness，而不是动态重构 Harness。

## 5. 我可以怎么复用 (Reuse Actions)
### 最小可运行原型 (PoC)
```python
plan = planner.expand(requirement)
code = generator.build(plan)
report = evaluator.verify(
    code,
    checks=["ui_flow", "api_state", "database_state"],
)
if not report.pass_:
    generator.fix(report)
```

### SMART 行动清单 (AI建议)
| 行动项 | 预估时间 | 验收标准 | 失败信号 |
|-------|----------|---------|---------|
| 给关键任务补独立 evaluator，并让它执行真实交互验证而不是截图打分 | 1 个迭代 | bug 报告能落到具体交互和具体代码位置，而不是停留在“感觉有问题” | generator 仍能在没有外部验收的情况下自我宣布完成 |

## 6. 关联概念与主题 (Knowledge Hooks)
| 概念 | 第一性原理定义 | 关系 | 关联笔记 |
|-----|--------------|------|----------|
| Harness Engineering | 通过运行时设计决定模型最终可交付质量 | 主概念 | [[Concepts/Harness Engineering]] `(depends[强]: 文中所有数据都指向“壳的回报率高于等模型” )` |
| 独立评估器 | 把“写”与“评”拆开，让评估靠执行而不是靠自评 | 关键机制 | [[Concepts/独立评估器]] `(implements[强]: Anthropic 证明严格 evaluator 比自我批评更容易训练)` |

- **金句关联**: "Agent 不难，Harness 才难。" —— 出处: [[2026-03-25-Anthropic-立刻做-Harness]]
- 逻辑考点 (Anki): 为什么 evaluator 不能只看截图？ -> 因为功能正确性常藏在真实交互、API 状态和数据库结果里，表面 UI 通过不等于系统可用。
