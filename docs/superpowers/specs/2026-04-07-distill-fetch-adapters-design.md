# Distill 抓取适配框架设计

## 1. 背景

Distill 的核心能力之一不是“生成笔记”，而是先稳定、完整地获取链接中的原文内容。现状中，`FetchURL` 被抽象成一个单点能力，但真实站点（尤其是微信）会根据请求头、Referer、页面结构和反爬策略返回完全不同的页面：正文页、验证码壳页、登录页、部分内容页。结果是：同一个 URL，在不同 Agent、不同请求姿势下，抓取质量差异很大。

最近的评测结论说明，问题的关键不在“绑定哪一个 Agent”，而在“是否有站点适配方案”：

- 默认本地直抓（普通桌面 UA）对微信样本集几乎全部失败
- 站点适配后的本地直抓（微信移动端请求策略）能稳定拿到正文
- Kimi/Copilot 也能作为高质量兜底，但更适合补完与校验，不应成为唯一抓取底座

因此，Distill 需要把抓取从“隐式经验”升级为“显式制度”。

## 2. 目标

本设计要实现以下目标：

1. 为 Distill 增加一层独立的**站点抓取适配框架**
2. 让已确认有效的站点规则成为**运行时硬约束**
3. 把抓取经验写成**可维护、可审计、可升级**的文档资产
4. 以**质量优先**而不是成本优先的方式组织抓取链
5. 允许规则老化被自动识别，并自动生成升级候选

## 3. 非目标

本设计不包含以下内容：

1. 不尝试一次性支持大量站点；首版只内置微信规则
2. 不把某个特定 Agent（Kimi/Copilot）写死为唯一正式抓取器
3. 不允许站点规则自动修改后直接上线生产
4. 不改动 Sources / Concepts / Topics 的知识归档结构

## 4. 设计原则

### 4.1 质量优先

抓取链排序以**保真度、稳定性、可验证性**为核心，而不是只以成本排序。

### 4.2 Agent 解耦

Agent 可以参与抓取兜底，但 Distill 不能把核心抓取能力绑定到某个特定 Agent 上。

### 4.3 规则分层

抓取规则要拆分为稳定的通用质量门、可演进的站点适配规则和独立的 fallback 链，避免单点失效拖垮整体抓取。

### 4.4 规则可观测

每次抓取都必须留下命中的规则、质量判断和降级路径，方便识别规则老化。

## 5. 整体架构

新增一个独立的抓取策略层，位于 URL 输入与步骤 2 内容解析之间：

`URL -> 站点识别 -> 专用 adapter -> 通用直抓 -> Agent fallback -> 结构化正文`

组件拆分如下：

1. **站点识别器**
   - 根据 URL 域名命中站点类型
   - 示例：`mp.weixin.qq.com -> wechat`

2. **站点专用 adapter**
   - 按站点执行专用请求策略和解析逻辑
   - 示例：微信使用移动微信风格请求头、Referer、正文容器提取

3. **通用直抓器**
   - 未命中站点规则时的默认抓取器
   - 已知站点专用 adapter 失败时的第二层降级

4. **Agent fallback 层**
   - 高成本兜底层
   - 不绑定到具体 Agent，仅定义“Agent 兜底接口”

5. **质量门**
   - 对抓取结果做可机械执行的判定
   - 决定是否采用、补完或继续降级

6. **遥测与规则老化检测**
   - 记录每次抓取的命中规则与结果
   - 按域名累计异常信号

### 5.1 统一抓取结果协议（Canonical Fetch Result）

步骤 2 不再直接消费“某个抓取器返回的原始 HTML/文本”，而只消费统一的抓取结果对象。  
无论结果来自站点 adapter、通用直抓还是 Agent fallback，都必须先归一化到同一协议，再进入解析。

统一协议必须至少包含以下字段：

