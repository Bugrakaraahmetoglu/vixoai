import os
import time
from google import genai
from google.genai import types

# Klasör ismi
output_folder = "videos"
os.makedirs(output_folder, exist_ok=True)

# API anahtarı
client = genai.Client(api_key="AIzaSyB2ooIwhfwMcx9sc7wCbrQxDQ-FaPrCwGY")

# Prompt
prompt_text = "İki Arkadaş ıssız ormanda yürüyor"

# Video üretim talebi
operation = client.models.generate_videos(
    model="veo-2.0-generate-001",
    prompt=prompt_text,
    config=types.GenerateVideosConfig(
        person_generation="allow_adult",
        aspect_ratio="9:16"
    )
)

# İşlem tamamlanana kadar bekle
while not operation.done:
    print("Video işleniyor, lütfen bekleyin...")
    time.sleep(20)
    operation = client.operations.get(operation)

# Yanıtı kontrol et
if operation.response and hasattr(operation.response, 'generated_videos') and operation.response.generated_videos:
    # İlk iki kelimeden dosya ismini oluştur
    filename_prefix = "_".join(prompt_text.split()[:2])

    # Video indir ve kaydet
    for n, generated_video in enumerate(operation.response.generated_videos):
        video_bytes = client.files.download(file=generated_video.video)
        filename = f"{filename_prefix}.mp4"
        filepath = os.path.join(output_folder, filename)
        with open(filepath, "wb") as f:
            f.write(video_bytes)
        print(f"Video başarıyla kaydedildi: {filepath}")
else:
    print("Video oluşturulamadı veya işlem başarısız oldu. Yanıt:", operation.response)


