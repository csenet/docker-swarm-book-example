FROM python:3.11-alpine

# 依存パッケージのインストール
RUN apk add --no-cache \
    postgresql-dev \
    gcc \
    musl-dev \
    && pip install --no-cache-dir \
    flask \
    redis \
    psycopg2-binary

WORKDIR /app

# アプリケーションコードをコピー
COPY app.py .

# ポートの公開
EXPOSE 5000

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:5000/health || exit 1

# アプリケーションの起動
CMD ["python", "app.py"]
