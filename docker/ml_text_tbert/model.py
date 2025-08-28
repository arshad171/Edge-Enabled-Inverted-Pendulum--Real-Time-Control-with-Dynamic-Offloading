import random
import string
from transformers import BertTokenizer, BertForSequenceClassification
import torch

batch_size = 2
weights_path = "/app/module/weights"

def get_data(batch_size, word_length=6):
    words = []
    for _ in range(128):
        word = ''.join(random.choices(string.ascii_lowercase, k=word_length))
        words.append(word)

    return ' '.join(words)


class Model:
    def __init__(self):
        self.model_id = "cross-encoder/ms-marco-TinyBERT-L2-v2"
        self.tokenizer = BertTokenizer.from_pretrained(weights_path)
        self.model = BertForSequenceClassification.from_pretrained(weights_path)

    def predict(self, batch_size=batch_size):
        preds = []
        for _ in range(batch_size):
            data = get_data(batch_size)
            inputs = self.tokenizer(data, return_tensors="pt", max_length=512, truncation=True)

            with torch.no_grad():
                outputs = self.model(**inputs)

            logits = outputs.logits

            predicted_class = torch.argmax(logits, dim=1).item()

            preds.append(predicted_class)
        
        return preds




