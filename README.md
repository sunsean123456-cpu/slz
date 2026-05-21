# 石榴籽城市更新 Agent - 后端服务

AI 驱动的城市更新工作平台后端服务

## 📋 项目概述

石榴籽 Agent 是一个 AI 驱动的城市更新工作平台，提供以下核心功能：

- **社区达人**：多源数据上传、自动对齐、智能核验、一键入表
- **政策咨询**：合规审查、判例查询、文书生成、跨地域对比
- **城市体检**：报告审查、报告生成优化、可视化图表、PPT 生成
- **方案评审**：智能评审、风险预警、优化建议、修改追踪

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库、AI 服务等
```

### 3. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

### 4. 访问文档

- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## 📖 功能模块

### 方案评审（真实 AI 评审）

方案评审模块使用真实 AI 模型进行方案评审，支持：

1. **文档上传**：支持 PDF/Word/Excel 格式
2. **文档解析**：自动解析文档内容
3. **AI 评审**：使用 Qwen 大模型进行五维评分
4. **报告生成**：自动生成评审报告
5. **优化建议**：基于评审结果生成优化方案

### 评审维度

| 维度 | 权重 | 说明 |
|------|------|------|
| 政策合规性 | 25% | 是否符合国家及地方政策法规 |
| 技术可行性 | 25% | 技术方案是否合理可行 |
| 经济合理性 | 20% | 预算编制是否合理，资金筹措是否可行 |
| 社会可接受度 | 15% | 居民接受程度，社会风险 |
| 实施可操作性 | 15% | 进度安排是否合理，责任是否明确 |

## 🔧 技术栈

| 层级 | 技术选型 |
|------|----------|
| 后端 | Python + FastAPI |
| 数据库 | PostgreSQL + SQLAlchemy |
| AI 服务 | Qwen 大模型 |
| 文档解析 | PyPDF2, python-docx, pandas |
| 认证 | JWT |

## 📝 API 接口

### 方案评审

- `POST /api/plan/upload` - 上传方案文件
- `POST /api/plan/{review_id}/parse` - 解析方案文件
- `POST /api/plan/{review_id}/review` - 执行 AI 评审
- `GET /api/plan/{review_id}` - 获取评审结果
- `POST /api/plan/{review_id}/optimize` - 生成优化方案
- `POST /api/plan/{review_id}/export` - 导出评审报告

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！
