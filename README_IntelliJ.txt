IntelliJ 运行方法

1. 解压项目
2. 用 IntelliJ / PyCharm 打开整个文件夹
3. 配置 Python Interpreter
4. 在 Terminal 运行:
   python -m pip install -r requirements.txt

5. 先启动普通功能:
   python run.py

6. 打开:
   http://127.0.0.1:5000

-----------------------------------
PaddleOCR 免费拍照识题功能（不需要 API key）
-----------------------------------

普通功能跑起来后，拍照识题页面如果提示缺少 PaddleOCR，
再额外安装 PaddleOCR 相关依赖。

按 PaddleOCR 官方文档，PaddleOCR 3.x 依赖 PaddlePaddle 3.0+，
CPU 安装示例是先安装 paddlepaddle，再安装 paddleocr[all]。
建议新建虚拟环境，避免依赖冲突。

Windows / CPU 示例:
python -m pip install paddlepaddle==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
python -m pip install "paddleocr[all]"

安装完成后重启项目，再进入“拍照识题”页面上传整页题目照片。

说明:
- 这版拍照识题是免费 OCR 方案，不用 API key。
- 识别后会按题号尽量拆成多道题。
- 讲解是本地规则生成的“基础讲解”，不是在线大模型讲解。
- 如果图片很糊、倾斜严重、题号不清楚，拆题效果会下降。
