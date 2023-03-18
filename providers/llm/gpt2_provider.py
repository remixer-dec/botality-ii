import numpy as np
import torch

tokenizer = None
model = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def init(model_path):
  global model, tokenizer
  from transformers import (GPT2LMHeadModel, GPT2Tokenizer)
  model_type = 'gpt2'
  model_class, tokenizer_class = GPT2LMHeadModel, GPT2Tokenizer
  tokenizer = tokenizer_class.from_pretrained(model_path)
  model = model_class.from_pretrained(model_path)
  model = model.to(device)


def tokenize(prompt):
  encoded_prompt = tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt")
  encoded_prompt = encoded_prompt.to(device)
  return encoded_prompt[:, :1024]


def generate(encoded_prompt, length=64, model_params={}):
  output_sequences = model.generate(
      input_ids=encoded_prompt,
      max_length=length + len(encoded_prompt[0]),
      do_sample=True,
      num_return_sequences=1,
      **model_params
  )
  return tokenizer.decode(output_sequences[0])