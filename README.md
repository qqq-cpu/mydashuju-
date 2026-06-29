# 电商价格指数项目 — 实操指南

你现在的情况：**有阿里云 OSS 账号**，但还没做 ClickHouse、GitHub Actions。  
没关系，按下面顺序做，**每完成一步就有东西可以写进报告和答辩**。

---

## 总路线图（建议 5 步）

```
第1步 准备数据 + OSS 上传          ← 你已有 OSS，今天就能做
第2步 开通 ClickHouse + 建表       ← 最关键，做完就有“真项目”
第3步 导入数据 + 跑 SQL 算指数     ← 能出真实折线图
第4步 推 GitHub + 配 Actions      ← 任务书第8-9次课要求
第5步 截图写进总结报告 + 练答辩    ← 用真实截图替换之前的示意内容
```

**原则：先跑通最小闭环（3 天数据），再扩到全量。不要一上来就传 1095 个文件。**

---

## 第 0 步：环境准备（30 分钟）

### 0.1 安装 Python 依赖

```powershell
cd e:\CodexW\dashuju\price-index
pip install -r requirements.txt
```

### 0.2 准备课程数据

从学习通下载数据集，放到：

```
e:\CodexW\dashuju\price-index\data\data\
  categories.csv
  products.csv
  daily_price\
    daily_prices_20250517.csv
    daily_prices_20250518.csv
    ...
```

如果数据不在本机，先找同学拷一份，或至少先放 3 个日文件做测试。

### 0.3 配置文件

```powershell
copy config.yaml.template config.yaml
```

编辑 `config.yaml`，填入你的 OSS 信息（ClickHouse 第 2 步再填）。

---

## 第 1 步：OSS 上传（今天就能完成）

### 1.1 阿里云控制台操作

