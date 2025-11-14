FROM python:3.11-alpine

WORKDIR /app

# 依存パッケージのインストール
RUN pip install --no-cache-dir flask redis

# アプリケーションコードをコピー
COPY app.py .

# ポートの公開
EXPOSE 5000

# アプリケーションの起動
CMD ["python", "app.py"]