- `source_url`: 原始 URL
- `final_url`: 最终落地 URL
- `site_id`: 命中的站点标识（如 `wechat` / `generic`）
- `fetch_layer`: 结果来源层（`adapter` / `generic` / `agent_fallback`）
- `rule_version`: 命中的规则版本
- `request_profile_id`: 本次请求使用的策略标识
- `artifact_id`: 本次抓取产物标识
- `artifact_hash`: 抓取产物哈希
- `page_type`: `article / captcha / login / shell / partial / unknown`
- `title`
- `author_byline`
- `publisher_name`
- `published_at`
- `body_text`
- `body_html_ref`
- `body_excerpt_ref`
- `field_provenance`: 每个字段来自哪个页面字段/抓取层
- `field_confidence`: 每个字段的置信度
- `field_evidence_refs`: 每个字段的页面证据定位
- `quality_score`
- `hard_fail_reasons`
- `soft_fail_reasons`
- `candidate_id`

说明：

1. `author_byline` 与 `publisher_name` 必须分开，避免公众号名和作者署名相互污染。
2. Step 2 解析时，必须基于该协议做确定性映射，而不是直接对原始 HTML 做临时推断。
3. 任何未归一化的结果都不能进入 Distill 的知识流程。
4. `agent_fallback` 候选只有在字段具备页面证据时，才允许进入正式候选池。
5. 页面证据必须能回指到带哈希的抓取产物，不能只是一段不可核验的自然语言说明。

### 5.1.1 Agent fallback 的准入边界

Agent fallback 是高成本抓取器，不是自由总结器。  
其结果只有满足以下条件时，才允许参与正式仲裁：

1. `body_text` 必须是 extractive 结果，而不是模型综合或改写后的正文
2. 关键字段必须提供 `field_evidence_refs`
3. 推断性 metadata 默认降为低置信度，不能覆盖高置信度字段
4. 若无法给出页面证据，则该结果只能用于问题诊断，不能作为正式正文来源
5. 任一 `field_evidence_refs` 若无法在 `artifact_id + artifact_hash` 对应的抓取产物中解析验证，则该候选直接记为硬失败

补充要求：

- `field_evidence_refs` 必须采用可机器校验的形式（如 selector/span/range/xpath/json-path）
- 运行时必须执行 evidence resolver；解析失败即 `HARD_UNVERIFIABLE_EVIDENCE`
- `agent_fallback` 不允许只返回“根据页面可知”之类不可核验的解释性文本

### 5.1.2 抓取产物包与 Evidence Resolver 契约

所有候选结果都必须落为可复核的抓取产物包，建议路径：

- `Distill/02-Processing/fetch-artifacts/<artifact_id>/`

每个产物包至少包含：

- `manifest.json`：`artifact_id`、`source_url`、`final_url`、`normalized_source_url`、`normalized_final_url`、`redirect_chain`、`fetch_layer`、`site_id`、`rule_version`
- `request.json`：请求 profile、headers 摘要、时间戳
- `response.json`：状态码、响应 headers 摘要、内容类型
- `page.raw.html` 或 `page.raw.txt`：原始页面主体
- `page.excerpt.txt`：受控 excerpt
- `normalized.json`：统一抓取结果对象

约束：

1. `artifact_hash` 必须基于产物包的规范化内容生成，同一内容重复写入应得到同一哈希
2. `body_html_ref`、`body_excerpt_ref` 与 `field_evidence_refs` 只允许引用当前产物包中的内容
3. Step 2 解析和后续 review 只能读取产物包，不允许重新联网“补看页面”

Evidence Resolver 输入契约：

- `artifact_id`
- `artifact_hash`
- `ref_kind`
- `ref_value`
- `expected_text_hash`（可选但推荐）

Evidence Resolver 输出契约：

- `resolved = true/false`
- `resolved_text`
- `resolved_range`
- `resolved_from_artifact_hash`
- `failure_reason`（若失败）

若 `resolved = false` 或 `resolved_from_artifact_hash != artifact_hash`，则必须 fail-closed。

### 5.1.3 `artifact_hash` 的规范化定义

`artifact_hash` 是证据校验与离线重放的信任锚，必须使用精确定义：

