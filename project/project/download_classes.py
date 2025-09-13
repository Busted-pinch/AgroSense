import urllib.request
import os

# URL of ImageNet 1k labels
url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"

# Ensure directory exists
os.makedirs("app/services", exist_ok=True)

# Save file in your project
save_path = "app/services/imagenet_classes.txt"
urllib.request.urlretrieve(url, save_path)

print("✅ imagenet_classes.txt डाउनलोड झाली:", save_path)
