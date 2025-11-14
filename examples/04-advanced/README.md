# 04. 高度な設定

Docker Swarmの高度な機能を学びます。実運用で必要となる設定を網羅的に扱います。

## サンプル内容

このサンプルでは、以下の高度な機能を学びます：

- **Secrets**: パスワード、APIキーなどの機密情報管理
- **Configs**: 設定ファイルの管理と動的更新
- **Volumes**: データの永続化とバックアップ
- **Networks**: 高度なネットワーク構成
- **配置戦略**: ノード選択とタスク配置の制御
- **ラベル**: メタデータによる管理

## ファイル構成

```
04-advanced/
├── README.md
├── docker-compose.yml
├── app/
│   ├── Dockerfile
│   └── app.py
├── nginx/
│   └── nginx.conf
├── secrets/
│   ├── db_password.txt
│   └── api_key.txt
└── configs/
    ├── app_config.json
    └── redis.conf
```

## 1. Secretsの管理

### Secretの作成

```bash
# ファイルからSecretを作成
docker secret create db_password secrets/db_password.txt
docker secret create api_key secrets/api_key.txt

# 標準入力からSecretを作成
echo "my_secret_password" | docker secret create db_root_password -

# Secretの一覧確認
docker secret ls

# Secretの詳細確認（内容は表示されない）
docker secret inspect db_password
```

### Secretの使用

```yaml
services:
  app:
    image: myapp:latest
    secrets:
      - db_password
      - api_key
    environment:
      - DB_PASSWORD_FILE=/run/secrets/db_password
      - API_KEY_FILE=/run/secrets/api_key

secrets:
  db_password:
    external: true  # 事前に作成されたSecret
  api_key:
    file: ./secrets/api_key.txt  # ファイルから作成
```

### アプリケーションでSecretを読み込む

```python
# /run/secrets/ 配下からSecretを読み込む
def get_secret(secret_name):
    try:
        with open(f'/run/secrets/{secret_name}', 'r') as f:
            return f.read().strip()
    except IOError:
        return None

db_password = get_secret('db_password')
api_key = get_secret('api_key')
```

### Secretの更新

```bash
# Secretは直接更新できないため、削除して再作成
docker service update --secret-rm db_password myapp_app
echo "new_password" | docker secret create db_password_v2 -
docker service update --secret-add db_password_v2 myapp_app
```

## 2. Configsの管理

### Configの作成

```bash
# ファイルからConfigを作成
docker config create nginx_config configs/nginx.conf
docker config create app_config configs/app_config.json

# Configの一覧確認
docker config ls

# Configの内容確認
docker config inspect --pretty nginx_config
```

### Configの使用

```yaml
services:
  nginx:
    image: nginx:alpine
    configs:
      - source: nginx_config
        target: /etc/nginx/nginx.conf
        mode: 0444  # 読み取り専用

configs:
  nginx_config:
    file: ./nginx/nginx.conf
  app_config:
    external: true
```

### Configの更新

```bash
# 新しいバージョンのConfigを作成
docker config create nginx_config_v2 nginx/nginx.conf

# サービスを更新
docker service update \
  --config-rm nginx_config \
  --config-add source=nginx_config_v2,target=/etc/nginx/nginx.conf \
  myapp_nginx
```

## 3. Volumesとデータ永続化

### Volumeの種類

```yaml
services:
  db:
    volumes:
      # Named volume（推奨）
      - db-data:/var/lib/postgresql/data

      # Bind mount（開発環境）
      - ./data:/data

      # tmpfs（一時データ）
      - type: tmpfs
        target: /tmp

volumes:
  db-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /path/on/host
```

### Volumeの管理

```bash
# Volume一覧
docker volume ls

# Volumeの詳細
docker volume inspect myapp_db-data

# Volumeのバックアップ
docker run --rm \
  -v myapp_db-data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/db-backup.tar.gz -C /data .

# Volumeのリストア
docker run --rm \
  -v myapp_db-data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/db-backup.tar.gz -C /data
```

## 4. 高度なネットワーク構成

### 複数ネットワークの使用

```yaml
networks:
  frontend:
    driver: overlay
    driver_opts:
      encrypted: "true"  # データ通信を暗号化
    ipam:
      config:
        - subnet: 10.0.1.0/24

  backend:
    driver: overlay
    attachable: true  # 手動でコンテナをアタッチ可能
    internal: true    # 外部通信を遮断

  admin:
    driver: overlay
    labels:
      - "environment=production"
```

### ネットワーク分離

```yaml
services:
  web:
    networks:
      - frontend  # フロントエンドのみアクセス可能

  app:
    networks:
      - frontend
      - backend  # 両方のネットワークにアクセス可能

  db:
    networks:
      - backend  # バックエンドのみアクセス可能
```

### ネットワーク管理

