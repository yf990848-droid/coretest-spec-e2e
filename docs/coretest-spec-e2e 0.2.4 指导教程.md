更新说明
新增全量测试设计卡片与 TestAgent 的交互能力。
支持在 TR 节点右键点击【AI分析】，触发 /coretest-explore 需求探索流程。
支持在 TS 节点右键点击【AI分析】，或在TR节点--关联对象--关联的TS，多选TS，点击【AI分析】，触发 /coretest-design 测试设计流程。
1. coretest-init
输入： /coretest-init 产品版本
例如：
/coretest-init UPCF 27.0.0
agent会自动拉取个人名下的设计任务和TR，并展示全量测试设计平台卡片：

如需创建TR，请在右侧卡片通过自己产品的逻辑创建好TR（关联好IR或SR、特性或功能）之后，在左侧对话区输入： TR已创建；
（如果不需创建TR，可以输入/coretest-explore TR_id 提前进入TS生成阶段。）
示例：

agent会再次拉取最新的TR信息，用于后续流程。

2. coretest-explore
两种方式：
方式①：在全量测试设计卡片的TR节点，右键点击【AI分析】，自动触发explore流程
示例：

方式②：输入：/coretest-explore TR id
例如：
/coretest-explore TR_3867
agent会调用工具获取平台上自动创建的DFX类TS，同agent创建的TS一并展示，方便用户在下一阶段对特定TS针对性地生成用例。

TS生成后，提示用户确认，是否要将TS归档到全量测试设计平台（如果后续需要使用卡片触发design流程，这里请选择直接归档）：

归档完成后，输出汇总结果：



3. coretest-design
三种方式：
方式①：在全量测试设计卡片的TS节点，右键点击【AI分析】，自动触发指定TS的design流程
示例：

 
方式②：在全量测试设计卡片的TR节点--关联对象--关联的TS，多选TS，点击【AI分析】，自动触发多个TS的design流程
示例：

方式③：输入：/coretest-design <tr_id> [TS列表]
例如：
/coretest-design TR_3863 TS_01 TS_02
agent会根据选择的TS,分批并行生成TP和TC,以卡片形式在右侧展示：

用户可点击“归档至测试用例管理”按钮，将用例归档至CIDA:

4. coretest-archive
输入：/coretest-archive <tr_id> <归档目标...>
例如：
/coretest-archive TR_3863 TS
/coretest-archive TR_3863 TS_01 TS_02
/coretest-archive TR_3863 TP
/coretest-archive TR_3863 TP.01.03.01
/coretest-archive TR_3863 TC
agent会根据归档目标生成执行计划（例如：如果输入的是TC,会自动补齐父级依赖的TS、TP计划）和文档范围，复用TR，将剩余目标按计划归档到全量测试设计平台:



归档完成后，会在右侧卡片展示全量测试设计平台，可以看到归档的对象、文档：
