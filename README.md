# Journal API

基于 FastAPI 的日记同步后端服务，支持 MongoDB 和 Redis 持久化存储。

## 功能特性

- 用户认证（登录/刷新 token）
- 日记条目同步（拉取/推送）
- 附件管理
- 七牛云存储集成
- MongoDB 数据持久化
- Redis 缓存支持

## 环境变量

```bash
# MongoDB 配置
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=journal_db

# Redis 配置
REDIS_URL=redis://localhost:6379

# 七牛云存储配置
QINIU_ACCESS_KEY=your_access_key
QINIU_SECRET_KEY=your_secret_key
QINIU_BUCKET_NAME=your_bucket_name
QINIU_UPLOAD_DOMAIN=https://upload.qiniup.com
QINIU_DOWNLOAD_BASE_URL=https://your-cdn-domain.com
```

## 使用 Docker Compose 部署

1. 复制环境变量示例：
```bash
cp .env.example .env
```

2. 配置环境变量（编辑 `.env` 文件）

3. 启动服务：
```bash
docker-compose up -d
```

4. 查看日志：
```bash
docker-compose logs -f api
```

5. 停止服务：
```bash
docker-compose down
```

## 本地开发

### 安装依赖
```bash
pipenv install --dev
```

### 启动开发服务器
```bash
pipenv run uvicorn app.main_v2:app --reload --port 8000
```

### 运行测试
```bash
pipenv run pytest
```

## API 端点

### 认证
- `POST /auth/login` - 用户登录
- `POST /auth/refresh` - 刷新访问令牌

### 同步
- `GET /sync/changes?since={revision}` - 拉取变更
- `POST /sync/push` - 推送变更

### 附件
- `PUT /attachments/{id}` - 上传附件
- `GET /attachments/{id}` - 下载附件

### 存储
- `GET /storage/qiniu/token?key={key}` - 获取七牛上传令牌

### 健康检查
- `GET /health` - 服务健康状态

## 数据持久化

- MongoDB 数据存储在 `mongodb_data` 卷
- Redis 数据存储在 `redis_data` 卷

## 生产环境建议

1. 使用 HTTPS（通过反向代理）
2. 配置 MongoDB 认证
3. 配置 Redis 密码
4. 使用环境变量管理敏感信息
5. 设置合理的七牛令牌过期时间
6. 配置日志收集和监控
7. 设置资源限制（CPU/内存）
