import os
import sys
sys.path.append('./2_image_caption_to_mood/')
sys.path.append('./3_mood_to_playlist/')
from transformer import MultiModalEarlyFusionBertModel, idx_to_emotion
from run_songs_to_playlist import extract_random_songs, mood_mapping, create_spotify_playlist

import requests
import torch
from PIL import Image
from tqdm import tqdm
from torchvision import transforms
from torchvision.models import resnet18
from transformers import AutoModel, AutoConfig, AutoTokenizer, BertConfig
from transformers import VisionEncoderDecoderModel, GPT2TokenizerFast, ViTImageProcessor

# set device to GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"

caption_model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning").to(device)
caption_tokenizer = GPT2TokenizerFast.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
caption_image_processor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

def get_caption(image_path):
    
    if os.path.exists(image_path):
        image = Image.open(image_path)
    else:
        raise FileNotFoundError(f"Image not found at path: {image_path}")
    
    img = caption_image_processor(image, return_tensors="pt").to(device)
    output = caption_model.generate(**img)
    caption = caption_tokenizer.batch_decode(output, skip_special_tokens=True)[0]
    return caption

def load_state_dict(model, state_dict):
    """
    Load state_dict into the model.
    """
    model_state_dict = model.state_dict()
    new_state_dict = {}
    for key in state_dict.keys():
        # Modify the key to match the model's keys
        new_key = key.replace("image_layer.0", "image_layer").replace("fusion_linear.0", "fusion_linear")
        if new_key in model_state_dict:
            new_state_dict[new_key] = state_dict[key]
    model.load_state_dict(new_state_dict)

def determine_mood(image_path, caption):
    model_path = "./2_image_caption_to_mood"
    # Initialize tokenizer and configuration
    config = BertConfig.from_pretrained('bert-base-uncased')
    tokenizer_config = AutoConfig.from_pretrained("ayoubkirouane/BERT-Emotions-Classifier")

    # Load tokenizer from files
    tokenizer = AutoTokenizer.from_pretrained(
    "bert-base-uncased",
    config=tokenizer_config,
    local_files_only=True  # Load tokenizer files from local directory
    )

    # Initialize model with correct arguments
    resnet_model = resnet18(pretrained=True)
    model = MultiModalEarlyFusionBertModel(config, num_classes=9, cnn_model=resnet_model)
    
    # Load model weights
    model_state_dict = torch.load(os.path.join(model_path, "model_weights.pth"), map_location=torch.device('cpu'))
    load_state_dict(model, model_state_dict)

    outputs = tokenizer(caption, padding=True, truncation=True, return_tensors='pt')
    input_ids = outputs ['input_ids']

    image = Image.open(image_path).convert('RGB')
    transform = transforms.Compose([
        transforms.Resize((224,224)),
        transforms.ToTensor(),
    ])

    image = transform(image).unsqueeze(0)

    model = model.to(device)
    image = image.to(device)
    input_ids = input_ids.to(device)

    # Forward pass, get logits or predictions
    with torch.no_grad():
        outputs = model.forward(input_ids=input_ids, images=image)

    # get predicted mood
    logits = outputs['logits']
    predicted_class_id = logits.argmax(-1).item()

    return predicted_class_id


def main():
    # step 1: generate caption based on images
    image_path = "adolphe-joseph-thomas-monticelli_rural-scene.jpg"
    caption = get_caption(image_path)
    print(caption)

    # step 2: generate mood based on image + caption
    class_id = determine_mood(image_path, caption)
    emotion = idx_to_emotion[class_id]
    print(emotion)

    # step 3: generate spotify playlist based on moods list
    moods = mood_mapping[emotion]
    spotify_songs = extract_random_songs(moods)
    playlist_name = image_path + " playlist"
    print(spotify_songs)
    create_spotify_playlist(playlist_name, spotify_songs)


if __name__ == "__main__":
    main()
