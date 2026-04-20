# T4 前工作区基线（2026-04-20）

## 目标

这份基线用于冻结 **T4 开始前** `MyObsidian` 工作区已经存在的混合脏状态。

后续进入 T4 内容产出时：

- 不应把这里列出的既有 dirty set 误判为 T4 新增问题
- 应优先审查 **T4 明确选择的目标输入、目标输出和对应 meta 产物**
- 若 T4 期间需要做回归或 diff，对比起点以本基线为准，而不是假设工作树已经全绿

## 锚点

- `MyObsidian` 当前 HEAD：`6817b496f55019cdd18a517e3ecb7bd288eac06c`
- Distill skill 当前 HEAD：`c8813881e28e370c3918fc7de6e325553ee99a6f`
- 工作区 `Distill/.distill-version`：`9.1.0`
- 捕获时间：`2026-04-20`

## 当前 dirty set 概览

### 1. 编辑器 / 个人噪声

这类文件不应进入 T4 产出审查口径：

- `.obsidian/workspace.json`
- `.DS_Store`
- `13沉淀笔记/2025面试/面试题todo.md`

### 2. Distill 仓库接盘与基础设施改动

这类文件属于接盘期留下的 repo / hook / spec / workspace 集成改动，不应与 T4 内容产出混审：

- `Distill/.distill-version`
- `Distill/.gitignore`
- `.claude/`
- `.codex/`
- `.github/`
- `AGENTS.md`
- `docs/superpowers/specs/2026-04-15-feishu-task-lifecycle-design.md`
- `docs/superpowers/specs/2026-04-15-feishu-terminal-dual-channel-session-broker-design.md`
- `docs/superpowers/specs/2026-04-17-distill-closeout-guarantee-design.md`
- `docs/superpowers/specs/2026-04-18-codex-closeout-hook-guarantee-design.md`
- `scripts/`

### 3. 知识内容与 backlog 输入

这批文件代表 Copilot 接盘前后的内容工作残留。进入 T4 时，应把它们视为**既有基线**，而不是本轮新生成内容：

已修改的知识内容：

- `Distill/03-Knowledge/Concepts/AI Agent.md`
- `Distill/03-Knowledge/Concepts/Agent Skills.md`
- `Distill/03-Knowledge/Concepts/Agent 框架选型.md`
- `Distill/03-Knowledge/Concepts/Harness Engineering.md`
- `Distill/03-Knowledge/Concepts/MCP.md`
- `Distill/03-Knowledge/Concepts/Managed Agents.md`
- `Distill/03-Knowledge/Concepts/Sub-Agent 编排.md`
- `Distill/03-Knowledge/Concepts/渐进式 Spec.md`
- `Distill/03-Knowledge/Concepts/独立评估器.md`
- `Distill/03-Knowledge/Topics/AI 编码工程化与 Agent 体系选型.md`
- `Distill/03-Knowledge/Topics/Android Framework 进程、消息、窗口与渲染主线.md`
- `Distill/03-Knowledge/Topics/Android 性能优化与运行时机制.md`
- `Distill/03-Knowledge/Topics/Harness Engineering 与 Agent 运行时设计.md`
- `Distill/03-Knowledge/Topics/知识图谱总纲.md`

已存在但未跟踪的 backlog 输入：

- `Distill/01-Queue/AI Afent 技术哲学.md`
- `Distill/01-Queue/Building multi-agent systems: When and how to use them.md`
- `Distill/01-Queue/Claude Managed Agents：get to production 10x faster.md`
- `Distill/01-Queue/llm-wiki.md`

### 4. 派生 / Meta 产物

这批文件属于 verify / lint / health-check / golden sample / debug 相关输出，进入 T4 时要按“派生产物”口径看，不应与 learner-facing 正文混审：

- `Distill/99-Meta/review-log.json`
- `Distill/99-Meta/golden-samples/`
- `Distill/99-Meta/health-reports/2026-04-14.md`
- `Distill/99-Meta/health-reports/2026-04-15.md`
- `Distill/99-Meta/health-reports/2026-04-17.md`
- `Distill/99-Meta/health-reports/2026-04-18.md`
- `Distill/99-Meta/hook-debug.log`
- `Distill/99-Meta/index.json`
- `Distill/99-Meta/index.md`
- `Distill/99-Meta/lint-report.json`
- `Distill/99-Meta/lint-report.md`
- `Distill/99-Meta/log.md`
- `Distill/99-Meta/refactor-baseline/`

## T4 审查建议

进入 T4 后，优先把审查边界收敛到：

1. 本轮明确选择的 `01-Queue` 输入
2. 与该输入对应的新 / 改 `Sources`、`Concepts`、`Topics`、`Guides`
3. 与这些目标文件直接相关的 lineage、review、index、lint、health-check 变化

不要把以下内容混进 T4 主审查面：

- 编辑器状态文件
- 个人笔记
- 接盘期基础设施改动
- 本基线中已经存在的旧知识稿件脏改

## 结论

T4 开始前，`MyObsidian` 不是“干净工作树”，但现在已经有了明确基线。

因此：

- Distill 机制层面可以进入 T4
- T4 的关键不是先把整个工作区清空，而是严格限定本轮目标输入和目标输出
- 后续任何 T4 复盘，都应先对照本文件判断“这是既有遗留，还是本轮新增”
