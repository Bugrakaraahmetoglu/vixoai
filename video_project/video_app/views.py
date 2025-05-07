import os
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai
from google.generativeai import types

# API anahtarını yapılandır
API_KEY = "AIzaSyB2ooIwhfwMcx9sc7wCbrQxDQ-FaPrCwGY"

# Google AI yapılandırması
genai.configure(api_key=API_KEY)

# Kayıt klasörü oluştur
OUTPUT_FOLDER = "videos"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

class GenerateVideoView(APIView):
    def post(self, request):
        prompt = request.data.get("prompt")
        aspect_ratio = request.data.get("aspect_ratio", "16:9")
        person_generation = request.data.get("person_generation", "dont_allow")

        if not prompt:
            return Response({"error": "Prompt alanı zorunludur."}, status=status.HTTP_400_BAD_REQUEST)

        if aspect_ratio not in ["16:9", "9:16"]:
            return Response({"error": "Aspect ratio yalnızca '16:9' veya '9:16' olabilir."}, status=status.HTTP_400_BAD_REQUEST)

        if person_generation not in ["dont_allow", "allow_adult"]:
            return Response({"error": "Person generation yalnızca 'dont_allow' veya 'allow_adult' olabilir."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Client oluştur
            client = genai.Client()
            
            # Video üretim talebi
            operation = client.models.generate_videos(
                model="veo-2.0-generate-001",
                prompt=prompt,
                config=types.GenerateVideosConfig(
                    person_generation=person_generation,
                    aspect_ratio=aspect_ratio
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
                filename_prefix = "_".join(prompt.split()[:2])
                saved_files = []

                # Video indir ve kaydet
                for n, generated_video in enumerate(operation.response.generated_videos):
                    video_bytes = client.files.download(file=generated_video.video)
                    filename = f"{filename_prefix}.mp4"
                    filepath = os.path.join(OUTPUT_FOLDER, filename)
                    with open(filepath, "wb") as f:
                        f.write(video_bytes)
                    saved_files.append(filepath)
                    print(f"Video başarıyla kaydedildi: {filepath}")

                return Response({
                    "message": "Video başarıyla oluşturuldu",
                    "video_paths": saved_files
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "Video oluşturulamadı veya işlem başarısız oldu",
                    "response": str(operation.response)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({"error": f"Hata oluştu: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)