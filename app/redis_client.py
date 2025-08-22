import redis

# Redis konekcija
r = redis.Redis(host="redis", port=6379, decode_responses=True)
