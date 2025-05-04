# 中国银行汇率查询 Telegram 机器人

这是一个提供中国银行汇率查询服务的 Telegram 机器人。用户可以通过简单的命令获取最新的汇率信息。

## 直接使用

https://t.me/chinaBank_Exchange_bot

## 功能

- FastAPI
- 查询最新的中国银行外汇汇率
- 支持多种货币转换
- 实时数据更新和异步缓存
- 用户日志隐私保护(可关闭)

## 本地部署

```
pip install uv
uv pip install -r requirements.txt

# Start Uvicorn server
uvicorn main:app --host 0.0.0.0 --port 7860 --reload

ngrok http 7860
```

记得更改`.env`的`TELEGRAM_BOT_TOKEN`和`WEBHOOK_URL`

## hf space 部署说明

此项目已配置为在 Hugging Face Space 上运行。部署后，您需要：

1. 在 Space 设置中配置以下环境变量：

   - `TELEGRAM_BOT_TOKEN`: 您的 Telegram 机器人令牌
   - `WEBHOOK_URL`: 您的 Hugging Face Space URL (例如 https://yourname-project.hf.space)
   - `CACHE_TTL_MINUTES`: 缓存超时时间（分钟）

2. 确保 Telegram 机器人已通过 BotFather 创建并获取了令牌

3. 部署完成后，机器人将自动设置 webhook 并开始响应用户消息
