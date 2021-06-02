import os
import time
import redis
import torch
from transformers import MBartTokenizer, MBartForConditionalGeneration

# init summarizer
model_name = "IlyaGusev/mbart_ru_sum_gazeta"
device = "cuda:0" if torch.cuda.is_available() else "cpu"
tokenizer = MBartTokenizer.from_pretrained(model_name)
model = MBartForConditionalGeneration.from_pretrained(model_name).to(device)

def summarize(article_text, tokenizer, model, device, no_repeat_ngram_size):    
    input_ids = tokenizer.prepare_seq2seq_batch(
        [article_text],
        src_lang="en_XX", # fairseq training artifact
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=600 # 600
    ).to(device)["input_ids"]

    output_ids = model.generate(
        input_ids=input_ids,
        max_length=162, #162
        no_repeat_ngram_size=no_repeat_ngram_size, # 3
        num_beams=5, # 5
        top_k=0 # 0
    )[0]

    summary = tokenizer.decode(output_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)
    return summary

# wait for request
subscriber = redis.StrictRedis(host='redis')
publisher = redis.StrictRedis(host='redis')
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
            # print('received', incoming_text)
            print('received')
            break
        time.sleep(0.1)

    # generate
    # print('generating on:', incoming_text)
    print('generating..')
    result =  summarize(incoming_text, tokenizer, model, device, 3)
    print('sending:', result)
    # send
    publisher.publish("summarus_client", result)
    print('listening..')
