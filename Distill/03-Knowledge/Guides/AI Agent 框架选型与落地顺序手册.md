---
标识: guide-agent-framework-selection-rollout
标题: AI Agent 框架选型与落地顺序手册
标签: [guide, agent-framework]
来源:
  - '(depends) [[Sources/2026-04-09-AI-Agent-入门与框架选型]]'
  - '(depends) [[Sources/2026-04-03-Qoder-Harness-Engineering-指南]]'
  - '(depends) [[Sources/2026-03-30-Agent-到-Skills-范式转变]]'
  - '(depends) [[Sources/2026-03-31-字节-Harness-Agent-54k-Star]]'
  - '(depends) [[Sources/2026-02-04-Scaling-Managed-Agents-Decoupling-the-brain-from-the-hands]]'
关联概念:
  - '(depends) [[Concepts/AI Agent]]'
  - '(depends) [[Concepts/Agent 框架选型]]'
  - '(depends) [[Concepts/Harness Engineering]]'
  - '(depends) [[Concepts/Agent Skills]]'
  - '(depends) [[Concepts/Sub-Agent 编排]]'
关联主题:
  - '(depends) [[Topics/AI 编码工程化与 Agent 体系选型]]'
状态: stable
更新日期: 2026-04-21
---

# AI Agent 框架选型与落地顺序手册

> 这份手册不回答“哪个框架最先进”，只回答一件事：**你现在到底该先补仓库内基线，还是该上工作流框架、多 Agent 框架、数据层，或者直接把运行时治理升级出去**。

## 什么时候该拿出这份手册
### 0.1 适用对象
- 已经在做 AI 编码、研究代理或业务自动化，开始认真讨论 LangChain、LangGraph、CrewAI、AutoGen、LlamaIndex 一类框架的人。
- 发现团队选型讨论越来越热闹，但始终说不清当前问题到底属于任务契约、长期知识、执行护栏还是协调承载的维护者。

### 0.2 触发信号
- 同一个团队一会儿想上多 Agent，一会儿又想补 RAG、补 Skill、补 workflow，但没人能说明“这次为什么先选这个”。
- 当前仓库内 Agent 已经不是完全不可用，但开始出现状态分支多、任务链长、角色冲突、知识检索重、恢复成本高等不同方向的复杂度。

### 0.3 非目标 / 不适用
- 不用于 benchmark、模型排行榜、品牌偏好讨论。
- 不用于一次性 demo、低风险脚本或还没建立最小 Spec / Skills / Harness 的场景。

### 0.4 前置准备
- 关联 Topic：(depends) [[Topics/AI 编码工程化与 Agent 体系选型]]
- 先读 Source：(depends) [[Sources/2026-04-09-AI-Agent-入门与框架选型]]
- 如果你连“第一次偏航发生在哪一层”都还说不清，先回到 (depends) [[Guides/AI 编码返工分诊与分层补强手册]]，不要直接拍框架。
- 如果你已经确定问题主要出在长会话、权限、恢复和运行时治理，再把升级分支交给 (depends) [[Guides/单 Agent、Sub-Agent 与 Managed Agents 升级选择手册]]。

## 先决定你要选的是“哪一类问题”
### 1.1 决策矩阵 / Decision Matrix
| 场景 / 症状 / 上下文 | 先看什么 | 选择路径 / 动作 | 为什么这么选 |
|---------------------|----------|-----------------|--------------|
| 返工主要表现为范围不清、验收模糊、补一处坏三处 | 最近 2-3 次失败样本的第一次偏航点 | **先别选框架**，先走 [[Guides/AI 编码返工分诊与分层补强手册]] | 这类问题首先是契约和治理层问题，热门框架不会自动帮你写清楚任务边界 |
| 模型总忘仓库规则、命令顺序、领域术语、长期背景 | 是否反复把同一批背景塞回聊天上下文 | **先补 Skills / repo-native Harness**，不要急着换框架 | [[Sources/2026-03-30-Agent-到-Skills-范式转变]] 已经说明：静态知识、脚本和工具连接本来就不是同一层 |
| 一个任务里开始出现显式状态流转、检查点、条件分支和回退恢复 | 工作流是否能画成有向图，且每步输入输出可描述 | **优先选 workflow / graph 类框架** | 这类问题首先是状态机与恢复语义，不是角色越多越好 |
| 子任务天然可并行，角色输入输出清楚，主上下文被高噪声探索拖垮 | 子任务能否独立验收并返回摘要 / verdict / diff | **优先选多 Agent / Sub-Agent 编排类框架** | 多 Agent 的主要收益是上下文隔离和搜索面扩展，不是“角色名字更完整” |
| 主要压力来自知识检索、文档索引、结构化数据访问和 RAG | 问题核心是不是“模型找不到稳定事实” | **优先上数据 / 检索层，而不是先拆多 Agent** | 数据层解决的是“知道什么”，不是“怎么编排谁来做” |
| 团队已经在反复造 sandbox、session、权限、凭证、trace、恢复 | 运行时治理是否已经吞掉交付节奏 | **先评估托管 runtime / Managed Agents 路线** | 当主成本从生成转到治理，框架家族已经不够，应该看承载层 |

