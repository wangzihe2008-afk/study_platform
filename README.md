# Study Platform（Flask + SQLAlchemy + Render）

这是一个可在 IntelliJ IDEA / PyCharm 中直接运行的教学平台示例项目，包含：

- 注册 / 登录
- 用户信息保存到数据库
- 国家 / 省份 / 学科 / 年级筛选
- 知识点列表
- 查看大纲要求
- 查看详细讲解
- 例题列表、例题详解、国家比较按钮
- 练习题列表、提交答案、得分、标准答案
- 练习记录保存到数据库
- 已适配 Render 部署

## 技术栈

- Flask 3.1
- Flask-SQLAlchemy 3.1
- Flask-Login 0.6
- SQLite（本地开发）
- PostgreSQL（Render 部署）

## 本地运行

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python run.py
```

打开：

```text
http://127.0.0.1:5000
```

## 数据库

### 本地默认

本地开发默认用 SQLite：

```env
DATABASE_URL=sqlite:///study_platform.db
```

### Render 部署

部署到 Render 时，把 `DATABASE_URL` 设置成 Render Postgres 提供的连接字符串。

代码已经支持：
- 本地没配 `DATABASE_URL` 时自动回退到 SQLite
- 云端有 `DATABASE_URL` 时自动连接 PostgreSQL

## Render 部署

详细步骤看：

- `DEPLOY_RENDER.md`

项目还附带了：

- `render.yaml`：可尝试用 Blueprint 一键部署

## 说明

当前版本里：
- 练习记录会真正保存到数据库
- 上传文件会保存到本地 `uploads/`
- 但在 Render 免费 Web Service 上，本地上传文件不适合长期保存

如果后面要继续升级，推荐：

1. 增加管理员后台
2. 接入真正课程标准数据
3. 改成云存储保存上传文件
4. 增加 OCR + AI 批改