1. 对 `manifest.json`、`normalized.json` 采用**按 key 排序的 canonical JSON**
2. 文本文件统一使用 `LF` 行尾
3. `artifact_hash` 计算时排除易变字段，如本地绝对路径、写入时间、临时 request id
4. `page.raw.html` / `page.raw.txt` 按落盘后的原始字节参与哈希
5. `artifact_hash` 计算使用：
   - `manifest_core = manifest.json` 去除 `artifact_id`、`artifact_hash`、时间戳、本地路径
   - `normalized_core = normalized.json` 去除 `artifact_id`、`artifact_hash`
   - `artifact_hash = SHA-256(canonical(manifest_core) + canonical(normalized_core) + raw_page_bytes_digest)`

实现要求：

- 同一内容即使写入不同 `artifact_id`，也必须得到相同 `artifact_hash`
- 任一参与字段变化都必须导致 `artifact_hash` 变化
- 哈希规则必须写入测试夹具，不能只存在实现代码中

### 5.2 元数据合并与污染防护

当多个抓取层返回不一致元数据时，不能简单覆盖，必须使用确定性的合并规则：

1. `body_text` 只接受一个主来源，不允许拼接不同抓取层的正文。
2. `title / author_byline / publisher_name / published_at` 允许跨层补完，但必须保留 `field_provenance` 与 `field_confidence`。
3. 若两个候选结果的 `title` 或 `published_at` 冲突明显，则标记为 `metadata_conflict`，禁止静默采用低置信字段。
4. Step 2 输出给知识层时，默认优先：
   - `author_byline`
   - 若缺失则退回 `publisher_name`

该规则的目标是防止“正文来自一层、标题来自另一层、但系统误以为它们天然一致”的静默污染。

### 5.3 同文等价性检查（Candidate Equivalence Gate）

多个候选结果在进入仲裁前，必须先证明它们指向的是同一篇文章，而不是：

- 登录页 / 验证页
- 镜像页 / 缓存页
- 跳错 URL 的另一篇文章
- 结构相似但正文不同的壳页

至少执行以下检查：

1. 规范化 URL / canonical URL 是否一致
2. 标题相似度是否在安全阈值内
3. 日期是否一致或可解释
4. 正文开头片段是否明显属于同一文档
5. 来源域名是否属于原始域名、同源域名或预先批准的镜像域名

来源可信策略：

- 默认只信任 `source_url` 的同源结果
- 若站点存在合法镜像 / AMP / 阅读页，必须在规则中显式登记 approved mirrors
- 跨源跳转但未命中 approved mirrors 的候选，即使正文质量高，也只能进入 `requires_review`
- approved mirrors 不能只按“相似域名”模糊匹配，必须按精确 host 或显式 path 规则匹配

URL 归一化要求：

- scheme / host 小写化
- 默认端口移除
- host 做 punycode 归一化
- fragment 丢弃
- query 默认保留，仅允许按站点规则删除已知 tracking 参数
- mirror 判断必须基于归一化后的 host/path 与完整 redirect chain

未通过等价性检查的候选必须标记为 `candidate_mismatch`，并禁止参与字段合并与正文仲裁。

## 6. 运行时决策流

### 6.1 已知站点

以微信为例：

1. 命中 `wechat` 站点规则
2. 执行 `wechat` adapter 主抓取
3. 通过质量门判定：
   - 成功：直接进入步骤 2 解析
   - 质量不足：进入通用直抓
   - 硬失败：直接进入通用直抓
4. 通用直抓仍失败或质量不足：进入 Agent fallback

### 6.2 未知站点

1. 直接进入通用直抓
2. 质量不足或失败：进入 Agent fallback
3. 若该站点高频出现且价值高，再升级为新的站点 adapter

### 6.3 候选结果仲裁（Best-Result Arbitration）

Distill 不采用“第一层抓到且勉强过门就直接收下”的策略。  
对于已知高价值站点，运行时必须执行**候选结果仲裁**：

1. 当前主抓取层先产出候选结果
2. 若命中硬失败，立即进入下一层
3. 若只命中软失败或质量分落入灰区，可继续请求下一层候选
4. 最终由仲裁器在多个候选结果中选择最佳结果，而不是默认采用先到先得

