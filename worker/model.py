# pyrefly: ignore [missing-import]
import torch
# pyrefly: ignore [missing-import]
import torch.nn as nn
# pyrefly: ignore [missing-import]
from torchvision import transforms
from PIL import Image
import os

# 1. SimpleCNN 모델 정의 (노트북과 일치)
class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),  
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2) 
        )
        self.fc = nn.Sequential(nn.Flatten(), nn.Linear(32*32*32, 2))

    def forward(self, x):
        return self.fc(self.conv(x))

# 모델 로드 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SimpleCNN().to(device)

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "models", "pneumonia_model.pth")

if os.path.exists(MODEL_PATH):
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device, weights_only=True))
        print(f"Pneumonia model successfully loaded from {MODEL_PATH}")
    except Exception as e:
        print(f"Error loading model weights: {e}")
else:
    print(f"Warning: Model file not found at {MODEL_PATH}. Prediction will run with initialized weights.")

model.eval()

# 이미지 변환 파이프라인 (노트북과 일치)
transform = transforms.Compose([
    transforms.Grayscale(),
    transforms.Resize((128, 128)),
    transforms.ToTensor()
])

def predict_pneumonia(image_path: str) -> dict:
    """
    흉부 X-ray 이미지를 활용하여 폐렴 예측 결과를 반환합니다.
    Args:
        image_path (str): 분석할 X-ray 이미지 파일 경로
    Returns:
        dict: 예측 결과 ("NORMAL" 또는 "PNEUMONIA") 및 상세 확률 정보
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    # 이미지 열기 및 RGB -> Grayscale 등 변환
    image = Image.open(image_path)
    
    # 텐서 변환 및 배치 차원 추가 [1, 1, 128, 128]
    input_tensor = transform(image).unsqueeze(0).to(device)

    # 예측 수행
    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.softmax(outputs, dim=1)[0]
        prediction_idx = outputs.argmax(1).item()

    classes = ["NORMAL", "PNEUMONIA"]
    prediction = classes[prediction_idx]
    
    return {
        "prediction": prediction,
        "probability_normal": float(probabilities[0]),
        "probability_pneumonia": float(probabilities[1]),
        "confidence": float(probabilities[prediction_idx])
    }
