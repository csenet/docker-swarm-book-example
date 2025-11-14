from flask import Flask, jsonify
import redis
import socket
import os

app = Flask(__name__)

# Redis接続設定
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    redis_available = True
except Exception as e:
    redis_available = False
    print(f"Redis connection failed: {e}")

@app.route('/')
def home():
    hostname = socket.gethostname()
    return jsonify({
        'message': 'Docker Swarm Stack Example',
        'hostname': hostname,
        'service': 'app',
        'redis_available': redis_available
    })

@app.route('/api/count')
def count():
    if not redis_available:
        return jsonify({'error': 'Redis not available'}), 500

    try:
        count = redis_client.incr('hit_count')
        hostname = socket.gethostname()
        return jsonify({
            'count': count,
            'hostname': hostname
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    if redis_available:
        try:
            redis_client.ping()
            return jsonify({'status': 'healthy'}), 200
        except:
            return jsonify({'status': 'unhealthy', 'reason': 'redis connection failed'}), 503
    return jsonify({'status': 'healthy', 'note': 'redis not configured'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
