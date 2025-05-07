import os
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai
from google.generativeai.types import GenerateVideosConfig

# Ortam değişkeninden API anahtarını al
API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

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
            model_name = "veo-1.5"
            model = genai.GenerativeModel(model_name=model_name)

            operation = model.generate_video(
                prompt=prompt,
                config=GenerateVideosConfig(
                    person_generation="allow_adult",
                    aspect_ratio=aspect_ratio
                )
            )

            # İşlem tamamlanana kadar bekle
            while not operation.done:
                print("Video işleniyor...")
                time.sleep(10)
                operation = genai.get_operation(operation.name)

            # Yanıtı kontrol et
            if operation.response and hasattr(operation.response, 'generated_videos'):
                saved_files = []
                for i, video in enumerate(operation.response.generated_videos):
                    video_bytes = genai.download_file(video.video)
                    filename = f"{'_'.join(prompt.split()[:2])}_{i}.mp4"
                    filepath = os.path.join(OUTPUT_FOLDER, filename)
                    with open(filepath, "wb") as f:
                        f.write(video_bytes)
                    saved_files.append(filepath)
                return Response({"video_paths": saved_files}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Video üretilemedi veya yanıt boş."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({"error": f"Hata oluştu: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
