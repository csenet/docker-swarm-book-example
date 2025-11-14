# Docker Swarm サンプル集

このリポジトリは、Docker Swarmの学習用サンプル集です。基本的な使い方から高度な設定まで、実践的なサンプルを提供しています。

## 必要な環境

- Docker Engine 20.10以上
- Docker Swarm モード有効

### Swarmモードの初期化

```bash
# Swarmマネージャーノードの初期化
docker swarm init

# ワーカーノードの追加（マネージャーノードで実行）
docker swarm join-token worker
```

## サンプル一覧

### 01. 基本的なサービスデプロイ

シンプルなWebアプリケーション（Nginx、Redis等）のデプロイ方法を学びます。

- サービスの作成と削除
- ポートの公開
- レプリカの基本設定

📁 `examples/01-basic-service/`

### 02. スタック構成

Docker Composeファイルを使用した複数サービスのスタックデプロイを学びます。

- docker-compose.ymlの作成
- スタックのデプロイと管理
- サービス間の連携

📁 `examples/02-stack/`

### 03. スケーリング・HA構成

高可用性とスケーラビリティを実現する方法を学びます。

- レプリカ数の動的変更
- ローリングアップデート
- ヘルスチェック
- 負荷分散

📁 `examples/03-scaling-ha/`

### 04. 高度な設定

実運用で必要となる高度な設定を学びます。

- シークレット管理
- Config管理
- ボリュームとストレージ
- オーバーレイネットワーク
- 配置戦略と制約

📁 `examples/04-advanced/`

## 使い方

各サンプルディレクトリに移動して、READMEの手順に従ってください。

```bash
cd examples/01-basic-service
cat README.md
```

## クリーンアップ

```bash
# すべてのスタックを削除
docker stack ls
docker stack rm <stack-name>

# すべてのサービスを削除
docker service ls
docker service rm $(docker service ls -q)

# Swarmモードの無効化（開発環境の場合）
docker swarm leave --force
```

## トラブルシューティング

### サービスが起動しない場合

```bash
# サービスのログを確認
docker service logs <service-name>

# サービスの詳細を確認
docker service ps <service-name> --no-trunc

# ノードの状態を確認
docker node ls
```

### ネットワークの問題

```bash
# ネットワーク一覧を確認
docker network ls

# ネットワークの詳細を確認
docker network inspect <network-name>
```

## 参考リソース

- [Docker Swarm 公式ドキュメント](https://docs.docker.com/engine/swarm/)
- [Docker Compose 仕様](https://docs.docker.com/compose/compose-file/)

## ライセンス

MIT License