### 1.2 默认路径
- **默认路径 / 首选**：先用仓库内 Spec + Skills + Harness 证明问题真的已经超出基线，再决定引入哪一类框架。
- **什么时候不要走默认路径**：如果你的任务已经稳定命中“显式状态机 / 并行角色 / 数据密集检索 / 运行时治理”其中之一，就不要继续用一个模糊的“全能 Agent”硬扛。

## 按阶段把选型顺序走对
### 2.1 先分清是任务问题、知识问题，还是承载问题
- **进入信号 / Entry Cue**：团队已经开始说“得换框架了”，但还没人能把当前失败样本归位到具体复杂度。
- **动作 / Action**：
  1. 从最近 2-3 条真实任务里，标出第一次偏航是发生在任务契约、长期知识、执行护栏还是协调 / runtime。
  2. 如果当前 Agent 主要问题是“看不见仓库规则”和“动作后没人拦”，优先回看 [[Sources/2026-04-03-Qoder-Harness-Engineering-指南]]，先把 repo-native Harness 补稳。
- **完成证据 / Exit Evidence**：你能明确写出一句话版本的主瓶颈，例如“这是状态机问题”“这是长期知识供给问题”“这是运行时治理问题”。

### 2.2 按复杂度选择框架家族，而不是按热度选品牌
- **进入信号 / Entry Cue**：已经确认当前主瓶颈不再是单纯的 Spec / Skills 缺位，而是 workflow、multi-agent、data access 或 runtime 之一。
- **动作 / Action**：
  1. 如果主问题是显式状态流转、检查点和可恢复分支，优先选 workflow / graph 类；[[Sources/2026-03-31-字节-Harness-Agent-54k-Star]] 给了节点状态和 checkpoint 的直接证据。
  2. 如果主问题是高噪声探索、角色冲突和独立子任务，优先选多 Agent / Sub-Agent 类；如果主问题是知识检索与索引，先让数据层承接，不要用多 Agent 伪装数据问题。
- **完成证据 / Exit Evidence**：你不仅能说“选什么”，还能说“为什么另外两类不是这次的主答案”。

### 2.3 只在一条真实工作流上做最小试点
- **进入信号 / Entry Cue**：已经选定框架家族，但还没有任何真实任务证明它值得长期接入。
- **动作 / Action**：
  1. 只选一条工作流做试点，并提前定义单一主指标，例如恢复成本、上下文长度、并行吞吐或知识命中率。
  2. 保留现有 repo-native Harness，不要把验证、权限和回退一股脑交给新框架；[[Sources/2026-04-03-Qoder-Harness-Engineering-指南]] 的结论很直接：框架不是替代护栏，而是承载护栏。
- **完成证据 / Exit Evidence**：这条试点能清楚给出一项确定收益，同时没有把仓库规则、验证和权限边界重新藏回 prompt。

### 2.4 升级条件 / 何时求助
- **进入信号 / Entry Cue**：框架家族本身已经选对，但团队真正痛的是 session 恢复、sandbox、安全边界、trace 和跨环境接入。
- **动作 / Action**：
  1. 用 [[Sources/2026-02-04-Scaling-Managed-Agents-Decoupling-the-brain-from-the-hands]] 去盘点：当前主成本是不是已经从“怎么编排”变成“怎么治理长期运行对象”。
  2. 一旦确认是运行时治理问题，就把后续动作交给 [[Guides/单 Agent、Sub-Agent 与 Managed Agents 升级选择手册]]，不要继续在框架层打转。
- **完成证据 / Exit Evidence**：你能明确说明“这已经不是框架 API 手感问题，而是 session / sandbox / 权限 / 恢复的系统问题”。

## 每次选型前都要过的检查清单
### 3.1 执行前 / Preflight
1. 只选一条真实工作流，不要用“未来所有 Agent 场景”做抽象目标。 —— 证据 / 完成标志：有一条明确任务链和 2-3 个失败样本。
2. 把主瓶颈写成单一句子，并且句子里不能同时出现 workflow、multi-agent、RAG、runtime 四种词。 —— 证据 / 完成标志：问题描述只有一个主复杂度。

### 3.2 执行中 / Execution
1. 这次试点只允许引入一个框架家族，不要同时上 workflow、multi-agent 和 data layer。 —— 证据 / 完成标志：方案里只有一个主承载层，其余层继续沿用现有基线。
2. 保留现有 repo-native 验证、权限和回退动作。 —— 证据 / 完成标志：测试、review、权限边界仍在仓库侧可见，不依赖框架黑盒兜底。