```bash
# ネットワークの作成
docker network create -d overlay --attachable my-network

# ネットワークの詳細
docker network inspect myapp_frontend

# コンテナのネットワーク接続
docker network connect myapp_frontend <container-id>
```

## 5. 配置戦略とConstraints

### ノードラベルの設定

```bash
# ノードにラベルを追加
docker node update --label-add zone=east node1
docker node update --label-add zone=west node2
docker node update --label-add ssd=true node1
docker node update --label-add gpu=nvidia node3

# ノードのラベル確認
docker node inspect node1 | jq '.[0].Spec.Labels'
```

### 配置制約（Constraints）

```yaml
services:
  db:
    deploy:
      placement:
        constraints:
          - node.role == manager  # マネージャーノードのみ
          - node.labels.ssd == true  # SSDラベルを持つノード
          - node.hostname == node1  # 特定のホスト

  cache:
    deploy:
      placement:
        constraints:
          - node.labels.zone == east  # 東ゾーンのノード
```

### 配置優先度（Preferences）

```yaml
services:
  web:
    deploy:
      placement:
        preferences:
          - spread: node.labels.zone  # ゾーン間で分散
          - spread: node.labels.datacenter  # データセンター間で分散
```

### レプリカ配置の制限

```yaml
services:
  app:
    deploy:
      replicas: 6
      placement:
        max_replicas_per_node: 2  # 各ノードに最大2レプリカ
```

## 6. サービスラベルとメタデータ

### サービスラベルの設定

```yaml
services:
  web:
    labels:
      - "com.example.description=Web Frontend"
      - "com.example.department=Engineering"
      - "com.example.version=1.0"
    deploy:
      labels:
        - "com.example.service=web"
        - "traefik.enable=true"
        - "traefik.http.routers.web.rule=Host(`example.com`)"
```

### ラベルでフィルタリング

```bash
# ラベルでサービスを検索
docker service ls --filter label=com.example.department=Engineering

# ラベルでノードを検索
docker node ls --filter node.label=zone=east
```

## 7. 完全なスタックのデプロイ

```bash
# Secretsの作成
echo "db_secure_password" | docker secret create db_password -
echo "api_key_12345" | docker secret create api_key -

# Configsの作成
docker config create nginx_config nginx/nginx.conf
docker config create app_config configs/app_config.json

# スタックのデプロイ
docker stack deploy -c docker-compose.yml advanced-app

# デプロイ確認
docker stack services advanced-app
docker stack ps advanced-app

# アクセス確認
curl http://localhost:8080
curl http://localhost:8080/api/config
```

## 8. モニタリングとロギング

### ログドライバーの設定

```yaml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service,environment"
```

### メトリクス収集

```yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - prometheus-data:/prometheus
    configs:
      - source: prometheus_config
        target: /etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
```

## トラブルシューティング

### Secretが読み込めない

```bash
# コンテナ内でSecretを確認
docker exec <container-id> ls -la /run/secrets/
docker exec <container-id> cat /run/secrets/db_password
```

### Configが反映されない

```bash
# Configのバージョンを確認
docker config ls
docker service inspect myapp_nginx | jq '.[0].Spec.TaskTemplate.ContainerSpec.Configs'
```

### ネットワーク接続の問題

```bash
# サービスのネットワーク確認
docker service inspect myapp_app | jq '.[0].Spec.TaskTemplate.Networks'

# ネットワークのサービス一覧
docker network inspect myapp_frontend | jq '.[0].Containers'
```

## 演習課題

1. Secretを使ってデータベースパスワードを安全に管理してください
2. Configを使ってNginxの設定を外部化してください
3. 異なるネットワークでフロントエンドとバックエンドを分離してください
4. ノードラベルを使って、データベースを特定のノードに配置してください
5. スタックを削除し、Secret/Configもクリーンアップしてください

## クリーンアップ

```bash
# スタックの削除
docker stack rm advanced-app

# Secretsの削除
docker secret rm db_password api_key

# Configsの削除
docker config rm nginx_config app_config

# Volumesの削除（注意: データが失われます）
docker volume rm advanced-app_db-data
```

## まとめ

このサンプルで学んだこと：

- **Secrets** で機密情報を安全に管理
- **Configs** で設定ファイルを外部化
- **Volumes** でデータを永続化
- **Networks** でサービスを分離
- **配置戦略** でタスク配置を制御
- **ラベル** でメタデータ管理

これらの機能を組み合わせることで、本番環境で安全かつ柔軟にDocker Swarmを運用できます。

## 参考資料

- [Docker Secrets](https://docs.docker.com/engine/swarm/secrets/)
- [Docker Configs](https://docs.docker.com/engine/swarm/configs/)
- [Manage swarm service networks](https://docs.docker.com/engine/swarm/networking/)
- [Control service placement](https://docs.docker.com/engine/swarm/services/#control-service-placement)
