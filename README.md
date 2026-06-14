# wiki_multihopHotpotQA 多跳推理可视化系统
基于 ArangoDB 图数据库的 HotpotQA 多跳问答数据集管理与可视化系统。
项目概述

    数据库：ArangoDB（图数据库）
    后端：Python Flask + pyArango
    前端：HTML5 + D3.js + Tailwind CSS
    部署：GitHub Pages（静态演示）/ 本地 Flask（完整功能）

功能特性
表格
功能	说明
多跳查询	支持问题→文档的多跳推理链查询与可视化
检索	关键词搜索问题、随机示例展示
聚类分析	文档按引用热度分桶统计
可视化	D3.js 力导向图展示推理链结构，支持拖拽、缩放、高亮
快速开始
方式一：GitHub Pages 在线演示（无需后端）
直接访问：https://你的用户名.github.io/hotpotqa-viz/

    此模式使用预生成的演示数据，展示完整前端界面与交互逻辑。

方式二：本地完整运行（需 ArangoDB + Flask）
bash

# 1. 克隆仓库
git clone https://github.com/leon423-lzzz/hotpotqa-viz.git
cd hotpotqa-viz

# 2. 安装依赖
pip install -r requirements.txt

# 3. 确保 ArangoDB 在 127.0.0.1:8529 运行，数据库名为 hotpot_multihop

# 4. 启动后端
python app.py

# 5. 浏览器访问 http://127.0.0.1:5000

项目结构
plain

hotpotqa-viz/
├── index.html              # 静态版前端（GitHub Pages 入口）
├── data/                   # 预生成演示数据（静态模式）
│   ├── stats.json
│   ├── search.json
│   ├── examples.json
│   ├── chain.json
│   └── cluster.json
├── templates/
│   └── index.html          # Flask 模板（后端模式）
├── app.py                  # Flask 后端（5个API）
├── requirements.txt        # Python 依赖
└── README.md               # 本文件

API 端点
表格
端点	方法	功能
/api/search?q=	GET	关键词搜索问题
/api/examples	GET	随机获取5个示例
/api/chain?id=	GET	多跳推理链查询
/api/cluster	GET	文档引用热度聚类
/api/stats	GET	数据库统计信息
技术选型对比
表格
数据库类型	代表产品	多跳查询能力	聚类分析	可视化	结论
文档数据库	MongoDB	需多次关联，逻辑复杂	需外部计算	一般	不适合
列族数据库	Cassandra	不支持复杂查询	困难	困难	不适合
关系型数据库	MySQL	递归CTE实现多跳，SQL冗长	需自建算法	需额外开发	勉强能用
图数据库	ArangoDB	原生图遍历，AQL简洁	内置聚合	天然适配	最佳
演示截图
多跳推理链可视化
文档聚类分布
作者：李冠林 2023040308 数据2301
