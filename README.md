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

### Pipenv 最佳实践

#### 环境初始化
```bash
# 安装生产环境依赖
pipenv install

# 安装开发环境依赖（包含测试、代码检查工具）
pipenv install --dev

# 进入虚拟环境（推荐方式）
pipenv shell

# 临时在虚拟环境中执行命令
pipenv run <command>
```

#### 依赖管理
```bash
# 添加生产依赖
pipenv install fastapi uvicorn

# 添加开发依赖
pipenv install --dev pytest black flake8

# 卸载依赖
pipenv uninstall package_name

# 查看依赖图
pipenv graph

# 检查安全性
pipenv check

# 生成 requirements.txt（用于 CI/CD）
pipenv requirements > requirements.txt
```

#### 虚拟环境管理
```bash
# 查看虚拟环境路径
pipenv --venv

# 删除虚拟环境（重新创建）
pipenv --rm

# 安装 Pipfile.lock 精确版本
pipenv install --deploy

# 更新依赖并锁定版本
pipenv lock

# 同步 Pipfile 和 Pipfile.lock
pipenv sync
```

#### 项目配置
- **Pipfile**：声明项目依赖和 Python 版本要求
- **Pipfile.lock**：锁定精确版本，确保环境一致性
- **镜像源**：已配置阿里云镜像加速依赖安装

#### 常用开发命令
```bash
# 启动开发服务器（热重载）
pipenv run dev

# 运行测试套件
pipenv run test

# 代码格式化
pipenv run format

# 代码检查
pipenv run lint

# 安全检查
pipenv run check

# 生成依赖锁定文件
pipenv lock
```

#### 脚本说明
Pipfile 中预定义了常用脚本命令：
- `dev`：启动开发服务器（热重载）
- `test`：运行测试套件
- `format`：代码格式化
- `lint`：代码风格检查
- `check`：依赖安全检查

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

## Pipenv 工程实践建议

### 依赖管理最佳实践
1. **版本锁定**：始终提交 `Pipfile.lock` 确保环境一致性
2. **依赖分类**：生产依赖放在 `[packages]`，开发依赖放在 `[dev-packages]`
3. **版本规范**：核心依赖使用精确版本，非关键依赖使用灵活版本
4. **安全检查**：定期运行 `pipenv check` 检查安全漏洞
5. **依赖清理**：定期运行 `pipenv graph` 检查并移除未使用依赖

### 团队协作规范
1. **环境同步**：新成员使用 `pipenv install --dev` 快速搭建环境
2. **变更流程**：修改依赖后必须运行 `pipenv lock` 并提交 lock 文件
3. **CI/CD 集成**：生产环境使用 `pipenv install --deploy` 确保精确版本
4. **镜像配置**：使用国内镜像源加速依赖安装

### 开发效率优化
1. **Shell 激活**：使用 `pipenv shell` 进入虚拟环境提升开发体验
2. **脚本管理**：在 Pipfile 中添加自定义脚本命令
3. **环境隔离**：避免使用系统 Python，始终使用 pipenv 管理环境
4. **依赖分析**：使用 `pipenv requirements` 生成 requirements.txt 用于部署

## 生产环境建议

1. 使用 HTTPS（通过反向代理）
2. 配置 MongoDB 认证
3. 配置 Redis 密码
4. 使用环境变量管理敏感信息
5. 设置合理的七牛令牌过期时间
6. 配置日志收集和监控
7. 设置资源限制（CPU/内存）
8. 在生产环境使用 `pipenv install --deploy` 确保依赖一致性