### 3.3 执行后 / Done Check
1. 说明这次试点到底减少了什么：上下文噪声、恢复工时、知识遗漏，还是协调冲突。 —— 证据 / 完成标志：至少有一项明确下降的成本或一项明确提升的稳定性。
2. 写清哪些问题仍没有解决。 —— 证据 / 完成标志：复盘里有未解决项，而不是“整体更先进了”。

## 最容易选错的姿势
### 4.1 反模式 / 不要这样做
1. **因为社区热度高，就默认它适合你。** —— 为什么错：[[Sources/2026-04-09-AI-Agent-入门与框架选型]] 已经把工作流、多 Agent、数据访问拆成不同形态，热度不是问题分类。
2. **把多 Agent 当成知识缺口的默认补丁。** —— 为什么错：如果模型缺的是稳定背景和仓库规则，多拆几个角色只会复制同样的无知。
3. **把框架接进来以后，就让它顺手替代仓库侧 Harness。** —— 为什么错：这样会把验证、权限和恢复重新藏进黑盒，短期省事，长期更难治理。

### 4.2 失败信号 / 异常现象
1. **框架已经接了，但团队仍在每次任务前重讲仓库规则和业务上下文。** —— 先排查：这是不是其实应该先补 [[Sources/2026-03-30-Agent-到-Skills-范式转变]] 所说的 Skill / 知识供给层。
2. **角色数越来越多，主协调者却比以前更忙。** —— 先排查：是不是把无法独立验收的子任务硬拆成多 Agent，结果协调成本反而上升。
3. **workflow 已经画出来，但真正的痛点还是权限、session 恢复和 trace。** —— 先排查：你是不是已经越过框架层，应该升级到托管 runtime 语义了。

### 4.3 回退 / 恢复 / 升级条件
- 如果试点结束后说不清到底减少了哪一类成本，就回退，不要为了“路线先进”继续扩大接入。
- 如果新框架把仓库规则、验证脚本和权限边界重新压回 prompt 或平台黑盒，就暂停扩张，先补回 repo-native Harness。

## 可以直接复用的判断 Prompt 与输出骨架
### 5.1 可复用模板 / Prompt / 命令
```text
请先不要推荐具体品牌，先把当前问题归位到以下五类之一：
1. 任务契约不清
2. 长期知识 / Skill 供给不足
3. workflow / 状态机 / checkpoint
4. multi-agent / context isolation / 并行角色
5. runtime governance / session / sandbox / 权限 / trace

然后只输出：
- 当前主复杂度
- 这次应该选的框架家族
- 这次不该选的两类替代路线
- 需要保留的 repo-native Harness
- 单工作流试点方案
```

### 5.2 产物骨架 / 输出格式
```text
当前主瓶颈：
- ...

推荐家族：
- repo-native / workflow / multi-agent / data-layer / managed-runtime

为什么现在选它：
- ...

为什么现在不选另外两条路：
- ...

最小试点：
- 任务：
- 指标：
- 成功标准：
- 回退条件：
```

## 术语对齐与继续深挖
### 6.1 术语统一
| 术语 | 在本文里的含义 | 不要混淆 |
|------|----------------|----------|
| repo-native 基线 | 在仓库里用 Spec、Skills、Harness 直接治理任务，不额外引入重框架 | 不是“只有 prompt，没有脚本和验证” |
| workflow / graph 类 | 把状态流转、分支、checkpoint、恢复写成显式执行图的承载层 | 不是“只要有多个步骤就必须上 graph” |
| multi-agent 类 | 让多个上下文隔离的执行单元分工协作的承载层 | 不是角色名字越多越高级 |
| data-layer / RAG 类 | 为知识检索、索引、结构化数据访问提供稳定底座的承载层 | 不是 workflow 或 runtime 的替代品 |

### 6.2 深挖入口 / 证据锚点
- (depends) [[Guides/AI 编码返工分诊与分层补强手册]] —— 用它先判断这次到底是不是框架问题。
- (depends) [[Guides/单 Agent、Sub-Agent 与 Managed Agents 升级选择手册]] —— 当复杂度已经进入协调 / runtime 层时，把后续升级动作交给它。
- (depends) [[Sources/2026-04-09-AI-Agent-入门与框架选型]] —— 用它拿到“按问题形态拆框架家族”的入门地图。
- (depends) [[Sources/2026-04-03-Qoder-Harness-Engineering-指南]] —— 用它校正一个关键前提：框架不能代替仓库侧 Harness。
- (depends) [[Sources/2026-03-30-Agent-到-Skills-范式转变]] —— 用它判断为什么 Skill、脚本和工具连接本来就该分层，而不是全塞给同一框架。
- (depends) [[Sources/2026-03-31-字节-Harness-Agent-54k-Star]] —— 用它理解 workflow / checkpoint / 节点状态何时真的值得显式建模。
- (depends) [[Sources/2026-02-04-Scaling-Managed-Agents-Decoupling-the-brain-from-the-hands]] —— 当问题已经进入 session / sandbox / 权限 / 恢复时，用它判断为什么这已经不是框架语法层问题。
