# pyrefly: ignore [missing-import]
import torch
# pyrefly: ignore [missing-import]
import torch.nn as nn
# pyrefly: ignore [missing-import]
from torchvision import transforms
from PIL import Image, ImageOps
import numpy as np
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

def generate_heatmap(image_path: str, output_path: str):
    """
    Grad-CAM을 이용하여 이미지 상에 폐렴의 활성화 영역(히트맵)을 렌더링하고 저장합니다.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    orig_img = Image.open(image_path).convert("RGB")
    width, height = orig_img.size

    # Grayscale 1-channel tensor로 변환 및 디바이스 이동
    input_tensor = transform(orig_img).unsqueeze(0).to(device)
    input_tensor.requires_grad = True

    features = None
    gradients = None

    def forward_hook(module, input, output):
        nonlocal features
        features = output

    def backward_hook(module, grad_input, grad_output):
        nonlocal gradients
        gradients = grad_output[0]

    # SimpleCNN의 마지막 Conv2d 레이어
    target_layer = model.conv[3]
    h_forward = target_layer.register_forward_hook(forward_hook)
    
    if hasattr(target_layer, "register_full_backward_hook"):
        h_backward = target_layer.register_full_backward_hook(backward_hook)
    else:
        h_backward = target_layer.register_backward_hook(backward_hook)

    try:
        # 순전파
        outputs = model(input_tensor)
        pred_idx = outputs.argmax(1).item()
        score = outputs[0, pred_idx]
        
        # 역전파
        model.zero_grad()
        score.backward()

        if features is not None and gradients is not None:
            # 가중치 계산 (GAP)
            weights = torch.mean(gradients, dim=(2, 3), keepdim=True)
            # Grad-CAM 계산
            cam = torch.sum(weights * features, dim=1, keepdim=True)
            # ReLU 적용
            cam = torch.clamp(cam, min=0)
            
            # 정규화
            cam_min, cam_max = cam.min(), cam.max()
            if cam_max > cam_min:
                cam = (cam - cam_min) / (cam_max - cam_min)
            
            # Numpy 변환 및 크기 복원
            cam_np = cam.squeeze().cpu().detach().numpy()
            heatmap_img = Image.fromarray((cam_np * 255).astype(np.uint8))
            heatmap_resized = heatmap_img.resize((width, height), Image.Resampling.BILINEAR)

            # Pillow ImageOps.colorize를 사용하여 컬러맵 적용 (blue -> green -> red)
            heatmap_color = ImageOps.colorize(heatmap_resized, black="blue", white="red", mid="green")

            # 원본 이미지와 블렌딩 (alpha=0.45)
            blended = Image.blend(orig_img, heatmap_color, alpha=0.45)
            blended.save(output_path)
        else:
            raise RuntimeError("Grad-CAM hook이 활성화 맵 또는 그라디언트를 캡처하지 못했습니다.")
    finally:
        h_forward.remove()
        h_backward.remove()