仲裁器的选择顺序：

1. 剔除所有硬失败候选
2. 优先选择正文结构更完整、连续正文更长、噪音更低的候选
3. 若多个候选正文质量相近，则优先选择 metadata 完整度更高且冲突更少的候选
4. 若依然相近，则优先选择低层抓取（adapter/generic）而不是 Agent fallback
5. 若候选间存在重大元数据冲突，标记为 `requires_review`，不得静默通过

### 6.3.1 抓取预算与停止条件

V1 必须为每个 URL 定义最大抓取预算，避免无界重试：

1. 已知站点：`1 次 adapter + 1 次 generic + 1 次 agent_fallback`
2. 未知站点：`1 次 generic + 1 次 agent_fallback`
3. `gray_zone` 结果最多触发一次额外候选获取

出现以下任一情况时，当前 URL 必须停止继续抓取：

- 某候选在仲裁中明确胜出
- 抓取预算耗尽
- 命中 `requires_review`

### 6.4 与现有 Distill 工作流的契约变化

本设计会改变 Step 1 / Step 2 的内部契约，但不在 V1 直接改动 Step 5 hook 接口：

1. **Step 1**：从“输入 URL”升级为“输入 URL 并产出统一抓取结果对象”
2. **Step 2**：从“消费原始 FetchURL 内容”升级为“消费统一抓取结果对象”
3. **Step 3-7**：继续使用结构化解析结果，不直接感知抓取层细节
4. **Hook 层（Step 5 写入）**：在 V1 中保持接口不变，抓取层问题在进入归档前解决
5. **PDF / 视频等非 URL 输入**：V1 继续走现有路径，不强制接入站点适配框架

因此，实施时必须同时更新：

- `SKILL.md` 中 Step 1/Step 2 描述
- `references/step2-parsing.md` 的输入契约
- 工作区版本与迁移说明

## 7. 质量门设计

质量门必须机械执行，不能依赖“模型感觉”。

### 7.1 硬失败信号

命中即立即降级：

- 命中验证码/环境异常/壳页特征
- 标题为空
- 正文长度接近 0
- 正文主容器缺失
- 返回结果明显不是文章页

### 7.2 软失败信号

累计到阈值再降级：

- 正文长度过短
- 作者/日期缺失
- HTML / 广告 / 导航噪音过高
- 标题与正文明显不匹配
- 结果像摘要而不是连续正文
- 批量模式下出现 URL 与标题/正文疑似串号

### 7.3 质量结果

每次抓取产出结构化质量结果：

- `抓取状态`
- `正文长度`
- `元数据完整度`
- `正文结构完整度`
- `命中的站点规则`
- `质量分`
- `是否触发 fallback`
- `最终采用哪一层结果`

建议判定：

- `90-100`: 直接采用
- `70-89`: 采用，但允许补完
- `< 70`: 继续降级
- `硬失败`: 立即降级

### 7.3.1 `requires_review` 的强制语义

`requires_review` 不是提示性标签，而是强制终止状态。

一旦命中：

1. 当前 URL 不得进入 Step 2 正式解析
2. 不得进入 Step 5 写入与归档
3. 必须写入隔离区等待审核
4. 审核通过前，不得把该结果视为正式知识来源

建议隔离区：

- `Distill/02-Processing/fetch-review-queue/`

审核出口契约：

1. 审核必须输出明确结论：`approved / rejected / needs_rule_change`
2. `approved`：只能基于已隔离候选重新进入仲裁，不能手工拼接正文
3. `rejected`：当前 URL 本轮终止，不生成知识文件
4. `needs_rule_change`：进入规则升级流程，待新规则回归后重新抓取
5. 所有审核结论必须记录触发原因码、审阅者和时间戳

### 7.3.2 Review Bundle 与重放契约

每个进入隔离区的条目都必须冻结成一个 review bundle，建议路径：

- `Distill/02-Processing/fetch-review-queue/<review_item_id>.json`

review bundle 至少包含：

