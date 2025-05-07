import os
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai

# API anahtarını yapılandır
API_KEY = "AIzaSyB2ooIwhfwMcx9sc7wCbrQxDQ-FaPrCwGY"  # Güvenlik için çevresel değişkenden almalısınız
# API_KEY = os.environ.get("GOOGLE_API_KEY")

# Google AI yapılandırması
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
            # Model oluştur
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Video üretim talebi
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.9,
                    "top_p": 1,
                    "top_k": 32,
                    "max_output_tokens": 2048,
                }
            )

            # Video yanıtı geldiyse kaydet
            if response and hasattr(response, 'text'):
                # Burada response.text içeriğini video olarak kaydetme işlemi yapılmalı
                # Not: Google'ın Generative AI API'si şu anda doğrudan video üretimi için
                # sınırlı destek sunuyor. Bu nedenle alternatif bir çözüm gerekebilir.
                return Response({"message": "Video üretim talebi alındı", "response": response.text}, status=status.HTTP_200_OK)

            return Response({"error": "Video üretilemedi."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({"error": f"Hata oluştu: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)