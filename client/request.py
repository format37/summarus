import requests
import json


def main():
    docker_server_address = 'http://localhost:2800/summarize'

    with open('init_data.txt') as file:
        article_text = file.read()
    article_text = article_text.replace('\n','. ')

    request = {
        'in_text':article_text,
        'in_max_length':600,
        'out_no_repeat_ngram_size':3,
        'out_num_beams':5,
        'out_top_k':0
    }
    request_str = json.dumps(request)
    r = requests.post(docker_server_address, json=request_str)
    print(r.text)


if __name__ == '__main__':
    main()
