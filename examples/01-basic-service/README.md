# 01. 基本的なサービスデプロイ

Docker Swarmでの基本的なサービスデプロイ方法を学びます。

## サンプル内容

1. **Nginx Webサーバー**: シンプルなWebサーバーのデプロイ
2. **Redis**: インメモリデータストアのデプロイ

## 前提条件

```bash
# Swarmモードが初期化されていることを確認
docker info | grep Swarm
# Swarm: active と表示されればOK

# 初期化されていない場合
docker swarm init
```

## 1. Nginxサービスのデプロイ

### 基本的なデプロイ

```bash
# Nginxサービスを作成
docker service create \
  --name web \
  --publish 8080:80 \
  nginx:alpine

# サービスの確認
docker service ls
docker service ps web

# ブラウザまたはcurlでアクセス
curl http://localhost:8080
```

### カスタムHTMLを使用したデプロイ

```bash
# カスタムHTMLファイルを使用してデプロイ
docker service create \
  --name custom-web \
  --publish 8081:80 \
  --mount type=bind,source=$(pwd)/html,target=/usr/share/nginx/html,readonly \
  nginx:alpine

# アクセス確認
curl http://localhost:8081
```

### レプリカ数の指定

```bash
# 3つのレプリカでデプロイ
docker service create \
  --name web-replicas \
  --replicas 3 \
  --publish 8082:80 \
  nginx:alpine

# レプリカの確認
docker service ps web-replicas

# スケールアウト
docker service scale web-replicas=5

# スケールイン
docker service scale web-replicas=2
```

## 2. Redisサービスのデプロイ

```bash
# Redisサービスを作成
docker service create \
  --name redis \
  --publish 6379:6379 \
  redis:alpine

# サービスの確認
docker service ps redis

# Redis CLIでアクセス（dockerコンテナ経由）
docker run --rm -it redis:alpine redis-cli -h <your-host-ip> ping
```

## サービスの管理

### サービスの詳細確認

```bash
# サービス一覧
docker service ls

# サービスの詳細情報
docker service inspect web

# サービスのログ確認
docker service logs web

# リアルタイムでログを追跡
docker service logs -f web
```

### サービスの更新

```bash
# イメージの更新
docker service update --image nginx:latest web

# レプリカ数の更新
docker service update --replicas 5 web

# ポートの追加
docker service update --publish-add 8083:80 web
```

### サービスの削除

```bash
# 特定のサービスを削除
docker service rm web

# 複数のサービスを削除
docker service rm web custom-web web-replicas redis
```

## 演習課題

1. Nginxサービスを3レプリカでデプロイし、ブラウザでアクセスできることを確認してください
2. サービスを5レプリカにスケールアウトし、その後2レプリカにスケールインしてください
3. サービスのログを確認し、どのレプリカにアクセスが分散されているか確認してください
4. サービスを削除してクリーンアップしてください

## まとめ

このサンプルで学んだこと：

- `docker service create` でサービスを作成
- `--publish` でポートを公開
- `--replicas` でレプリカ数を指定
- `docker service scale` でスケーリング
- `docker service logs` でログ確認
- `docker service rm` でサービス削除

次のステップ: [02. スタック構成](../02-stack/) でDocker Composeファイルを使った複数サービスの管理を学びます。
