# GitHub 推送与 Actions 配置指南

## 1. 本地初始化并提交（已完成可跳过）

```powershell
cd E:\CodexW\dashuju\price-index
git init
git add .
git commit -m "feat: price index project with OSS, ClickHouse and CI"
```

## 2. 在 GitHub 创建空仓库

1. 打开 https://github.com/new
2. 仓库名例如：`price-index`
3. **不要**勾选 README（避免冲突）
4. 创建后复制 HTTPS 地址

## 3. 关联远程并推送

```powershell
git branch -M main
git remote add origin https://github.com/你的用户名/price-index.git
git push -u origin main
git checkout -b dev
git push -u origin dev
```

## 4. 配置 GitHub Secrets

仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret 名称 | 填什么 |
|-------------|--------|
| `OSS_ENDPOINT` | `https://oss-cn-beijing.aliyuncs.com` |
| `OSS_BUCKET` | `java-ai-you-li` |
| `OSS_ACCESS_KEY_ID` | 你的 RAM AccessKey ID |
| `OSS_ACCESS_KEY_SECRET` | 你的 RAM AccessKey Secret |
| `CK_HOST` | `cc-bp10l1gy3g7bg08k4.public.clickhouse.ads.aliyuncs.com` |
| `CK_PORT` | `8123` |
| `CK_USER` | `ck_user_database` |
| `CK_PASSWORD` | 你的 ClickHouse 密码 |

## 5. 触发 Actions

- push 到 `main` 或 `dev` 分支会自动运行
- 或 Actions 页 → **Run workflow** 手动触发

流水线步骤：pytest → 测 OSS/CK → 从 OSS 下载 3 个 CSV → 导入 CK → 算指数 → 上传折线图 artifact

## 6. ClickHouse 白名单注意

GitHub Actions 运行在 GitHub 服务器上，IP 不固定。若 CI 的 deploy  job 连接 CK 超时，需：

- 在阿里云白名单添加 GitHub Actions 出口 IP 段（难）
- 或课程演示时 **只展示 test job 通过**，deploy 在本地已跑通即可

## 7. 不要提交的内容

- `config.yaml`（已在 .gitignore）
- `data/data/daily_price/` 大 CSV（已在 .gitignore）
