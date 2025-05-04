FROM python:3.11-slim
WORKDIR /app

# 1. 安装 uv
RUN pip install --no-cache-dir uv

# 2. 拷贝依赖清单
COPY requirements.txt .

# 3. 用 uv 在 .venv 中批量安装
RUN uv pip install --system --no-cache -r requirements.txt

# 5. 拷贝源码及环境示例
COPY . .
COPY .env.example .env

EXPOSE 7860
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
