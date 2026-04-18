import streamlit as st
import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0
import torchvision.transforms as transforms
from PIL import Image

from src.config import MODEL_PATH, FITZ_MAP, UNDER_MAP, SEASON_MAP

class PersonalColorModel(nn.Module):
    def __init__(self):
        super(PersonalColorModel, self).__init__()
        self.backbone = efficientnet_b0(weights=None)
        num_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Identity()
        self.head_fitz = nn.Linear(num_features, 6)
        self.head_under = nn.Linear(num_features, 3)
        self.head_season = nn.Linear(num_features, 4)

    def forward(self, x):
        features = self.backbone(x)
        return (
            self.head_fitz(features),
            self.head_under(features),
            self.head_season(features)
        )

@st.cache_resource
def load_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = PersonalColorModel()
    try:
        checkpoint = torch.load(MODEL_PATH, map_location=device)
        if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
        else:
            state_dict = checkpoint
            
        model.load_state_dict(state_dict)
        model.to(device)
        model.eval()
        return model, device
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, device

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def predict(img):
    model, device = load_model()
    if model is None:
        return "Unknown", "Unknown", "Unknown"
        
    img_tensor = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        out_fitz, out_under, out_season = model(img_tensor)
        p_fitz = torch.argmax(out_fitz, dim=1).item()
        p_under = torch.argmax(out_under, dim=1).item()
        p_season_default = torch.argmax(out_season, dim=1).item()

    # Integration with ColorInsight core for highly accurate season prediction on masked skin.
    try:
        from src.services.colorinsight_service import predict_season_colorinsight
        p_season = predict_season_colorinsight(img)
    except Exception as e:
        print(f"Error using Colorinsight: {e}")
        p_season = p_season_default

    return FITZ_MAP.get(p_fitz, "Unknown"), UNDER_MAP.get(p_under, "Unknown"), SEASON_MAP.get(p_season, "Unknown")
