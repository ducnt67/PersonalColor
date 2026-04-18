import os
import sys
import torch
import torch.nn as nn
import torchvision.models as tv_models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

# Thêm thư mục nội bộ để nhận diện được /facer module vừa chép
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR / "src") not in sys.path:
    sys.path.append(str(BASE_DIR / "src"))

import facer
from src.config import MODELS_DIR

_season_model = None
_device = None

_face_detector = None
_face_parser = None


def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_facer_models():
    """ Load FaRL (Face Parsing) model và RetinaFace model """
    global _face_detector, _face_parser
    if _face_detector is None:
        device = get_device()
        _face_detector = facer.face_detector('retinaface/mobilenet', device=device)
    if _face_parser is None:
        device = get_device()
        _face_parser = facer.face_parser('farl/lapa/448', device=device)
    return _face_detector, _face_parser

def load_season_model():
    """ Load Colorinsight ResNet model for Season prediction """
    global _season_model, _device
    if _season_model is not None:
        return _season_model, _device

    _device = get_device()
    num_classes = 4
    
    model = tv_models.resnet18(weights=tv_models.ResNet18_Weights.IMAGENET1K_V1)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    
    model_path = os.path.join(MODELS_DIR, 'best_model_resnet_ALL.pth')
    state_dict = torch.load(model_path, map_location=_device)
    model.load_state_dict(state_dict)
    
    model.to(_device)
    model.eval()
    
    _season_model = model
    return _season_model, _device

def extract_face_skin(pil_img: Image.Image) -> Image.Image:
    """
    Extract facial skin mask from a PIL image using facer library.
    Returns the masked PIL Image containing only the skin.
    """
    device = get_device()
    detector, parser = load_facer_models()

    img_arr = np.array(pil_img.convert("RGB"))
    image_tensor = torch.from_numpy(img_arr).to(device=device) 
    image = facer.hwc2bchw(image_tensor)

    with torch.inference_mode():
        faces = detector(image)

    # Fallback if no face detected
    if not faces or 'rects' not in faces or faces['rects'].numel() == 0:
        return pil_img

    with torch.inference_mode():
        faces = parser(image, faces)

    seg_logits = faces['seg']['logits']
    seg_probs = seg_logits.softmax(dim=1)
    seg_probs = seg_probs.cpu()
    
    tensor = seg_probs.permute(0, 2, 3, 1).squeeze().numpy()
    
    # 1 is skin label in LaPa dataset used by FaRL
    if tensor.ndim == 3 and tensor.shape[-1] > 1:
        face_skin = tensor[:, :, 1]
    else:
        return pil_img

    binary_mask = (face_skin >= 0.5).astype(np.uint8)

    masked_arr = np.zeros_like(img_arr)
    masked_arr[binary_mask == 1] = img_arr[binary_mask == 1]
    
    return Image.fromarray(masked_arr)

def predict_season_colorinsight(pil_img: Image.Image) -> int:
    """
    1. Extract pure skin
    2. ResNet18 inference
    3. Return mapped season Index:
       0: Spring, 1: Summer, 2: Autumn, 3: Winter
    """
    masked_img = extract_face_skin(pil_img)
    model, device = load_season_model()

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    input_tensor = transform(masked_img).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(input_tensor)
        pred_index = output.argmax().item()

    # Original mapping from Colorinsight logic:
    # 0 -> Autumn
    # 1 -> Spring
    # 2 -> Summer
    # 3 -> Winter
    mapping = {
        0: 2, 
        1: 0, 
        2: 1, 
        3: 3  
    }
    return mapping.get(pred_index, 0)