- `review_item_id`
- `source_url`
- `normalized_source_url`
- `normalized_final_url`
- `redirect_chain`
- `trigger_reasons`
- `site_id`
- `candidate_set`
- `selected_candidate_id`（若存在）
- `selected_artifact_hash`（若存在）
- `approved_result_snapshot`（若存在，且必须完整符合 5.1 Canonical Fetch Result schema）
- `artifact_ids`
- `artifact_hashes`
- `rule_versions`
- `rule_package_digest`
- `rule_snapshot_ref`
- `quality_scores`
- `decision_status`
- `created_at`

其中 `candidate_set` 的每个候选至少包含：

- `candidate_id`
- `fetch_layer`
- `quality_score`
- `hard_fail_reasons`
- `soft_fail_reasons`
- `artifact_id`
- `artifact_hash`

审核决定必须额外记录：

- `decision_reason`
- `reviewer_id`
- `reviewed_at`

重放要求：

1. review bundle 必须足以在**不重新联网**的前提下复现当时的候选仲裁与证据验证
2. `approved` 仅允许基于 bundle 内现有候选继续推进
3. 若 bundle 缺失关键 artifact 或哈希不一致，则该 review item 自动转为 `rejected`
4. `approved` 必须冻结 `selected_candidate_id`、`selected_artifact_hash` 与 `approved_result_snapshot`；Step 2 之后只消费该冻结快照

### 7.3.3 Replay Invariants 与资产钉住规则

离线重放必须同时钉住三类输入：

1. review bundle 本身
2. 对应的 fetch artifact bundles
3. 生成该结果时使用的规则包摘要 `rule_package_digest`

规则：

- 任一 pending review item 的 artifact bundle 不得被 TTL 清理
- 已 `approved` 或 `needs_rule_change` 的条目，在规定保留期内仍需保留其 pinned artifacts
- 若规则升级后 `rule_package_digest` 变化，旧 review bundle 仍必须能按 `rule_snapshot_ref` 指向的原规则快照离线重放
- 若任一 pinned artifact、规则快照或哈希缺失，则该条目不得重新进入知识流程

### 7.4 站点阈值、原因码与跨层触发条件

质量门必须支持**通用默认阈值 + 站点覆盖阈值**两层配置。

每条站点规则至少定义：

- `min_body_chars`
- `required_fields`
- `hard_fail_patterns`
- `soft_fail_patterns`
- `gray_zone_range`
- `escalation_policy`

同时，所有失败或降级都必须产出明确原因码，例如：

- `HARD_CAPTCHA`
- `HARD_EMPTY_BODY`
- `HARD_SHELL_PAGE`
- `SOFT_SHORT_BODY`
- `SOFT_MISSING_AUTHOR`
- `SOFT_METADATA_CONFLICT`
- `SOFT_SUMMARY_LIKE_BODY`

这样后续遥测、规则老化检测与回归评测才能基于明确的原因码，而不是靠自然语言日志猜测。

此外，质量分必须由确定性打分项组成，而不是自由裁量：

- 正文长度得分
- 必填字段完整度得分
- 页面结构完整度得分
- 壳页/噪音惩罚项
- 元数据冲突惩罚项
- extractive-evidence 完整度得分

评分执行要求：

1. 每项权重必须配置在站点规则中
2. 运行时只允许做固定公式计算，不允许动态口头裁量
3. 同一版本规则在同一输入上必须得到相同分数

## 8. 规则分层与风险控制

为避免“规则老化”把整个系统拖垮，规则分为四层：

### L1 通用失败识别

识别壳页、空页、验证码页、非正文页。  
这层相对稳定，轻易不会变化。

### L2 站点适配规则

定义某站点的请求与解析方式。  
这层可能随着站点改版而变化。

### L3 质量门

决定当前结果是否足以进入知识流程。  
这层阈值可以调整，但结构相对稳定。

### L4 Fallback 链

当上层失败时自动切入下一层。  
这层保证单层失效不会导致整体抓取链崩溃。

### 8.1 为什么不是“第一层成功即结束”

