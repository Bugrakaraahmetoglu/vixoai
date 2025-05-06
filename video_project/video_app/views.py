from django.shortcuts import render
import os
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google import genai
from google.genai import types

# API key otomatik olarak ortam değişkeninden alınır (GOOGLE_API_KEY)
client = genai.Client()

class GenerateVideoView(APIView):
    def post(self, request):
        prompt_text = request.data.get("prompt")
        aspect_ratio = request.data.get("aspect_ratio", "9:16")

        if not prompt_text:
            return Response({"error": "Prompt alanı zorunludur."}, status=status.HTTP_400_BAD_REQUEST)

        output_folder = "videos"
        os.makedirs(output_folder, exist_ok=True)

        try:
            # Video oluşturma isteği
            operation = client.models.generate_videos(
                model="veo-2.0-generate-001",
                prompt=prompt_text,
                config=types.GenerateVideosConfig(
                    person_generation="dont_allow",
                    aspect_ratio=aspect_ratio
                ),
            )

            # İşlem tamamlanana kadar bekle
            while not operation.done:
                time.sleep(20)
                operation = client.operations.get(operation)

            # İlk videoyu kaydet
            if operation.response and operation.response.generated_videos:
                generated_video = operation.response.generated_videos[0]
                video_file = client.files.download(file=generated_video.video)

                filename = f"{'_'.join(prompt_text.split()[:2])}.mp4"
                filepath = os.path.join(output_folder, filename)

                with open(filepath, "wb") as f:
                    f.write(video_file.read())

                return Response({"video": filepath})

            else:
                return Response({"error": "Video oluşturulamadı."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
