# 石榴籽城市更新 Agent

AI 驱动的城市更新工作平台，用 AI 对话重构 B 端交互。

## 📋 产品概述

**产品名称：** 石榴籽城市更新 Agent
**定位：** AI 驱动的城市更新工作平台
**目标用户：** 城市更新工作人员（街道办、住建局、城管局等）
**核心价值：** 用 AI 对话重构 B 端交互，去掉菜单/看板/筛选器，让自然语言成为唯一入口

## 🏗️ 技术架构

```
前端层 (HTML/JS/CSS) → API 网关 (FastAPI) → 后端服务层 → AI 服务层 → 数据层
```

## 📦 快速开始

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

### 📊 社区达人（数据管理）
- 文件上传解析（Excel/CSV/PDF/Word/图片/音频/视频）
- 数据校验（格式错误、空值、格式不统一）
- 确认入表
- 追问环节（导出报表/定时同步/查看趋势）

### ⚖️ 政策咨询（合规咨询）
- 文件上传解析
- 法规检索
- 合规分析
- 追问环节（生成书面意见/查看判例/答复口径/文书模板/跨地域对比/导出记录）

### 🏥 城市体检（报告审查 + 生成优化 + 可视化图表 + PPT）
- 报告审查（数据准确性、逻辑一致性、格式规范性）
- 报告生成
- 报告优化
- 可视化图表生成
- PPT 生成
- 追问环节

### 📐 方案评审（智能评审 + 方案设计）
- 方案评审（5 大维度评分）
- 优化方案生成
- 风险预警
- 评审意见模板
- 修改追踪
- 追问环节

## 🔧 多模态输入支持

系统支持以下多模态输入：
- **文字输入**：文本查询/指令
- **图片输入**：JPG/PNG/GIF/BMP/WebP
- **文件输入**：PPT/PDF/Excel/Word
- **音频输入**：MP3/WAV/OGG/FLAC/AAC
- **视频输入**：MP4/AVI/MOV/MKV/WMV

## 📚 API 文档

### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录

### 文件管理接口
- `POST /api/files/upload` - 文件上传
- `GET /api/files/{file_id}` - 获取文件信息
- `POST /api/files/{file_id}/parse` - 解析文件
- `DELETE /api/files/{file_id}` - 删除文件

### 社区达人接口
- `POST /api/data/` - 创建数据记录
- `POST /api/data/validate/{record_id}` - 数据校验
- `POST /api/data/enter/{record_id}` - 确认入表
- `GET /api/data/` - 查询数据记录列表
- `DELETE /api/data/{record_id}` - 删除数据记录

### 政策咨询接口
- `POST /api/policy/` - 创建政策法规
- `GET /api/policy/` - 查询政策法规列表
- `GET /api/policy/{policy_id}` - 获取政策法规详情
- `DELETE /api/policy/{policy_id}` - 删除政策法规
- `POST /api/policy/analyze` - 合规分析

### 城市体检接口
- `POST /api/health/` - 创建体检报告
- `GET /api/health/` - 查询体检报告列表
- `GET /api/health/{report_id}` - 获取体检报告详情
- `DELETE /api/health/{report_id}` - 删除体检报告
- `POST /api/health/{report_id}/review` - 审查体检报告
- `POST /api/health/{report_id}/optimize` - 优化体检报告
- `POST /api/health/{report_id}/generate-charts` - 生成可视化图表
- `POST /api/health/{report_id}/generate-ppt` - 生成汇报 PPT

### 方案评审接口
- `POST /api/plan/` - 创建方案评审
- `GET /api/plan/` - 查询方案评审列表
- `GET /api/plan/{review_id}` - 获取方案评审详情
- `DELETE /api/plan/{review_id}` - 删除方案评审
- `POST /api/plan/{review_id}/review` - 评审方案
- `POST /api/plan/{review_id}/optimize` - 优化方案
- `POST /api/plan/{review_id}/approve` - 评审通过
- `POST /api/plan/{review_id}/reject` - 评审不通过

### AI 服务接口
- `POST /api/ai/chat` - AI 对话
- `POST /api/ai/compliance` - 合规分析
- `POST /api/ai/review` - 方案评审
- `POST /api/ai/generate` - 报告生成
- `POST /api/ai/optimize` - 报告优化

### 多模态输入接口
- `POST /api/multimodal` - 多模态输入处理
- `POST /api/upload` - 文件上传（支持多模态）

## 📝 开发计划

### Phase 1：MVP（2-3 周）
- [x] 后端服务搭建（FastAPI）
- [x] 文件上传解析（Excel/CSV/PDF/Word/图片/音频/视频）
- [x] 数据校验算法
- [x] 数据库对接（PostgreSQL）
- [x] 前端 API 对接

### Phase 2：AI 集成（3-4 周）
- [x] LLM 推理服务（Qwen/GPT）
- [x] RAG 知识库（政策法规库）
- [x] 向量检索（相似判例匹配）
- [x] 合规分析/方案评审 AI 推理

### Phase 3：高级功能（2-3 周）
- [x] 图表生成（Matplotlib/ECharts）
- [x] PPT 生成（python-pptx）
- [x] 用户认证（JWT）
- [x] 权限管理

### Phase 4：优化部署（1-2 周）
- [ ] 性能优化（缓存、异步）
- [ ] 安全加固（HTTPS、CORS、CSRF）
- [ ] 部署上线（Docker/K8s）
- [ ] 监控告警（Prometheus/Grafana）

## 📊 技术栈

| 层级 | 技术选型 |
|------|----------|
| 前端 | HTML/CSS/JS |
| 后端 | Python + FastAPI |
| AI | LLM（Qwen/GPT）+ LangChain |
| 数据库 | PostgreSQL + Redis |
| 文件存储 | MinIO/OSS |
| 图表 | ECharts + Matplotlib |
| PPT | python-pptx |
| 部署 | Docker + Nginx |
| 监控 | Prometheus + Grafana |

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

- 项目地址：https://github.com/sunsean123456-cpu/slz
- 问题反馈：https://github.com/sunsean123456-cpu/slz/issues
