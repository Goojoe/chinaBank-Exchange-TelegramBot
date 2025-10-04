# 中国银行汇率查询 Telegram 机器人

这是一个提供中国银行汇率查询服务的 Telegram 机器人。用户可以通过简单的命令获取最新的汇率信息。

![1000029908](https://github.com/user-attachments/assets/2ff522d4-26a6-4730-bf38-12bbb3b8717d)

## 直接使用

https://t.me/chinaBank_Exchange_bot

## 功能

- FastAPI
- 查询最新的中国银行外汇汇率
- 支持多种货币转换
- 实时数据更新和异步缓存
- 用户日志隐私保护(可关闭)
- 使用Claude Pro开发

## 本地部署

1.  **安装 `uv` (如果尚未安装)**
    ```bash
    pip install uv
    ```

2.  **创建并激活虚拟环境**
    ```bash
    # 创建虚拟环境
    uv venv .venv

    # 激活虚拟环境 (根据你的 Shell选择)
    # PowerShell
    .\.venv\Scripts\Activate.ps1
    # Windows CMD
    .\.venv\Scripts\activate.bat
    # Linux/macOS
    source ./.venv/bin/activate
    ```

3.  **安装项目依赖**
    ```bash
    uv pip install -r requirements.txt
    ```

4.  **配置环境变量**
    -   复制 `.env.example` 文件并重命名为 `.env`。
    -   在 `.env` 文件中，填入你的 `TELEGRAM_BOT_TOKEN`。
    -   `WEBHOOK_URL` 暂时可以留空。

5.  **启动应用服务器**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 7860 --reload
    ```
    服务器将在 `http://localhost:7860` 上运行。

6.  **设置 Webhook**
    为了让 Telegram 能够将消息发送到你的本地服务器，你需要一个公共 URL。`ngrok` 是一个很好的工具。
    ```bash
    ngrok http 7860
    ```
    `ngrok` 会提供一个 `https://` 开头的 URL，例如 `https://xxxx-xxxx.ngrok-free.app`。

7.  **更新 `.env` 文件**
    -   将 `ngrok` 提供的 URL 填入 `.env` 文件的 `WEBHOOK_URL` 变量中。
    -   由于应用以 `--reload` 模式运行，它会自动重启并使用新的 Webhook URL 设置自己。

现在，你的机器人应该可以接收和响应消息了。


## 使用 Docker Compose 部署

如果你安装了 Docker 和 Docker Compose，你可以使用 `docker compose.yml` 文件来简化部署过程。

1.  **配置环境变量**
    -   复制 `.env.example` 文件并重命名为 `.env`。
    -   在 `.env` 文件中，填入你的 `TELEGRAM_BOT_TOKEN`。
    -   使用 `ngrok` 或其他服务获取一个公共的 `https` URL，并将其填入 `WEBHOOK_URL`。

2.  **构建并启动容器**
    ```bash
    docker compose up --build -d
    ```
    -   `--build` 标志会强制重新构建镜像，确保你使用的是最新的代码。
    -   `-d` 标志会在后台运行容器。

3.  **查看日志**
    ```bash
    docker compose logs -f
    ```

4.  **停止容器**
    ```bash
    docker compose down
    ```
## hf space 部署说明

此项目已配置为在 Hugging Face Space 上运行。

### 部署方法

下载Dockerfile.hf并改名为Dockerfike上传即可

部署后，您需要：

1. 在 Space 设置中配置以下环境变量：

   - `TELEGRAM_BOT_TOKEN`: 您的 Telegram 机器人令牌
   - `WEBHOOK_URL`: 您的 Hugging Face Space URL (例如 https://yourname-project.hf.space)
   - `CACHE_TTL_MINUTES`: 缓存超时时间（分钟）

2. 确保 Telegram 机器人已通过 BotFather 创建并获取了令牌

3. 部署完成后，机器人将自动设置 webhook 并开始响应用户消息
