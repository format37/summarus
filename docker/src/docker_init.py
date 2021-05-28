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


with open('test_data.txt') as file:
    article_text = file.read()
article_text = article_text.replace('\n','. ')

# generate
print('generating..', len(article_text))
result =  summarize(article_text, tokenizer, model, device, 3)
print(result)
print('Init complete')