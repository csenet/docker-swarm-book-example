# 03. スケーリング・HA構成

高可用性（HA）とスケーラビリティを実現するDocker Swarmの機能を学びます。

## サンプル内容

このサンプルでは、以下の機能を学びます：

- **レプリカスケーリング**: サービスの水平スケーリング
- **ローリングアップデート**: 無停止でのアップデート
- **ヘルスチェック**: コンテナの健全性監視
- **リソース制限**: CPU・メモリの制限と予約
- **配置戦略**: ノード間でのコンテナ配置
- **再起動ポリシー**: 障害時の自動復旧

## ファイル構成

```
03-scaling-ha/
├── README.md
├── docker-compose.yml           # HA構成のスタック定義
├── docker-compose.update.yml    # ローリングアップデートのデモ用
└── app/
    ├── Dockerfile
    ├── app.py (v1)
    └── app-v2.py
```

## 1. HAスタックのデプロイ

```bash
# スタックをデプロイ
docker stack deploy -c docker-compose.yml ha-app

# デプロイの進行状況を確認
watch docker stack ps ha-app

# サービスの状態を確認
docker stack services ha-app
```

## 2. スケーリング

### 手動スケーリング

```bash
# レプリカ数を確認
docker service ls

# スケールアウト（5レプリカに増やす）
docker service scale ha-app_web=5

# リアルタイムで状態を確認
watch docker service ps ha-app_web

# スケールイン（2レプリカに減らす）
docker service scale ha-app_web=2
```

### Composeファイルでスケーリング

```yaml
services:
  web:
    deploy:
      replicas: 5  # この値を変更
```

```bash
# 変更後、再デプロイ
docker stack deploy -c docker-compose.yml ha-app
```

## 3. ローリングアップデート

### イメージの更新

```bash
# 現在のバージョンを確認
curl http://localhost:8080

# イメージを更新してデプロイ
# docker-compose.update.yml を使用
docker stack deploy -c docker-compose.update.yml ha-app

# ローリングアップデートの進行状況を確認
watch docker service ps ha-app_web

# 更新中もサービスは継続的にアクセス可能
while true; do curl http://localhost:8080; sleep 1; done
```

### アップデート設定の調整

```yaml
deploy:
  update_config:
    parallelism: 2       # 同時に更新するコンテナ数
    delay: 10s           # 更新間隔
    failure_action: rollback  # 失敗時の動作
    monitor: 60s         # 監視期間
    max_failure_ratio: 0.3    # 失敗許容率
  rollback_config:
    parallelism: 2
    delay: 5s
```

### 手動ロールバック

```bash
# 前のバージョンにロールバック
docker service rollback ha-app_web

# ロールバックの進行状況を確認
watch docker service ps ha-app_web
```

## 4. ヘルスチェック

### ヘルスチェックの確認

```bash
# サービスの詳細を確認（ヘルスステータスも表示）
docker service ps ha-app_web

# 特定のコンテナのヘルスチェックログ
CONTAINER_ID=$(docker ps -q -f name=ha-app_web | head -1)
docker inspect $CONTAINER_ID | jq '.[0].State.Health'
```

### ヘルスチェック設定

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
  interval: 30s      # チェック間隔
  timeout: 10s       # タイムアウト
  retries: 3         # 失敗許容回数
  start_period: 40s  # 起動猶予期間
```

## 5. リソース制限

### リソース使用状況の確認

```bash
# サービスのリソース使用状況
docker stats $(docker ps -q -f name=ha-app_web)

# ノード全体のリソース
docker node ls
docker node inspect <node-id> | jq '.[0].Status.Resources'
```

### リソース制限の設定

```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'      # CPUの上限
      memory: 512M     # メモリの上限
    reservations:
      cpus: '0.25'     # CPU予約
      memory: 256M     # メモリ予約
```

## 6. 負荷テスト

### 負荷をかけてスケーリングを確認

```bash
# Apache Benchで負荷テスト
# 1000リクエスト、同時接続数10
ab -n 1000 -c 10 http://localhost:8080/

# または、簡易的な負荷テスト
for i in {1..100}; do
  curl -s http://localhost:8080 &
done
wait

# リクエストが各レプリカに分散されているか確認
docker service logs ha-app_web | grep "hostname"
```

### スケールアウトの効果確認

```bash
# レプリカを増やす前の性能測定
ab -n 1000 -c 10 http://localhost:8080/

# スケールアウト
docker service scale ha-app_web=10

# スケールアウト後の性能測定
ab -n 1000 -c 10 http://localhost:8080/
```

## 7. 障害復旧のテスト

### コンテナ障害のシミュレーション

```bash
# ランダムにコンテナを停止
CONTAINER_ID=$(docker ps -q -f name=ha-app_web | head -1)
docker stop $CONTAINER_ID

# 自動的に新しいコンテナが起動することを確認
watch docker service ps ha-app_web

# サービスは継続的に利用可能
curl http://localhost:8080
```

### ノード障害のシミュレーション（複数ノード環境）

```bash
# ノードをドレインモードに（新しいタスクを受け付けない）
docker node update --availability drain <node-id>

# タスクが他のノードに再配置されることを確認
watch docker service ps ha-app_web

# ノードを復帰
docker node update --availability active <node-id>
```

## 8. モニタリング

### リアルタイムモニタリング

```bash
# サービスのログをリアルタイムで確認
docker service logs -f ha-app_web

# 特定のタスクのログ
docker service ps ha-app_web
docker service logs ha-app_web.<task-id>

# イベントの監視
docker events --filter 'type=service'
```

## トラブルシューティング

### アップデートが失敗する場合

```bash
# 失敗したタスクの確認
docker service ps ha-app_web --no-trunc

# 自動ロールバックされたか確認
docker service inspect ha-app_web | jq '.[0].UpdateStatus'

# 手動でロールバック
docker service rollback ha-app_web
```

### ヘルスチェックが失敗する場合

```bash
# ヘルスチェックのログを確認
docker service ps ha-app_web

# コンテナ内でヘルスチェックコマンドを実行
docker exec <container-id> curl -f http://localhost:5000/health
```

## 演習課題

1. スタックを3レプリカでデプロイしてください
2. アプリケーションに負荷をかけながら、5レプリカにスケールアウトしてください
3. イメージを更新し、ローリングアップデートを実行してください
4. ランダムにコンテナを停止し、自動復旧を確認してください
5. スタックを削除してクリーンアップしてください

## まとめ

このサンプルで学んだこと：

- `docker service scale` でスケーリング
- ローリングアップデートで無停止デプロイ
- ヘルスチェックで障害検知
- リソース制限でリソース管理
- 再起動ポリシーで自動復旧
- 負荷分散とHA構成の実現

次のステップ: [04. 高度な設定](../04-advanced/) でシークレット、Config、ボリューム、ネットワーク、配置戦略を学びます。
