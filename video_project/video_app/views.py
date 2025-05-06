from django.shortcuts import render
import os
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai

# Configure the Google API with your API key
genai.configure(api_key="AIzaSyB2ooIwhfwMcx9sc7wCbrQxDQ-FaPrCwGY")

class GenerateVideoView(APIView):
    def post(self, request):
        prompt_text = request.data.get("prompt")
        aspect_ratio = request.data.get("aspect_ratio", "9:16")

        # Check if the prompt is provided
        if not prompt_text:
            return Response({"error": "Prompt alanı zorunludur."}, status=status.HTTP_400_BAD_REQUEST)

        output_folder = "videos"
        os.makedirs(output_folder, exist_ok=True)

        try:
            # Use the appropriate method to generate the video model
            model = genai.Model.from_pretrained("veo-2.0-generate-001")
            
            # Start the video generation
            response = model.generate_video(
                prompt=prompt_text,
                aspect_ratio=aspect_ratio
            )
            
            # Check if videos were generated successfully
            if response.videos:
                filename_prefix = "_".join(prompt_text.split()[:2])
                
                # Get the first video from the response
                generated_video = response.videos[0]
                video_uri = generated_video.uri
                
                # Download the video using the provided URI
                video_bytes = genai.download_file(uri=video_uri)
                filename = f"{filename_prefix}.mp4"
                filepath = os.path.join(output_folder, filename)
                
                # Save the video to disk
                with open(filepath, "wb") as f:
                    f.write(video_bytes)

                return Response({"video": filepath})
            else:
                return Response({"error": "Video oluşturulamadı."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
