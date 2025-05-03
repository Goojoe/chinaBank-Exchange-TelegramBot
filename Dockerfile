FROM python:3.11-slim

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .
COPY .env.example .env

# 暴露端口（Hugging Face Spaces 使用 7860 端口）
EXPOSE 7860

# 启动应用（注意：指向 app.main:app 而不是原来的 app.master:app）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]