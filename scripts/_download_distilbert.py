"""One-time pre-flight script: download DistilBERT weights to HuggingFace cache."""
from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast

print("Downloading DistilBERT tokenizer...")
DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
print("Downloading DistilBERT model...")
DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)
print("DistilBERT download complete.")
