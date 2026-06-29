# GitHub 推送与 Actions 配置指南

仓库：https://github.com/qqq-cpu/mydashuju-

## 流水线说明（OSS → ClickHouse）

| Job | 运行环境 | 做什么 |
|-----|----------|--------|
| **test** | GitHub 云端 `ubuntu-latest` | pytest 单元测试 |
| **deploy** | **本机 Self-hosted Runner** | OSS 下载 CSV → 导入 CK → 算指数 → 出图 → 上传 artifact |

deploy 使用本机 Runner，出口 IP 与本地调试相同，可复用 ClickHouse 白名单（无需放行 GitHub 云端 7000+ 个 IP 段）。

---

## 1. Secrets（已配置可跳过）

仓库 → **Settings** → **Secrets and variables** → **Actions**

| Secret | 值 |
|--------|-----|
| `OSS_ENDPOINT` | `https://oss-cn-beijing.aliyuncs.com` |
| `OSS_BUCKET` | `java-ai-you-li` |
| `OSS_ACCESS_KEY_ID` | RAM AK |
| `OSS_ACCESS_KEY_SECRET` | RAM SK |
| `CK_HOST` | `cc-bp10l1gy3g7bg08k4.public.clickhouse.ads.aliyuncs.com` |
| `CK_PORT` | `8123` |
| `CK_USER` | `ck_user_database` |
| `CK_PASSWORD` | CK 密码 |

本地一键写入（需 `gh auth login`）：

```powershell
cd E:\CodexW\dashuju\price-index
python _scripts/set_github_secrets.py
```

---

## 2. 安装本机 Self-hosted Runner（deploy 必做）

### 2.1 在 GitHub 获取注册命令

1. 打开 https://github.com/qqq-cpu/mydashuju-/settings/actions/runners/new
2. 选择 **Windows** → **x64**
3. 按页面提示执行（或在本机 PowerShell 运行下面脚本）

### 2.2 一键安装（PowerShell）

```powershell
cd E:\CodexW\dashuju
$token = (gh api repos/qqq-cpu/mydashuju-/actions/runners/registration-token --method POST | ConvertFrom-Json).token
New-Item -ItemType Directory -Force -Path actions-runner | Out-Null
cd actions-runner
if (-not (Test-Path config.cmd)) {
  Invoke-WebRequest -Uri "https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-win-x64-2.321.0.zip" -OutFile runner.zip
  Expand-Archive runner.zip -DestinationPath . -Force
}
.\config.cmd --url https://github.com/qqq-cpu/mydashuju- --token $token --unattended --replace
```

### 2.3 启动 Runner（保持窗口开着，或装成服务）

```powershell
cd E:\CodexW\dashuju\actions-runner
.\run.cmd
```

看到 `Listening for Jobs` 即就绪。关闭窗口会停止接收任务。

---

## 3. 触发流水线

- **自动**：push 到 `main` / `dev`
- **手动**：Actions → **OSS to ClickHouse Pipeline** → **Run workflow**（可填 `import_limit`，默认 3）

成功后在 Actions 运行页下载 **price-index-chart** artifact（含 `price_index_trend.png`）。

---

## 4. deploy 步骤对照（课程「OSS → CK 导入工作流」）

```
pytest (test job)
  ↓
Secrets → config.yaml
  ↓
test_connection.py oss
  ↓
oss_downloader.py          # OSS → 本地 CSV
  ↓
test_connection.py ck
  ↓
ck_loader.py ddl
  ↓
ck_loader.py import        # 本地 CSV → fact_daily_price
  ↓
calc_daily_index.sql       # → agg_daily_index
  ↓
plot_index.py              # → report/price_index_trend.png
```

---

## 5. 常见问题

| 现象 | 处理 |
|------|------|
| deploy 一直 **Queued** | 本机 Runner 未启动，运行 `actions-runner\run.cmd` |
| CK 连接 timeout | 白名单加本机公网 IP/32 |
| OSS AccessDenied | endpoint 与 Bucket 地域一致（北京） |
| 无 artifact | 检查 deploy job 是否绿 |

---

## 6. 不要提交的内容

- `config.yaml`（已在 .gitignore）
- `data/data/daily_price/` 大 CSV