1. 登录 [阿里云 OSS 控制台](https://oss.console.aliyun.com/)
2. **创建 Bucket**（若还没有）
   - 名称：全局唯一，如 `price-index-你的学号`
   - 地域：选离你近的，如华东1（杭州）
   - 读写权限：私有（推荐）
3. 记下 **Endpoint**，如 `https://oss-cn-hangzhou.aliyuncs.com`
4. 创建 **RAM 子账号**（推荐，不要用主账号 AK 长期裸奔）
   - 权限：`AliyunOSSFullAccess` 或仅该 Bucket 的读写
   - 创建 AccessKey，保存 ID 和 Secret

### 1.2 填写 config.yaml 的 oss 部分

```yaml
oss:
  endpoint: "https://oss-cn-hangzhou.aliyuncs.com"
  bucket: "price-index-你的学号"
  access_key_id: "LTAI..."
  access_key_secret: "..."
```

### 1.3 上传测试（先传 3 个文件）

```powershell
cd e:\CodexW\dashuju\price-index
python src/oss_uploader.py --limit 3
```

成功标志：控制台 Bucket 里出现 `raw/daily_price/daily_prices_*.csv`。

**截图保存**：OSS 文件列表 → 写进总结报告「结果分析」。

---

## 第 2 步：开通 ClickHouse（必做）

任务书要求用 **阿里云 ClickHouse 社区版**。

### 2.1 开通实例

1. 登录阿里云，搜索 **ClickHouse** 或 **云数据库 ClickHouse**
2. 创建 **社区版** 实例（选最低配即可，注意费用）
3. 创建数据库 `db_price_index`
4. 记下：Host、端口（通常 9000）、用户名、密码

### 2.2 填写 config.yaml 的 clickhouse 部分

```yaml
clickhouse:
  host: "cc-xxx.clickhouse.aliyuncs.com"
  port: 9000
  user: "default"
  password: "你的密码"
  database: "db_price_index"
```

### 2.3 建表

```powershell
python src/ck_loader.py ddl
```

成功标志：ClickHouse 里有 `fact_daily_price` 和 `agg_daily_index` 两张表。

---

## 第 3 步：导入数据 + 计算指数（核心）

### 3.1 导入 3 天数据（测试）

```powershell
python src/ck_loader.py import --limit 3
```

### 3.2 执行指数 SQL

```powershell
python src/ck_loader.py sql sql/calc_daily_index.sql
```

### 3.3 查看结果

在 ClickHouse 客户端或 DMS 执行：

```sql
SELECT * FROM db_price_index.agg_daily_index
WHERE category_id = ''
ORDER BY change_date;
```

基日 `2025-05-17` 的 `index_value` 应接近 **100**。

### 3.4 生成折线图

```powershell
python src/plot_index.py
```

图片在 `report/price_index_trend.png`。

### 3.5 扩到更多天（可选）

```powershell
python src/ck_loader.py import --limit 30    # 30 天
python src/ck_loader.py sql sql/calc_daily_index.sql
python src/plot_index.py
```

全量 1095 天会较慢，答辩前 **30~50 天 + 趋势图** 通常够用。

---

## 第 4 步：GitHub + Actions（任务书第 8-9 次课）

### 4.1 创建 GitHub 仓库

```powershell
cd e:\CodexW\dashuju\price-index
git init
git add .
git commit -m "init price index project"
git branch -M main
git remote add origin https://github.com/你的用户名/price-index.git
git push -u origin main
git checkout -b dev
git push -u origin dev
```

**注意**：`config.yaml` 已在 `.gitignore`，不会上传密钥。

### 4.2 配置 GitHub Secrets

仓库 → Settings → Secrets and variables → Actions → New repository secret：

| Secret 名 | 内容 |
|-----------|------|
| OSS_ENDPOINT | https://oss-cn-hangzhou.aliyuncs.com |
| OSS_BUCKET | 你的 bucket 名 |
| OSS_ACCESS_KEY_ID | RAM 子账号 AK |
| OSS_ACCESS_KEY_SECRET | RAM 子账号 SK |
| CK_HOST | ClickHouse 主机 |
| CK_PORT | 9000 |
| CK_USER | default |
| CK_PASSWORD | CK 密码 |

### 4.3 触发流水线

```powershell
git add .
git commit -m "add workflow"
git push origin dev
```

到 GitHub → Actions 查看是否绿色通过。  
**截图**：Actions 运行成功页 → 放进总结报告「测试说明」。

---

## 第 5 步：单元测试（任务书第 4 次课）

```powershell
pytest tests/ -v
```

应 3 个用例全部通过。截图放进报告。

---

## 你现在该做什么（今天）

| 优先级 | 任务 | 预计时间 |
|--------|------|----------|
| P0 | 确认数据在 `price-index/data/data/` 下 | 已完成 |
| P0 | 配置 `config.yaml`，上传 3 个文件到 OSS | 30 min |
| P1 | 开通 ClickHouse，执行 `ddl` + `import --limit 3` | 1-2 h |
| P1 | 跑 SQL + `plot_index.py` 出真图 | 20 min |
| P2 | 推 GitHub，配 Secrets，跑 Actions | 1 h |
| P3 | 用真实截图更新总结报告 | 30 min |

---

## 常见问题

**Q：没有 ClickHouse 怎么办？**  
必须用云 CK 或老师提供的实例。本地 Docker 可以开发，但答辩要说清楚最终用的是阿里云。

**Q：OSS 上传报 AccessDenied？**  
检查 RAM 权限、Bucket 地域与 endpoint 是否一致。

**Q：导入报连接超时？**  
ClickHouse 需把本机 IP 加入白名单（阿里云控制台 → 数据安全性 → 白名单）。

**Q：感觉报告写的和做的不一样？**  
正常。报告是设计文档；你现在要做的是 **把设计变成真实截图**。做完后更新总结报告里的「测试说明」「结果分析」章节。

**Q：GitHub Actions 连不上 CK？**  
Actions 运行在 GitHub 国外服务器，需在 CK 白名单加 `0.0.0.0/0`（仅课程演示）或使用可公网访问的 CK 地址。

---

## 项目目录

```
price-index/
├── config.yaml.template   # 配置模板
├── config.yaml            # 本地配置（不提交 Git）
├── src/
│   ├── oss_uploader.py    # 上传 OSS
│   ├── ck_loader.py       # 导入 CK / 执行 SQL
│   └── plot_index.py      # 出图
├── sql/
│   ├── ddl.sql
│   └── calc_daily_index.sql
├── tests/
├── .github/workflows/pipeline.yml
└── report/                # 输出图表
```

---

## 答辩时你怎么说

> 我先在 OSS 上存储原始 CSV，再用 Python 导入 ClickHouse，  
> 通过 SQL 计算链式价格指数，matplotlib 出图，  
> GitHub Actions 在 push 后自动跑测试和导入。  
> 基日 2025-05-17 指数为 100，后续按日变化。

配上 OSS 截图、CK 查询结果、折线图、Actions 绿勾，就是完整项目。
