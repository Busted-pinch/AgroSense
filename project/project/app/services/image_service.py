import torch
from torchvision import models, transforms
from fastapi import UploadFile
from PIL import Image
import io

# Load pre-trained model
model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
model.eval()

# Load ImageNet classes
with open("app/services/imagenet_classes.txt") as f:
    imagenet_classes = [line.strip() for line in f.readlines()]

async def process_image(file: UploadFile):
    try:
        image_bytes = await file.read()
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])
        input_tensor = preprocess(img).unsqueeze(0)

        with torch.no_grad():
            outputs = model(input_tensor)
            _, predicted_idx = outputs.max(1)
            class_name = imagenet_classes[predicted_idx.item()]

        return {"class_name": class_name}

    except Exception as e:
        return {"error": str(e)}
