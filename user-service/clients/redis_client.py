import redis
import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis-master.redis.svc.cluster.local")
REDIS_PASS = os.getenv("REDIS_PASSWORD", None)

redis_client = redis.Redis(host=REDIS_HOST, port=6379, password=REDIS_PASS)
