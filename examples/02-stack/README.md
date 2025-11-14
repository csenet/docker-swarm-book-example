# 02. スタック構成

Docker Composeファイルを使用した複数サービスのスタックデプロイを学びます。

## サンプル内容

このサンプルでは、以下の構成のWebアプリケーションをデプロイします：

- **Webサーバー (Nginx)**: リバースプロキシとして動作
- **アプリケーション (Python Flask)**: シンプルなAPIサーバー
- **データベース (Redis)**: セッションストレージ
- **ビジュアライザー (Visualizer)**: Swarmクラスタの可視化ツール

## ファイル構成

```
02-stack/
├── README.md
├── docker-compose.yml          # メインのスタック定義
├── docker-compose.simple.yml   # シンプルな3層構成
├── app/
│   ├── Dockerfile
│   └── app.py
└── nginx/
    └── nginx.conf
```

## 1. シンプルなスタックデプロイ

最初に、基本的な3層構成をデプロイしてみましょう。

```bash
# スタックをデプロイ
docker stack deploy -c docker-compose.simple.yml simple-app

# スタックの確認
docker stack ls
docker stack services simple-app

# 各サービスの状態を確認
docker service ls
docker service ps simple-app_web
docker service ps simple-app_redis

# アクセス確認
curl http://localhost:8080
```

## 2. 完全なアプリケーションスタック

次に、Visualizerを含む完全な構成をデプロイします。

```bash
# スタックをデプロイ
docker stack deploy -c docker-compose.yml myapp

# デプロイの進行状況を確認
watch docker stack ps myapp

# すべてのサービスがRunningになるまで待つ
docker stack services myapp

# アクセス確認
curl http://localhost:8080           # アプリケーション
curl http://localhost:8080/api/count # カウンター API
open http://localhost:8081           # Visualizer
```

## 3. スタックの管理

### サービスのスケーリング

```bash
# スタックファイルでレプリカ数を変更してから再デプロイ
# または、serviceコマンドで直接変更
docker service scale myapp_app=3

# 確認
docker service ps myapp_app
```

### ログの確認

```bash
# スタック全体のログ（全サービス）
docker stack ps myapp

# 特定のサービスのログ
docker service logs myapp_app
docker service logs -f myapp_app  # リアルタイム

# 複数サービスのログを同時に
docker service logs myapp_app myapp_redis
```

### スタックの更新

```bash
# docker-compose.ymlを編集後、再デプロイ
docker stack deploy -c docker-compose.yml myapp

# 変更されたサービスのみが更新される
```

### スタックの削除

```bash
# スタック全体を削除
docker stack rm myapp

# 確認
docker stack ls
docker service ls
```

## 4. Composeファイルの詳細

### バージョン

```yaml
version: "3.8"
```

Swarmモードでは、Compose仕様のバージョン3.x系を使用します。

### サービス定義

```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure
```

### ネットワーク

```yaml
networks:
  frontend:
    driver: overlay
  backend:
    driver: overlay
```

Swarmでは、サービス間通信に `overlay` ネットワークを使用します。

### ボリューム

```yaml
volumes:
  redis-data:
    driver: local
```

## トラブルシューティング

### サービスが起動しない

```bash
# サービスの詳細ログを確認
docker service ps myapp_app --no-trunc

# コンテナのログを直接確認
docker service logs myapp_app
```

### ネットワーク接続の問題

```bash
# ネットワークの確認
docker network ls
docker network inspect myapp_frontend

# サービスがネットワークに接続されているか確認
docker service inspect myapp_app
```

### イメージのビルド

```bash
# ローカルでイメージをビルド
cd app
docker build -t myapp:latest .

# または、docker-compose build を使用（開発時）
docker-compose build
```

## 演習課題

1. `docker-compose.simple.yml` を使ってスタックをデプロイしてください
2. アプリケーションサービスを3レプリカにスケールしてください
3. ブラウザでアクセスし、リロードするたびに異なるコンテナIDが表示されることを確認してください
4. スタックを削除してクリーンアップしてください

## まとめ

このサンプルで学んだこと：

- `docker stack deploy` でスタックをデプロイ
- Docker Composeファイルで複数サービスを定義
- `overlay` ネットワークでサービス間通信
- `docker stack services` でスタック内のサービスを確認
- `docker stack rm` でスタック全体を削除

次のステップ: [03. スケーリング・HA構成](../03-scaling-ha/) で高可用性とスケーラビリティを学びます。
