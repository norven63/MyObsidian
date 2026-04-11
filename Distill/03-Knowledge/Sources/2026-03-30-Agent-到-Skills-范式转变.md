---
标识: 2026-03-30-Agent-到-Skills-范式转变
标题: 学习笔记：从 Agent 到 Skills — AI 智能体架构的范式转变
来源: https://mp.weixin.qq.com/s/RMh2JqHwkjonPTZlwVKxsw
作者: 元丹
发布方: 阿里云开发者
日期: 2026-03-30
优先级: P0
评估理由: 视角覆盖 Skill、MCP、OpenClaw、A2A 和多层协议栈，是理解 2026 Agent 基础设施分层的优质全景文档。
状态: 已归档
关联概念: [Agent Skills, MCP, Sub-Agent 编排]
关联主题: [Harness Engineering 与 Agent 运行时设计]
---

# 学习笔记：从 Agent 到 Skills — AI 智能体架构的范式转变

## 1. 为什么值得保存 (Why Save This)
- **保存理由**：视角覆盖 Skill、MCP、OpenClaw、A2A 和多层协议栈，是理解 2026 Agent 基础设施分层的优质全景文档。
- **知识挂点**：优先挂到 [[Concepts/Agent Skills]]、[[Concepts/MCP]]、[[Concepts/Sub-Agent 编排]]。
- **专题位置**：当前更直接服务于 [[Topics/Harness Engineering 与 Agent 运行时设计]]。

## 2. 核心机制与论证链 (Core Logic)
### 方案推导链条 (AI分析)
- **初始痛点**：把所有知识、工具逻辑和 API 集成都塞进单体 Agent，会浪费上下文、难以复用、也难以维护。
- **演进尝试**：行业先用 MCP 统一工具连接，再用 Skills 把专业知识从 Agent 主体中拆出来，最后用运行框架承接多通道、记忆与沙箱。
- **底层逻辑**：把“决定做什么”“教怎么做”“用什么做”“在哪里做”拆成不同层——Agent、Skills、MCP、OpenClaw/运行环境，各层只负责自己的稳定职责。

### 反事实推演 (Counterfactual Timeline)
- **第 1 周**：团队用单体 Prompt 堆出一个能跑的 Agent。
- **第 4 周**：每加一种渠道或工具都要回头改主 Agent，知识和集成一起爆炸。
- **第 12 周**：没有技能包和协议分层的系统，会在多渠道、多任务、多 Agent 场景下迅速失控。

## 3. 关键证据 / 案例 / 事实 (Evidence)
| 指标 | 数值 | 来源/条件 | 可信度评级 |
|------|------|----------|-----------|
| Agent Skills 行业采纳速度 | 48 小时内被 Microsoft、OpenAI 采纳 | Anthropic 开放标准发布后的行业响应 | ⭐⭐⭐ |
| 行业趋势判断 | 2026 年 75% AI 项目聚焦可组合 Skills | 文中援引 Gartner 预测 | ⭐⭐ |
| MCP 生态规模 | 9700 万+ 月 SDK 下载量，10000+ 活跃 MCP Server | 截至 2026 年初的生态统计 | ⭐⭐⭐ |
| Filesystem MCP 实测能力 | 14 个 Tools | 2026-02-26 的工具发现结果 | ⭐⭐⭐ |

## 4. 适用边界与反模式 (Boundaries)
- **反模式**：把静态知识和动态工具都塞进 MCP，或者反过来把实时连接能力误做成 Skill 文档。
- **适用边界**：能写成脚本跑完的业务能力优先做 Skill；需要持续连接外部系统的能力优先做 MCP；真正的多通道长任务再交给运行框架。
- **利益冲突/偏见**：文章对 OpenClaw 生态有明显好感，部分平台对比更偏“架构说明”而非严格 benchmark。
- **替代方案对比**：单体 Agent 上手最快但不可复用；Skill+MCP 分层让知识与接口都能独立演化；运行框架把二者汇成可操作的系统。
- **最大陷阱**：为了“统一”而过早把一切放进一个平台，结果知识层、工具层和运行层互相耦合。

## 5. 我可以怎么复用 (Reuse Actions)
### 最小可运行原型 (PoC)
```yaml
skill:
  name: deploy-to-production
  level1: 元数据
  level2: 部署步骤与回滚策略
  level3: scripts/deploy.sh
mcp:
  filesystem: list_directory, read_file, search_files
runtime:
  agent: 负责匹配 skill
  sandbox: 负责执行脚本与文件读写
```

### SMART 行动清单 (AI建议)
| 行动项 | 预估时间 | 验收标准 | 失败信号 |
|-------|----------|---------|---------|
| 先拆出 1 个高频 Skill 和 1 个稳定 MCP，再把它们挂进统一运行框架 | 1 个迭代 | Agent 能按需加载知识、稳定调用工具、且替换任一层不会拖垮其他层 | 一次新增渠道或能力仍需回改主 Agent Prompt 与硬编码脚本 |

## 6. 关联概念与主题 (Knowledge Hooks)
| 概念 | 第一性原理定义 | 关系 | 关联笔记 |
|-----|--------------|------|----------|
| Agent Skills | 把领域知识、最佳实践和脚本封装为可按需加载的能力包 | 知识层 | [[Concepts/Agent Skills]] `(depends[强]: 文章把 Skill 定位为“员工培训手册” )` |
| MCP | 让 Agent 以标准协议连接外部工具和数据源 | 工具层 | [[Concepts/MCP]] `(depends[强]: 文章把 MCP 定位为“AI 的 USB-C” )` |
| Sub-Agent 编排 | 让复杂任务在独立上下文中并行推进再汇总 | 执行层 | [[Concepts/Sub-Agent 编排]] `(implements[中]: DeerFlow 的独立 sub-agents 和 A2A 场景是文中最直接的跨上下文协作证据；Skill 内部的 Director/Creator/Critic 更接近 Prompt 级角色分工)` |

- **金句关联**: "MCP 是递给你一把锤子，Skill 是教你怎么用这把锤子。" —— 出处: [[2026-03-30-Agent-到-Skills-范式转变]]
- 逻辑考点 (Anki): 为什么 Skill 和 MCP 不该互相取代？ -> 因为 Skill 负责静态知识与流程说明，MCP 负责动态连接与运行时查询，它们解决的是不同层级的问题。
