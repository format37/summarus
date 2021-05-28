import redis

# wait for request
subscriber = redis.StrictRedis(host='localhost', port=int(os.environ['port']))
publisher = redis.StrictRedis(host='localhost', port=int(os.environ['port']))
pub = publisher.pubsub()
sub = subscriber.pubsub()
sub.subscribe('summarus_server')
print('listening..')
while True:
    # receive
    while True:
        message = sub.get_message()
        if message and message['type'] != 'subscribe':
            incoming_text = message['data'].decode("utf-8")
            print('received', incoming_text)
            break
        time.sleep(0.1)

    # generate
    print('generating on:', incoming_text)
    #result = model.play(args_wt_ranker, params, incoming_text)
    result = 'fake result'
    print('sending:', result)
    # send
    publisher.publish("summarus_client", result)
    print('listening..')