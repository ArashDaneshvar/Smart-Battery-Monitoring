# How to connect to redis database and check the connection

import redis 

REDIS_HOST = "redis-14980.c300.eu-central-1-1.ec2.cloud.redislabs.com"
REDIS_PORT = 14980
REDIS_USERNAME = "default"
REDIS_PASSWORD = "WclyL3nHTYtgrBy192F9dEfyWQRrx9gi"

#Connect to redis database
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, username=REDIS_USERNAME, password=REDIS_PASSWORD)

#Check the connection
is_connect = redis_client.ping()
print(is_connect)

#set key-value pairs 
set_massage = redis_client.set("massage1", value="Hello World!")
print("my first massage", set_massage)

# get value and decode it using decode() method
get_massage = redis_client.get("massage1")
print(get_massage.decode())

