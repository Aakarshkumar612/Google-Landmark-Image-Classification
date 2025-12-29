import os
import requests

# We'll start with 3 famous landmarks to test the "Brain"
LANDMARKS = {
    "Eiffel_Tower": [
        "https://upload.wikimedia.org/wikipedia/commons/8/85/Tour_Eiffel_2014.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/af/Tour_eiffel_at_sunrise.jpg"
    ],
    "Taj_Mahal": [
        "https://upload.wikimedia.org/wikipedia/commons/1/1d/Taj_Mahal_%28Edited%29.jpeg",
        "https://upload.wikimedia.org/wikipedia/commons/6/67/Taj_Mahal_in_India_-_World_Heritage.JPG"
    ],
    "Statue_of_Liberty": [
        "https://upload.wikimedia.org/wikipedia/commons/a/a1/Statue_of_Liberty_7.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/d/dd/Lady_Liberty_under_a_blue_sky_%28cropped%29.jpg"
    ]
}

def download_images():
    for landmark, urls in LANDMARKS.items():
        folder_path = os.path.join('data', 'train', landmark)
        os.makedirs(folder_path, exist_ok=True)
        
        for i, url in enumerate(urls):
            try:
                response = requests.get(url, timeout=10)
                file_name = f"{landmark}_{i}.jpg"
                with open(os.path.join(folder_path, file_name), 'wb') as f:
                    f.write(response.content)
                print(f"✅ Downloaded: {file_name}")
            except Exception as e:
                print(f"❌ Failed to download {landmark} image {i}: {e}")

if __name__ == "__main__":
    download_images()