对高质量知识库来说，“能抓到一点内容”不等于“拿到了最佳可用内容”。  
如果沿用第一层成功即结束的逻辑，会有两个直接风险：

1. 截断正文、缺作者、缺日期的结果被过早锁定
2. 更高质量的下一层候选根本没有机会参与仲裁

因此，Distill 的抓取策略必须区分：

- **成功抓到内容**
- **抓到足够好的内容**

只有在候选结果通过质量门并在仲裁中胜出后，才能正式进入知识流程。

## 9. 规则老化检测与升级

### 9.1 自动识别

按域名持续记录以下信号：

- 专用 adapter 成功率下降
- fallback 救回率上升
- 核心字段缺失率上升
- 页面结构指纹变化
- 新壳页关键词反复出现

命中阈值后，将站点标记为：

`规则疑似老化`

### 9.1.1 迟滞、基线与样本量约束

为避免把临时反爬、网络抖动误判成规则老化，检测逻辑必须包含：

1. **最小样本量**：未达到站点规定样本量前，不触发老化结论
2. **滚动基线**：与该站点的历史稳定窗口比较，而不是只看当前窗口
3. **迟滞机制**：必须连续多个窗口恶化，才升级为“疑似老化”
4. **错误分类**：区分 `network`、`anti_bot`、`parser`、`metadata`、`unknown`
5. **fallback 相关性**：只有“专用规则失败 + 下一层稳定救回”的组合，才强烈指向规则老化

也就是说，规则老化不是一个单点事件，而是一个需要统计证据支持的结论。

### 9.2 自动生成升级候选

一旦标记老化，系统自动：

1. 保存失败样本
2. 对比 fallback 成功结果
3. 分析结构差异
4. 生成规则升级候选
5. 生成经验文档更新建议

升级候选必须包含：

- 规则差异摘要
- 受影响站点与风险等级
- 黄金样本集回归结果
- 与当前生产规则的对比结果
- 是否改变了字段映射/质量门/降级链

### 9.3 发布治理

规则升级采用：

`AI 主审 -> AI 回归 -> 人工放行`

说明：

- AI 负责检测、比对、生成 patch、做样本回归
- 人工不做 HTML 细节审查，而是做最终生产放行
- 默认不允许“自动改规则并直接上线”
- AI 主审与 AI 回归应尽量使用独立评审配置，避免完全共享同一盲点

### 9.4 Shadow Mode、发布包与回滚

规则升级不直接替换生产规则，而是先进入 **shadow mode**：

1. 新旧规则并行跑同一批样本
2. 旧规则仍然产生产生正式结果
3. 新规则只输出对比结果与风险报告
4. 通过对比报告决定是否放行

每次规则发布必须形成一个**发布包**，至少包含：

- 新旧规则 diff
- 黄金样本回归报告
- 线上 shadow 对比摘要
- 风险等级
- 回滚目标版本

回滚要求：

1. 任一发布都必须能回滚到前一个规则版本
2. 回滚不影响已归档的知识文件
3. 仅影响后续 URL 的抓取策略

### 9.5 失败样本与遥测治理

失败样本和页面证据是必要的，但必须受控：

1. 默认只在本地保存，不外发到第三方系统
2. 优先保存结构指纹、字段摘要和有限 excerpt，而不是无限制保留整页内容
3. 对失败样本设置保留期（例如 7 天），过期自动清理
4. 如需保留完整页面用于规则升级，必须记录理由和来源站点
5. 默认优先保存字段证据、DOM 指纹、开头 excerpt 和哈希，不默认保留整页正文
6. telemetry / 隔离样本必须设置大小上限，超限时只保留证据片段与哈希

## 10. 文档与规则资产

为使规则真正成为“硬性规定”，新增三类资产：

### 10.1 机器规则文件

建议新增：

- `references/fetch-site-rules.yaml`

用途：

- 供运行时读取
- 定义域名匹配、抓取顺序、请求策略、解析规则、质量门、fallback 条件、版本号

### 10.2 经验文档

建议新增：

- `references/fetch-site-rules.md`

用途：

