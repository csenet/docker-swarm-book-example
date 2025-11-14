#!/bin/bash

set -e

# Docker Configが既に存在する場合は削除
docker config rm swarm-cd-repos 2>/dev/null || true
docker config rm swarm-cd-stacks 2>/dev/null || true

# Docker Configを作成
docker config create swarm-cd-repos repos.yaml
docker config create swarm-cd-stacks stacks.yaml

# スタックをデプロイ
docker stack deploy --compose-file docker-compose.yaml swarm-cd

echo "Deployment completed successfully!"
