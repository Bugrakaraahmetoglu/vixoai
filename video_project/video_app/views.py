import time
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google import genai
from google.genai import types

# Configure the API key
genai.configure(api_key="AIzaSyB2ooIwhfwMcx9sc7wCbrQxDQ-FaPrCwGY")

class GenerateVideoView(APIView):
    def post(self, request):
        prompt = request.data.get("prompt")
        aspect_ratio = request.data.get("aspect_ratio", "16:9")
        
        if not prompt:
            return Response({"error": "Prompt alanı zorunludur."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create a client instance
            client = genai.Client()
            
            # Start the video generation operation
            operation = client.models.generate_videos(
                model="veo-2.0-generate-001",
                prompt=prompt,
                config=types.GenerateVideosConfig(
                    aspect_ratio=aspect_ratio,
                    person_generation="dont_allow"
                )
            )
            
            # Wait for the operation to complete
            while not operation.done:
                time.sleep(10)
                operation = client.operations.get(operation)
            
            # Download the video
            video_id = prompt[:5].replace(" ", "_")
            file_path = f"videos/{video_id}.mp4"
            os.makedirs("videos", exist_ok=True)
            
            # Save the first generated video
            for n, generated_video in enumerate(operation.response.generated_videos):
                client.files.download(file=generated_video.video)
                generated_video.video.save(file_path)
                break  # Just save the first video
            
            return Response({"video_path": file_path})
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
