FROM python:3.11-alpine

WORKDIR /app

# 依存パッケージのインストール
RUN pip install --no-cache-dir flask redis requests

# アプリケーションコードをコピー
COPY app.py .

# ポートの公開
EXPOSE 5000

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:5000/health || exit 1

# アプリケーションの起動
CMD ["python", "app.py"]
