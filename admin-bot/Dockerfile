FROM python:3.11-slim
WORKDIR /bot
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl gnupg ca-certificates \
    fonts-liberation libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libgbm1 libx11-xcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 \
    libxrandr2 libxrender1 libxss1 libxtst6 libnss3 libxkbcommon0 libglib2.0-0 \
    libpango-1.0-0 libcairo2 \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install chromium
COPY bot.py .
CMD ["python", "bot.py"]


