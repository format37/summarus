import redis
import time


def summarus_request(question):
    subscriber = redis.StrictRedis(host='localhost', port=6379)
    publisher = redis.StrictRedis(host='localhost', port=6379)
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
            break
        time.sleep(1)


with open('data/content_a.txt') as file:
    article_text = file.read()
article_text = article_text.replace('\n','. ')

print('requested..')
print(summarus_request(article_text))
print('received!')