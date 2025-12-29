import os
import requests
from PIL import Image
from io import BytesIO

# 4 landmarks, 5 images each from high-quality public sources
DATA_MAP = {
    "Eiffel_Tower": [
        "https://upload.wikimedia.org/wikipedia/commons/a/a8/Eiffel_Tower_from_immediately_beside_it_wide_angle.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/85/Tour_Eiffel_2014.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/d/d2/Eiffel_tower_at_night_1.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/af/Tour_eiffel_at_sunrise.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/6/6e/Paris_-_Eiffel_Tower_and_Mars_Field.jpg"
    ],
    "Taj_Mahal": [
        "https://upload.wikimedia.org/wikipedia/commons/1/1d/Taj_Mahal_%28Edited%29.jpeg",
        "https://upload.wikimedia.org/wikipedia/commons/6/67/Taj_Mahal_in_India_-_World_Heritage.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/c/c8/Taj_Mahal_in_March_2004.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/d/da/Taj_Mahal%2C_Agra%2C_India_edit3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/b/b5/Taj_Mahal%2C_Agra%2C_India.jpg"
    ],
    "Colosseum": [
        "https://upload.wikimedia.org/wikipedia/commons/5/53/Colosseum_in_Rome%2C_Italy_-_April_2007.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/d/de/Colosseo_2020.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/b/b8/Colosseum_Night.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f3/Rome_Colosseum_Exterior.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/2/23/Colosseum_in_Rome.jpg"
    ]
}

def build_dataset():
    base_path = "data/train"
    for landmark, urls in DATA_MAP.items():
        folder = os.path.join(base_path, landmark)
        os.makedirs(folder, exist_ok=True)
        
        for i, url in enumerate(urls):
            try:
                print(f"Downloading {landmark} {i+1}...")
                response = requests.get(url, timeout=15)
                img = Image.open(BytesIO(response.content)).convert('RGB')
                img.save(os.path.join(folder, f"{landmark}_{i}.jpg"))
            except Exception as e:
                print(f"Failed {url}: {e}")

if __name__ == "__main__":
    build_dataset()
    print("\n✅ Dataset Ready! Check your 'data/train' folder.")