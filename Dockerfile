FROM python:3.9-slim-bullseye

RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    wget \
    chromium \
    ca-certificates \
    fonts-liberation \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

RUN npm install

RUN mkdir -p uploads

EXPOSE 5000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
