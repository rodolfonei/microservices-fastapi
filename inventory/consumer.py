from main import redis, Product
import time

key = "order_completed"
group = "inventory-group"

try:
    redis.xgroup_create(key, group)
except:
    print("Group already exists!")

while True:
    try:
        results = redis.xreadgroup(group, key, { key: ">"}, None)

        print(results)
    except Exception as e:
        print(str(e))

    time.sleep(1)