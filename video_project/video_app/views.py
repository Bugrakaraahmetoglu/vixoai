import os
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai
from google.generativeai import types

# API anahtarını yapılandır
API_KEY = "AIzaSyB2ooIwhfwMcx9sc7wCbrQxDQ-FaPrCwGY"  # Güvenlik için çevresel değişkenden almalısınız
# API_KEY = os.environ.get("GOOGLE_API_KEY")

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
            # Client oluştur
            client = genai.Client(api_key=API_KEY)
            
            # Video üretim talebi
            operation = client.models.generate_videos(
                model="veo-2.0-generate-001",
                prompt=prompt,
                config=types.GenerateVideosConfig(
                    person_generation="allow_adult",
                    aspect_ratio=aspect_ratio
                )
            )

            # İşlem tamamlanana kadar bekle
            while not operation.done:
                print("Video işleniyor, bekleniyor...")
                time.sleep(15)
                operation = client.operations.get(operation)

            # Video yanıtı geldiyse kaydet
            if operation.response and hasattr(operation.response, 'generated_videos') and operation.response.generated_videos:
                saved_files = []
                for i, generated_video in enumerate(operation.response.generated_videos):
                    video_bytes = client.files.download(file=generated_video.video)
                    filename = f"{'_'.join(prompt.split()[:2])}_{i}.mp4"
                    filepath = os.path.join(OUTPUT_FOLDER, filename)
                    with open(filepath, "wb") as f:
                        f.write(video_bytes)
                    saved_files.append(filepath)

                return Response({"video_paths": saved_files}, status=status.HTTP_200_OK)

            return Response({"error": "Video üretilemedi."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({"error": f"Hata oluştu: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)