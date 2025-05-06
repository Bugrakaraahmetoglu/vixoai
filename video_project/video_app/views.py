import time
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai
from google.generativeai.types import GenerateVideosConfig

genai.configure(api_key="SENİN_API_KEYİN")

class GenerateVideoView(APIView):
    def post(self, request):
        prompt = request.data.get("prompt")
        aspect_ratio = request.data.get("aspect_ratio", "16:9")

        if not prompt:
            return Response({"error": "Prompt alanı zorunludur."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            client = genai.GenerativeModel(model_name="veo-2.0-generate-001")

            operation = client.generate_video(
                prompt=prompt,
                config=GenerateVideosConfig(
                    aspect_ratio=aspect_ratio,
                    person_generation="dont_allow"
                )
            )

            # İşlem tamamlanana kadar bekle
            while not operation.done:
                time.sleep(10)
                operation = genai.get_operation(name=operation.name)

            # Videoyu indir
            video_data = operation.response.generated_videos[0].video
            file_path = f"videos/{prompt[:5]}.mp4"
            os.makedirs("videos", exist_ok=True)
            genai.download_file(video_data.uri, file_path)

            return Response({"video_path": file_path})

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
