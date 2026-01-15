# 后端服务完善说明

本文档说明了后端服务的 MongoDB 和 Redis 集成，以及容器化部署配置。

## 新增文件

### 数据库层
- `app/database/mongo.py` - MongoDB 异步客户端封装
- `app/database/redis.py` - Redis 异步客户端封装
- `app/models/mongo.py` - MongoDB 数据模型

### 服务层 (v2)
- `app/services/auth_v2.py` - 基于 MongoDB 的认证服务
- `app/services/sync_v2.py` - 基于 MongoDB 的同步服务
- `app/services/attachments_v2.py` - 基于 MongoDB 的附件服务

### 路由层 (v2)
- `app/api/routes/auth_v2.py` - 认证路由
- `app/api/routes/sync_v2.py` - 同步路由
- `app/api/routes/attachments_v2.py` - 附件路由
- `app/api/routes/storage_v2.py` - 存储路由
- `app/api/deps_v2.py` - 依赖注入

### 应用入口
- `app/main_v2.py` - 使用 MongoDB/Redis 的应用入口

### 部署配置
- `Dockerfile` - Docker 镜像构建配置
- `docker-compose.yml` - 开发环境 Docker Compose 配置
- `docker-compose.prod.yml` - 生产环境 Docker Compose 配置
- `nginx.conf.example` - Nginx 反向代理配置示例
- `.dockerignore` - Docker 构建排除文件
- `Makefile` - 常用命令快捷方式

## 功能特性

### MongoDB 持久化
- 日记条目存储
- 附件元数据存储
- 附件内容存储
- 刷新令牌存储
- 版本号序列管理

### Redis 缓存
- 访问令牌验证（1小时过期）
- 可扩展缓存支持

### 七牛云存储
- 通过 API 获取上传令牌
- 支持大文件上传

## 环境变量

```bash
# MongoDB 配置
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=journal_db

# Redis 配置
REDIS_URL=redis://localhost:6379

# 七牛云配置
QINIU_ACCESS_KEY=your_access_key
QINIU_SECRET_KEY=your_secret_key
QINIU_BUCKET_NAME=your_bucket_name
QINIU_UPLOAD_DOMAIN=https://upload.qiniup.com
QINIU_DOWNLOAD_BASE_URL=https://your-cdn-domain.com
```

## 部署方式

### 本地开发
```bash
# 安装依赖
pipenv install --dev

# 启动开发服务器
make dev
# 或
pipenv run uvicorn app.main_v2:app --reload --port 8000
```

### Docker Compose 开发环境
```bash
# 启动所有服务
make docker-up
# 或
docker-compose up -d

# 查看日志
make docker-logs

# 停止服务
make docker-down
```

### Docker Compose 生产环境
```bash
# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 启动生产服务
make docker-prod-up

# 停止生产服务
make docker-prod-down
```

### 手动 Docker 部署
```bash
# 构建镜像
docker build -t journal-api .

# 运行容器
docker run -p 8000:8000 \
  -e MONGODB_URL=mongodb://host.docker.internal:27017 \
  -e REDIS_URL=redis://host.docker.internal:6379 \
  journal-api
```

## 数据持久化

### 开发环境
- MongoDB 数据存储在 `mongodb_data` 卷
- Redis 数据存储在 `redis_data` 卷

### 生产环境
- 数据存储在命名卷中，确保容器重启后数据不丢失
- 支持备份和恢复

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

## 生产环境建议

1. **HTTPS 配置**
   - 使用 Nginx 反向代理
   - 配置 SSL/TLS 证书
   - 参考 `nginx.conf.example`

2. **数据库安全**
   - 配置 MongoDB 认证
   - 配置 Redis 密码
   - 使用环境变量管理敏感信息

3. **监控和日志**
   - 配置日志收集
   - 设置健康检查
   - 监控资源使用情况

4. **备份策略**
   - 定期备份 MongoDB 数据
   - 备份 Redis 数据（如果需要）
   - 测试恢复流程

5. **性能优化**
   - 配置 MongoDB 索引
   - 调整 Redis 缓存策略
   - 优化数据库查询

## 迁移说明

从内存存储迁移到 MongoDB/Redis：

1. 更新环境变量配置
2. 使用 `app/main_v2.py` 作为应用入口
3. 使用新的路由和服务层（v2 版本）
4. 启动服务，自动初始化数据库索引

## 故障排查

### MongoDB 连接问题
```bash
# 检查 MongoDB 状态
docker-compose logs mongodb

# 检查连接
docker exec -it journal_mongodb mongo
```

### Redis 连接问题
```bash
# 检查 Redis 状态
docker-compose logs redis

# 检查连接
docker exec -it journal_redis redis-cli ping
```

### API 启动问题
```bash
# 检查 API 日志
docker-compose logs api

# 进入容器检查
docker exec -it journal_api bash
```

## 依赖项

### Python 依赖
- fastapi = "0.128.0"
- motor = "*" (MongoDB 异步驱动)
- redis[hiredis] = "*" (Redis 异步驱动)
- qiniu = "*" (七牛云 SDK)
- uvicorn (ASGI 服务器)

### 容器依赖
- mongo:6.0
- redis:7-alpine
- nginx:alpine (生产环境)

## 测试

```bash
# 运行单元测试
make test
# 或
pipenv run pytest
```
