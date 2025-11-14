from flask import Flask, jsonify
import redis
import socket
import os
import time

app = Flask(__name__)

# 設定
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
VERSION = os.getenv('VERSION', '1.0')

# Redis接続
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    redis_client.ping()
    redis_available = True
except Exception as e:
    redis_available = False
    print(f"Redis connection failed: {e}")

@app.route('/')
def home():
    hostname = socket.gethostname()

    # アクセスカウント
    count = 0
    if redis_available:
        try:
            count = redis_client.incr('access_count')
        except:
            pass

    return jsonify({
        'message': 'Docker Swarm HA Example',
        'version': VERSION,
        'hostname': hostname,
        'container_id': hostname[:12],
        'access_count': count,
        'timestamp': time.time()
    })

@app.route('/health')
def health():
    """ヘルスチェックエンドポイント"""
    health_status = {
        'status': 'healthy',
        'version': VERSION,
        'hostname': socket.gethostname(),
        'redis': 'connected' if redis_available else 'disconnected'
    }

    if redis_available:
        try:
            redis_client.ping()
            return jsonify(health_status), 200
        except:
            health_status['status'] = 'unhealthy'
            health_status['redis'] = 'failed'
            return jsonify(health_status), 503

    return jsonify(health_status), 200

@app.route('/api/stats')
def stats():
    """統計情報"""
    if not redis_available:
        return jsonify({'error': 'Redis not available'}), 500

    try:
        access_count = redis_client.get('access_count') or 0
        return jsonify({
            'access_count': int(access_count),
            'version': VERSION,
            'hostname': socket.gethostname()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/slow')
def slow():
    """遅いエンドポイント（負荷テスト用）"""
    time.sleep(2)
    return jsonify({
        'message': 'Slow response',
        'hostname': socket.gethostname(),
        'version': VERSION
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
