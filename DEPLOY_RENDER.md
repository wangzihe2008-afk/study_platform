# Render 部署指南（适合这个项目）

这个项目已经改成：
- 本地开发默认用 SQLite
- 上 Render 时改用 PostgreSQL
- 启动命令已适配 `gunicorn run:app`

---

## 一、本地先确认能运行

在项目目录执行：

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python run.py
```

浏览器打开：

```text
http://127.0.0.1:5000
```

---

## 二、上传到 GitHub

1. 打开 GitHub，新建一个仓库，例如：`study-platform`
2. 把当前项目文件全部上传到仓库
3. 确认仓库里有这些文件：
   - `run.py`
   - `requirements.txt`
   - `render.yaml`
   - `app/`

---

## 三、在 Render 创建数据库

1. 登录 Render
2. 点 **New → Postgres**
3. 名字填：`study-platform-db`
4. 先选免费方案
5. 创建完成后，在数据库页面记住：
   - Internal Database URL
   - External Database URL

建议 Web Service 连接数据库时优先用 **Internal Database URL**。

---

## 四、在 Render 创建 Web Service（手动方式）

1. 在 Render 点 **New → Web Service**
2. 连接你的 GitHub 仓库
3. 选择这个项目仓库
4. 参数这样填：

### 基本设置
- **Name**: `study-platform`
- **Runtime**: `Python 3`
- **Build Command**:

```bash
pip install -r requirements.txt
```

- **Start Command**:

```bash
gunicorn run:app
```

---

## 五、在 Render 添加环境变量

在 Web Service 的 **Environment** 页面添加：

### 1. SECRET_KEY
随便填一个长字符串，例如：

```text
my-study-platform-secret-key-2026
```

### 2. DATABASE_URL
把你的 Render Postgres 的 **Internal Database URL** 粘贴进去。

格式一般类似：

```text
postgresql://USER:PASSWORD@HOST:5432/DATABASE
```

### 3. 可选：UPLOAD_FOLDER
如果你不填，默认就是 `uploads`。

---

## 六、部署完成后测试

部署成功后：

1. 打开 Render 给你的公网网址
2. 先注册一个账号
3. 再登录
4. 查看是否能进入 dashboard
5. 提交一条练习记录，确认数据库能写入

---

## 七、如果想用 render.yaml 一键部署

这个项目已经带了 `render.yaml`。

你可以在 Render 里使用 Blueprint / IaC 导入仓库。
如果 `render.yaml` 导入时有字段提示需要补充，就按 Render 页面提示确认即可。

---

## 八、常见报错

### 1. `No module named ...`
说明依赖没有装全。
确认 `requirements.txt` 已经包含：
- Flask
- Flask-Login
- Flask-SQLAlchemy
- python-dotenv
- gunicorn
- psycopg2-binary

### 2. `Application error` 或 502
常见原因：
- `Start Command` 写错
- `DATABASE_URL` 没设置
- 数据库还没创建好

正确启动命令：

```bash
gunicorn run:app
```

### 3. 文件上传后过一段时间消失
这是正常的：
- Render Web Service 默认本地文件系统不是永久保存
- 免费 Web Service 不能挂持久化磁盘

所以这个项目在 Render 上：
- **数据库数据会保存在 Postgres**
- **上传到本地 uploads/ 的文件不适合长期保存**

如果以后你要长期保存上传文件，建议把文件改存到：
- Cloudinary
- AWS S3
- Supabase Storage

---

## 九、你要交作业时可以怎么说

你可以这样介绍：

> 本系统本地开发时使用 SQLite，部署到 Render 公网后改用 Render Postgres 作为正式数据库。后端使用 Flask + SQLAlchemy，Render 使用 `gunicorn run:app` 启动服务。用户注册、登录和练习记录会保存到 PostgreSQL 中。

