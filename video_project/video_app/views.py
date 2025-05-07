import os
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google import genai
from google.genai import types

# API anahtarını yapılandır
API_KEY = os.environ.get("GOOGLE_API_KEY", "AIzaSyB2ooIwhfwMcx9sc7wCbrQxDQ-FaPrCwGY")

# Kayıt klasörü oluştur
OUTPUT_FOLDER = "videos"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

class GenerateVideoView(APIView):
    def post(self, request):
        prompt = request.data.get("prompt")
        aspect_ratio = request.data.get("aspect_ratio", "16:9")

        if not prompt:
            return Response({"error": "Prompt alanı zorunludur."}, status=status.HTTP_400_BAD_REQUEST)

        if aspect_ratio not in ["16:9", "9:16"]:
            return Response({"error": "Aspect ratio yalnızca '16:9' veya '9:16' olabilir."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Client oluştur - 0.8.5 sürümüne uygun yapılandırma
            genai.configure(api_key=API_KEY)
            
            # Video üretim talebi - bu satırı güncelleyeceğiz
            try:
                # Eski sürüm için uyarlanmış
                from google.generativeai import generate_videos, get_operation, download_file
                
                operation = generate_videos(
                    model="veo-2.0-generate-001",
                    prompt=prompt,
                    config={
                        "person_generation": "allow_adult",
                        "aspect_ratio": aspect_ratio
                    }
                )
                
                # İşlem tamamlanana kadar bekle
                while not operation.done:
                    print("Video işleniyor, bekleniyor...")
                    time.sleep(15)
                    operation = get_operation(operation.name)
                
                # Video yanıtı geldiyse kaydet
                if operation.response and hasattr(operation.response, "generated_videos"):
                    saved_files = []
                    for i, video in enumerate(operation.response.generated_videos):
                        video_bytes = download_file(video.video)
                        filename = f"{'_'.join(prompt.split()[:2])}_{i}.mp4"
                        filepath = os.path.join(OUTPUT_FOLDER, filename)
                        with open(filepath, "wb") as f:
                            f.write(video_bytes)
                        saved_files.append(filepath)

                    return Response({"video_paths": saved_files}, status=status.HTTP_200_OK)
                
            except ImportError:
                # Alternatif yeni sürüm yaklaşımı
                model = genai.get_model("veo-2.0-generate-001")
                
                response = model.generate_videos(
                    prompt=prompt,
                    config=types.GenerateVideosConfig(
                        person_generation="allow_adult",
                        aspect_ratio=aspect_ratio
                    )
                )
                
                # Video yanıtları işleme
                saved_files = []
                for i, video_obj in enumerate(response.videos):
                    video_data = video_obj.raw_data  # Bu da değişebilir
                    filename = f"{'_'.join(prompt.split()[:2])}_{i}.mp4"
                    filepath = os.path.join(OUTPUT_FOLDER, filename)
                    with open(filepath, "wb") as f:
                        f.write(video_data)
                    saved_files.append(filepath)
                
                return Response({"video_paths": saved_files}, status=status.HTTP_200_OK)

            return Response({"error": "Video üretilemedi."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({"error": f"Hata oluştu: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
