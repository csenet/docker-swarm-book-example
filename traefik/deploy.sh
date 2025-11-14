docker network create --driver overlay --attachable traefik_proxy || true
docker stack deploy -c docker-compose-swarm.yaml traefik