- 记录已验证站点
- 解释为什么规则这样写
- 记录老化信号与升级流程
- 明确“当前确认有效的站点适配方案”

### 10.3 运行状态与遥测资产

建议新增：

- `Distill/99-Meta/fetch-telemetry.jsonl`
- `Distill/99-Meta/fetch-rule-state.json`
- `Distill/02-Processing/fetch-artifacts/`
- `Distill/02-Processing/fetch-failure-samples/`
- `Distill/02-Processing/fetch-rule-snapshots/`
- `Distill/02-Processing/fetch-review-queue/`

用途：

- 记录每次抓取的原因码、质量分、降级路径
- 记录站点规则当前状态与疑似老化结论
- 保存可复核的抓取产物包与 evidence 解析输入
- 保存受控的失败证据与升级候选输入
- 保存 review bundle 依赖的规则快照
- 隔离 `requires_review` 的候选结果，等待审核或丢弃

## 11. 首版范围

首版只正式内置 3 个抓取层，并配套统一抓取结果协议与仲裁器：

1. `wechat` 站点适配方案
2. `generic` 通用直抓
3. `agent_fallback` 抽象兜底层

不在首版内置更多站点规则。  
新增站点需满足：

- 高频出现
- 业务价值高
- 通用直抓质量不足

## 12. 微信首版规则方向

微信首版规则的经验结论写入站点规则文档：

- 使用移动微信风格请求策略
- 带 `Referer: https://mp.weixin.qq.com/`
- 从页面变量中提取标题、作者、日期
- 从正文主容器提取正文
- 若命中环境异常/验证页特征，则判硬失败
- 若正文过短、metadata 不完整或字段冲突，则判质量不足，进入下一层
- 微信规则必须区分 `author_byline` 与 `publisher_name`
- 微信规则通过后，仍可在灰区场景进入仲裁，而不是“第一成功即采用”

该规则在未来失效时，不直接删除，而是进入“规则疑似老化 -> 候选升级 -> 人工放行”流程。

## 13. 首版测试要求

需要最小回归测试集与黄金样本集：

1. 微信成功样本
2. 微信验证码/异常样本
3. 未知站点样本
4. metadata 冲突样本
5. 截断正文样本

检查项至少包括：

- 是否拿到正文
- 标题/作者/日期是否存在
- 正文长度是否达标
- 是否误把壳页判成正文
- evidence resolver 无法解析时是否 fail-closed
- review bundle 是否可离线重放
- 未登记 mirror 是否被拦截或送审

发布门禁：

- fail-closed / replay / mirror 三类测试均为**阻断型门禁**
- 任一失败，规则包不得进入 shadow release 之后的正式放行
- 是否正确触发 fallback
- 是否正确执行候选仲裁
- 是否在冲突元数据场景下避免静默污染
- 新旧规则在 shadow mode 下的差异是否可解释
- 回滚到上一规则版本后是否恢复旧行为

## 14. 需要修改的现有文件

首版实施时需要至少更新：

- `SKILL.md`
- `CHANGELOG.md`
- `references/step2-parsing.md`
- `references/version-manager.md`
- `scripts/` 下的抓取入口与规则读取逻辑
- `scripts/init-workspace.sh`
- 新增 `references/fetch-site-rules.yaml`
- 新增 `references/fetch-site-rules.md`
- 新增抓取结果协议、遥测与回归测试相关脚本/定义

### 14.1 工作区与版本迁移

由于本设计新增运行状态文件与抓取规则资产，实施时必须：

1. 为 Distill 工作区新增必要目录与元数据文件
2. 更新 `.distill-version`
3. 在 `init-workspace.sh` 中补齐新文件初始化
4. 在 `version-manager.md` 中记录升级路径

## 15. 预期结果

实施后，Distill 的抓取能力将从：

`依赖单点抓取经验`

升级为：

`可规则化、可回归、可升级、对 Agent 解耦的抓取制度`

这使 Distill 能把“高质量原文获取”真正纳入知识库工程的一部分，而不是依赖临时技巧或某个特定 Agent 的偶然表现。
