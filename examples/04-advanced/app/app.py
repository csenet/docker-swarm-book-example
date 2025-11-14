from flask import Flask, jsonify
import redis
import psycopg2
import socket
import os
import json

app = Flask(__name__)

# Secretの読み込みヘルパー関数
def get_secret(secret_name):
    """Secretファイルから値を読み込む"""
    try:
        secret_file = os.getenv(f'{secret_name.upper()}_FILE', f'/run/secrets/{secret_name}')
        with open(secret_file, 'r') as f:
            return f.read().strip()
    except IOError as e:
        print(f"Secret '{secret_name}' not found: {e}")
        return None

# Configの読み込み
def get_config():
    """設定ファイルを読み込む"""
    try:
        config_file = os.getenv('CONFIG_FILE', '/app/config.json')
        with open(config_file, 'r') as f:
            return json.load(f)
    except IOError as e:
        print(f"Config file not found: {e}")
        return {}

# 設定の取得
db_password = get_secret('db_password')
api_key = get_secret('api_key')
config = get_config()

# データベース接続
DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_USER = os.getenv('DB_USER', 'appuser')
DB_NAME = os.getenv('DB_NAME', 'appdb')

def get_db_connection():
    """PostgreSQL接続を取得"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=db_password,
            database=DB_NAME
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

# Redis接続
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    redis_client.ping()
    redis_available = True
except Exception as e:
    redis_available = False
    print(f"Redis connection failed: {e}")

# データベース初期化
def init_db():
    """データベーステーブルを初期化"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS visits (
                    id SERIAL PRIMARY KEY,
                    hostname VARCHAR(255),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Database initialization failed: {e}")
            return False
    return False

# アプリケーション起動時にDB初期化
init_db()

@app.route('/')
def home():
    hostname = socket.gethostname()

    # アクセスをデータベースに記録
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO visits (hostname) VALUES (%s)", (hostname,))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Failed to record visit: {e}")

    # Redisでカウント
    cache_count = 0
    if redis_available:
        try:
            cache_count = redis_client.incr('visit_count')
        except:
            pass

    return jsonify({
        'message': 'Docker Swarm Advanced Example',
        'hostname': hostname,
        'container_id': hostname[:12],
        'cache_count': cache_count,
        'config': config,
        'features': ['Secrets', 'Configs', 'Volumes', 'Networks']
    })

@app.route('/health')
def health():
    """ヘルスチェックエンドポイント"""
    health_status = {
        'status': 'healthy',
        'hostname': socket.gethostname(),
        'redis': 'unknown',
        'database': 'unknown'
    }

    # Redis接続確認
    if redis_available:
        try:
            redis_client.ping()
            health_status['redis'] = 'connected'
        except:
            health_status['redis'] = 'failed'
            health_status['status'] = 'degraded'

    # データベース接続確認
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            health_status['database'] = 'connected'
        except:
            health_status['database'] = 'failed'
            health_status['status'] = 'degraded'
    else:
        health_status['database'] = 'failed'
        health_status['status'] = 'degraded'

    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code

@app.route('/api/stats')
def stats():
    """統計情報"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database not available'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM visits")
        total_visits = cursor.fetchone()[0]

        cursor.execute("""
            SELECT hostname, COUNT(*) as count
            FROM visits
            GROUP BY hostname
            ORDER BY count DESC
        """)
        visits_by_host = [{'hostname': row[0], 'count': row[1]} for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        cache_count = 0
        if redis_available:
            try:
                cache_count = int(redis_client.get('visit_count') or 0)
            except:
                pass

        return jsonify({
            'total_visits': total_visits,
            'cache_count': cache_count,
            'visits_by_host': visits_by_host,
            'hostname': socket.gethostname()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config')
def get_app_config():
    """設定情報を返す（機密情報は除く）"""
    return jsonify({
        'config': config,
        'environment': {
            'DB_HOST': DB_HOST,
            'DB_USER': DB_USER,
            'REDIS_HOST': REDIS_HOST,
            'has_db_password': db_password is not None,
            'has_api_key': api_key is not None
        }
    })

@app.route('/api/secrets')
def check_secrets():
    """Secretsの存在確認（値は返さない）"""
    return jsonify({
        'db_password_exists': db_password is not None,
        'api_key_exists': api_key is not None,
        'note': 'Secret values are not exposed via API'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
