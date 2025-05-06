from django.shortcuts import render
import os
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai
from google.generativeai import types

# Google API client başlat
client = genai.Client(api_key="AIzaSyB2ooIwhfwMcx9sc7wCbrQxDQ-FaPrCwGY")

class GenerateVideoView(APIView):
    def post(self, request):
        prompt_text = request.data.get("prompt")
        aspect_ratio = request.data.get("aspect_ratio", "9:16")

        if not prompt_text:
            return Response({"error": "prompt alanı zorunludur."}, status=status.HTTP_400_BAD_REQUEST)

        output_folder = "videos"
        os.makedirs(output_folder, exist_ok=True)

        try:
            operation = client.models.generate_videos(
                model="veo-2.0-generate-001",
                prompt=prompt_text,
                config=types.GenerateVideosConfig(
                    person_generation="allow_adult",
                    aspect_ratio=aspect_ratio
                )
            )
            print(operation.response)

            while not operation.done:
                time.sleep(20)
                operation = client.operations.get(operation)

            if operation.response and hasattr(operation.response, 'generated_videos') and operation.response.generated_videos:
                filename_prefix = "_".join(prompt_text.split()[:2])
                
                # İlk videoyu alıyoruz
                generated_video = operation.response.generated_videos[0]
                video_bytes = client.files.download(file=generated_video.video)
                filename = f"{filename_prefix}.mp4"
                filepath = os.path.join(output_folder, filename)
                
                with open(filepath, "wb") as f:
                    f.write(video_bytes)

                return Response({"video": filepath})
            else:
                return Response({"error": "Video oluşturulamadı."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

