import json
import logging

import redis

from app.config import settings

logger = logging.getLogger(__name__)


class FeatureCache:
    def __init__(self):
        try:
            self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.client.ping()
            self.available = True
        except Exception:
            logger.warning("redis not available, running without cache")
            self.client = None
            self.available = False

    def get_user_stats(self, user_id):
        if not self.available:
            return None
        try:
            key = f"user_stats:{user_id}"
            data = self.client.get(key)
            if data:
                return json.loads(data)
        except Exception:
            return None
        return None

    def set_user_stats(self, user_id, stats, ttl=3600):
        if not self.available:
            return
        try:
            key = f"user_stats:{user_id}"
            self.client.setex(key, ttl, json.dumps(stats))
        except Exception:
            pass

    def invalidate_user(self, user_id):
        if not self.available:
            return
        try:
            key = f"user_stats:{user_id}"
            self.client.delete(key)
        except Exception:
            pass

    def get_recent_transactions(self, user_id, window="1h"):
        if not self.available:
            return None
        try:
            key = f"recent_txns:{user_id}:{window}"
            data = self.client.get(key)
            if data:
                return json.loads(data)
        except Exception:
            return None
        return None

    def set_recent_transactions(self, user_id, transactions, window="1h", ttl=300):
        if not self.available:
            return
        try:
            key = f"recent_txns:{user_id}:{window}"
            self.client.setex(key, ttl, json.dumps(transactions))
        except Exception:
            pass

    def increment_txn_count(self, user_id):
        if not self.available:
            return 0
        try:
            key = f"txn_count:{user_id}"
            count = self.client.incr(key)
            self.client.expire(key, 86400)
            return count
        except Exception:
            return 0

    def health_check(self):
        if not self.available:
            return {"status": "unavailable"}
        try:
            self.client.ping()
            return {"status": "connected"}
        except Exception:
            return {"status": "error"}
