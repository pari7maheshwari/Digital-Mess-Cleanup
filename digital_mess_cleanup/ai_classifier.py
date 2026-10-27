from pathlib import Path

import streamlit as st
from PIL import Image, ImageOps

from .config import AI_LABELS, AI_MODEL_NAME, AI_PROMPT_TEMPLATES


def _extract_features(output, torch):
    """Handle the tensor and model-output formats used by Transformers."""
    if isinstance(output, torch.Tensor):
        return output

    pooled_output = getattr(output, "pooler_output", None)
    if isinstance(pooled_output, torch.Tensor):
        return pooled_output

    if isinstance(output, tuple):
        for value in output:
            if isinstance(value, torch.Tensor) and value.ndim == 2:
                return value

    raise TypeError(
        "The CLIP model returned an unsupported feature output."
    )


@st.cache_resource(max_entries=1, show_spinner=False)
def load_clip_model(model_name: str = AI_MODEL_NAME):
    """Load CLIP once and cache the encoded category labels as well."""
    import torch
    from transformers import CLIPModel, CLIPProcessor

    processor = CLIPProcessor.from_pretrained(model_name)
    model = CLIPModel.from_pretrained(model_name)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    # Category labels stay the same during a scan, so encode them only once.
    prompts = [
        template.format(label)
        for label in AI_LABELS
        for template in AI_PROMPT_TEMPLATES
    ]
    text_inputs = processor(
        text=prompts,
        return_tensors="pt",
        padding=True,
        truncation=True,
    )
    text_inputs = {name: value.to(device) for name, value in text_inputs.items()}
    with torch.inference_mode():
        text_features = _extract_features(
            model.get_text_features(**text_inputs), torch
        )
        text_features = text_features.reshape(
            len(AI_LABELS), len(AI_PROMPT_TEMPLATES), -1
        ).mean(dim=1)
        text_features = text_features / text_features.norm(
            p=2, dim=-1, keepdim=True
        )

    return processor, model, torch, text_features, device


def classify_image_with_ai(
    image_path: Path, model_name: str = AI_MODEL_NAME
):
    """Return the best category and its relative (not calibrated) score."""
    processor, model, torch, text_features, device = load_clip_model(model_name)

    with Image.open(image_path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        # Resize very large images before preprocessing to limit CPU/memory use.
        image.thumbnail((1024, 1024))
        inputs = processor(images=image, return_tensors="pt")
    pixel_values = inputs["pixel_values"].to(device)

    with torch.inference_mode():
        image_features = _extract_features(
            model.get_image_features(pixel_values=pixel_values),
            torch,
        )
        image_features = image_features / image_features.norm(
            p=2, dim=-1, keepdim=True
        )
        logits = model.logit_scale.exp() * image_features @ text_features.T
        probabilities = logits.softmax(dim=1)[0]

    best_index = int(probabilities.argmax().item())
    best_label = AI_LABELS[best_index]
    score = float(probabilities[best_index].item())
    return best_label, score



# SCAN AND ORGANIZE

# --------------------------------------------------
