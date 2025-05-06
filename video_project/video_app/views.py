from django.shortcuts import render
import os
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai

# Configure the Google API
genai.configure(api_key="AIzaSyB2ooIwhfwMcx9sc7wCbrQxDQ-FaPrCwGY")

class GenerateVideoView(APIView):
    def post(self, request):
        prompt_text = request.data.get("prompt")
        aspect_ratio = request.data.get("aspect_ratio", "9:16")

        if not prompt_text:
            return Response({"error": "prompt alanı zorunludur."}, status=status.HTTP_400_BAD_REQUEST)

        output_folder = "videos"
        os.makedirs(output_folder, exist_ok=True)

        try:
            # Get the video generation model
            model = genai.get_generative_model(model_name="veo-2.0-generate-001")
            
            # Start the generation operation
            generation_config = {
                "person_generation": "allow_adult",
                "aspect_ratio": aspect_ratio
            }
            
            response = model.generate_video(
                prompt=prompt_text,
                generation_config=generation_config
            )
            
            # Get the operation ID to track progress
            operation_name = response.operation.name
            
            # Poll until completion
            while not response.operation.done:
                time.sleep(20)
                response = genai.get_operation(operation_name)
            
            # Check for results
            if hasattr(response, 'result') and response.result and hasattr(response.result, 'videos') and response.result.videos:
                filename_prefix = "_".join(prompt_text.split()[:2])
                
                # Get the first video
                generated_video = response.result.videos[0]
                video_bytes = genai.download_file(uri=generated_video.uri)
                filename = f"{filename_prefix}.mp4"
                filepath = os.path.join(output_folder, filename)
                
                with open(filepath, "wb") as f:
                    f.write(video_bytes)

                return Response({"video": filepath})
            else:
                return Response({"error": "Video oluşturulamadı."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)