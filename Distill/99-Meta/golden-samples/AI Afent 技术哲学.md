---
类型: golden-sample
标题: AI Agent 技术哲学
原始路径: Distill/01-Queue/AI Afent 技术哲学.md
状态: reference-only
适用资产:
  - Topic
  - Guide
  - Prompt template
登记日期: 2026-04-19
---

# Golden Sample：AI Agent 技术哲学

## 定位

这份样本是一个高质量的 **AI Agent / Harness Engineering 复合型 Wiki 草稿**，用于给后续 Distill 内容产出提供质量参照。

它不是普通 backlog，也不是要被 Distill 拿来“证明自己能改好”的测试输入。原文已经具备较强结构和表达质量，应作为标杆保留。

## 原始样本

- 原始文件：`Distill/01-Queue/AI Afent 技术哲学.md`
- 当前处理策略：保留原文，不移动、不改写、不归档到 `已完成/`
- 默认用途：质量参考、结构参照、T4 产出评估的对照样本

## 代表的质量标准

1. **读者定位清楚**：面向开发者，且有“架构导师”协作人设。
2. **主线完整**：从 Agent 定位、Harness 哲学、五大模块，到工作流、安全、可观测性和里程碑。
3. **判断矩阵丰富**：包含造轮子 vs 买轮子、多 Agent 判据、规划模式、合规检查。
4. **行动性强**：提供流程、检查清单、Prompt 模板、反模式和里程碑。
5. **表达产品化**：读起来像一份能直接指导协作的 Wiki / playbook，而不是松散摘要。

## 不应照抄的地方

1. 不把它的章节结构强制套给所有 Topic 或 Guide。
2. 不要求 Sources / lineage / index / health report 也具备同等人读优雅度。
3. 不把该样本直接放入 `@skill/templates/`；它是实例级样本，不是通用模板。
4. 不直接作为首个 Guide 链路验证材料，因为它本身已经很成熟，无法证明 Distill 能把低质量输入提升到高质量输出。

## 暴露出的当前 Distill 差距

当前 Distill 的 `Concept / Topic` 产出已有可验证高质量样本；`Guide` 作为 9.1.0 新增一等资产，规则、模板和 hook 已具备，但真实工作区中 `Guides: 0`，尚缺首个完整实战样本。

因此，下一个 T4 不应以本文件作为测试对象，而应选择质量较低、结构较散但行动潜力明确的输入，跑通：

1. 原料解析。
2. Topic / Guide 选型。
3. `on_guide_written` 或对应 hook。
4. review gate。
5. health-check / validate-distill。
6. closeout receipt。

## 使用方式

后续评估 T4 产物时，可用本样本回答四个问题：

1. 产物是否有清楚读者定位？
2. 产物是否把判断顺序讲清，而不是只堆概念？
3. 产物是否提供可执行矩阵、清单、Prompt 或操作骨架？
4. 产物是否知道哪些内容应写给人，哪些内容应留给 agent-facing meta 层？
