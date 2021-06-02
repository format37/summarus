import redis
import time

REDIS_IP = '192.168.1.23' # 10.2.5.212

def summarus_request(question):
    subscriber = redis.StrictRedis(host=REDIS_IP)
    publisher = redis.StrictRedis(host=REDIS_IP) 
    pub = publisher.pubsub()
    sub = subscriber.pubsub()
    sub.subscribe('summarus_client')
    # send
    print('sending')
    publisher.publish("summarus_server", question)
    # receive
    print('receiving')
    while True:
        message = sub.get_message()
        if message and message['type']!='subscribe':
            return message['data'].decode("utf-8")
        time.sleep(1)


with open('server/scripts/init_data.txt') as file:
    article_text = file.read()
article_text = article_text.replace('\n','. ')

print('requested..')
print(summarus_request(article_text))
print('received!')