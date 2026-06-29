# OSS 与 ClickHouse 配置指南

## 一、先搞懂两件事

| 组件 | 是什么 | 要不要下载 |
|------|--------|------------|
| **OSS** | 阿里云对象存储，存 CSV 文件 | 不用下软件，网页控制台 + Python 脚本 |
| **ClickHouse** | 列式分析数据库 | **不用本机安装**，课程要求用 **阿里云 ClickHouse 云实例** |

你已有阿里云账号 → 先配 OSS（今天能做完）→ 再开 ClickHouse 云实例。

---

## 二、OSS 配置（详细步骤）

### 步骤 1：创建 Bucket

1. 打开 https://oss.console.aliyun.com/
2. 点击 **创建 Bucket**
3. 填写：
   - **Bucket 名称**：全局唯一，如 `price-index-20221234`（建议加学号）
   - **地域**：选离你近的，如 **华东1（杭州）**
   - **存储类型**：标准存储
   - **读写权限**：**私有**（推荐）
   - 其他默认即可
4. 创建成功后，在 Bucket 概览页记下：
   - **Bucket 名称**
   - **Endpoint（外网）**，形如：`oss-cn-hangzhou.aliyuncs.com`

> Endpoint 填到 config 里要加 `https://`，即 `https://oss-cn-hangzhou.aliyuncs.com`

### 步骤 2：创建 AccessKey（建议用 RAM 子账号）

**不要用主账号长期裸奔**，按下面做子账号：

1. 打开 https://ram.console.aliyun.com/users
2. **创建用户** → 勾选 **OpenAPI 调用访问**
3. 保存显示的 **AccessKey ID** 和 **AccessKey Secret**（只显示一次，务必保存）
4. 给用户授权：
   - 简单做法：`AliyunOSSFullAccess`（OSS 完全权限）
   - 更安全：自定义策略，只允许你的 Bucket

### 步骤 3：创建 config.yaml

在 PowerShell 中：

```powershell
cd E:\CodexW\dashuju\price-index
copy config.yaml.template config.yaml
notepad config.yaml
```

按你的实际情况修改（示例）：

```yaml
oss:
  endpoint: "https://oss-cn-hangzhou.aliyuncs.com"   # 改成你 Bucket 的地域 Endpoint
  bucket: "price-index-20221234"                      # 改成你的 Bucket 名
  access_key_id: "LTAI5txxxxxxxxxxxx"                 # RAM 用户的 AK
  access_key_secret: "xxxxxxxxxxxxxxxxxxxxxxxx"         # RAM 用户的 SK

clickhouse:
  host: "待填写"          # ClickHouse 开通后再填
  port: 9000
  user: "default"
  password: "待填写"
  database: "db_price_index"

project:
  base_date: "2025-05-17"
```

### 步骤 4：测试 OSS 是否配好

```powershell
cd E:\CodexW\dashuju\price-index
pip install --user -r requirements.txt
python src/test_connection.py oss
```

成功会显示 Bucket 名称和已有文件数量。

### 步骤 5：上传 3 个测试文件

```powershell
python src/oss_uploader.py --limit 3
```

然后去 OSS 控制台 → 你的 Bucket → 文件管理，应看到：

```
raw/daily_price/daily_prices_20250517.csv
raw/daily_price/daily_prices_20250518.csv
raw/daily_price/daily_prices_20250519.csv
```

**截图保存**，后面写报告用。

---

## 三、ClickHouse 配置（云实例，不用下载）

### 步骤 1：开通阿里云 ClickHouse

1. 登录阿里云控制台：https://www.aliyun.com/
2. 顶部搜索 **「ClickHouse」** 或 **「云数据库 ClickHouse」**
3. 选择 **社区兼容版 / 社区版**（课程指导书要求）
4. 点击 **创建实例**：
   - 地域：尽量和 OSS **同一地域**（如杭州），传输更快
   - 规格：选 **最低配** 即可（注意费用，学生有免费额度/试用最好）
   - 设置 **管理员密码**（记下来）
5. 等待实例状态变为 **运行中**

> 如果找不到入口：在控制台搜索「ApsaraDB for ClickHouse」或问老师/同学要课程统一实例地址。

### 步骤 2：创建数据库

在 ClickHouse 控制台：

1. 进入你的实例 → **数据库管理** → **创建数据库**
2. 名称填：`db_price_index`

### 步骤 3：配置白名单（重要！）

本机和 GitHub Actions 要能连上 CK，必须把访问 IP 加进白名单：

1. 实例 → **数据安全性** → **白名单**
2. 添加：
   - 本机调试：可先加 `0.0.0.0/0`（仅课程演示，**有安全风险**，做完改回）
   - 或查本机公网 IP（百度搜「IP」）只加你的 IP

不配白名单会报 **Connection timeout**。

### 步骤 4：获取连接信息

在实例详情页找到：

| 配置项 | config.yaml 字段 | 示例 |
|--------|------------------|------|
| 连接地址 / Host | `clickhouse.host` | `cc-xxx.clickhouse.aliyuncs.com` |
| 端口 | `clickhouse.port` | `9000`（原生协议） |
| 用户名 | `clickhouse.user` | `default` |
| 密码 | `clickhouse.password` | 你设置的密码 |
| 数据库 | `clickhouse.database` | `db_price_index` |

把 `config.yaml` 里 clickhouse 段填完整。

### 步骤 5：测试 ClickHouse 连接

```powershell
python src/test_connection.py ck
```

### 步骤 6：建表 + 导入 + 算指数

```powershell
python src/ck_loader.py ddl
python src/ck_loader.py import --limit 3
python src/ck_loader.py sql sql/calc_daily_index.sql
python src/plot_index.py
```

---

## 四、常见问题

### OSS 报 AccessDenied
- Bucket 名写错
- Endpoint 地域和 Bucket 地域不一致
- RAM 用户没有 OSS 权限

### OSS 报 NoSuchBucket
- bucket 名称拼写错误（不要带 `oss://` 前缀）

### ClickHouse 连接超时
- 白名单没加 IP
- host 填错（不要带 `http://`）
- 端口应为 **9000**（不是 8123 HTTP 端口，除非改代码）

### 有没有本地 ClickHouse 替代？
- 可以用 Docker 本地跑做开发：`docker run clickhouse/clickhouse-server`
- 但**课程答辩**建议还是用阿里云实例，和任务书一致
- 本地 Docker 的 host 填 `127.0.0.1`，port `9000`

---

## 五、推荐顺序（今天 → 明天）

**今天（只需 OSS）：**
1. 创建 Bucket + RAM 用户
2. 填写 config.yaml 的 oss 部分
3. `python src/test_connection.py oss`
4. `python src/oss_uploader.py --limit 3`

**明天（ClickHouse 开通后）：**
1. 填写 config.yaml 的 clickhouse 部分
2. `python src/test_connection.py ck`
3. `python src/ck_loader.py ddl`
4. `python src/ck_loader.py import --limit 3`
5. 跑 SQL + 出图

ClickHouse 部分可以等实例开通后再做，**OSS 可以先独立完成**。
