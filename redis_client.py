import redis 


r = redis.Redis(
    host='redis-16749.c274.us-east-1-3.ec2.redns.redis-cloud.com',
    port=16749,
    decode_responses=True,
    username="default",
    password="fj4qcz48xIsGp1X4iyNhJyp6pt1UxFks",
)
# success = r.set('foo', 'bar')
# result = r.get('foo')
# print(result)