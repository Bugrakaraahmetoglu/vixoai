import time
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai

# Environment değişkeninden API anahtarını al
api_key = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

class GenerateVideoView(APIView):
    def post(self, request):
        prompt = request.data.get("prompt")
        aspect_ratio = request.data.get("aspect_ratio", "16:9")
        
        if not prompt:
            return Response({"error": "Prompt alanı zorunludur."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Mevcut modelleri listele ve debug için yazdır
            models = genai.list_models()
            print("Mevcut modeller:")
            veo_models = []
            for model in models:
                print(f"- {model.name}")
                if "veo" in model.name.lower():
                    veo_models.append(model.name)
            
            if not veo_models:
                return Response(
                    {"error": "Veo video üretim modeli API anahtarınızla kullanılamıyor"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # İlk bulduğumuz Veo modelini kullan
            model_name = veo_models[0]
            print(f"Kullanılan video modeli: {model_name}")
            
            # Model örneği oluştur
            model = genai.GenerativeModel(model_name=model_name)
            
            # Model metodlarını debug için yazdır
            print(f"Model metodları: {dir(model)}")
            
            # İstek yapısını hazırla
            generation_config = {
                "aspect_ratio": aspect_ratio,
                "person_generation": "dont_allow"
            }
            
            # Video üretimini başlat
            try:
                # Metodun varlığını kontrol et
                if hasattr(model, "generate_content"):
                    # Content API ile deneme
                    response = model.generate_content(
                        contents=[{"text": prompt}],
                        generation_config=generation_config
                    )
                    print(f"Response tip: {type(response)}")
                    print(f"Response öznitelikleri: {dir(response)}")
                    
                elif hasattr(model, "start_generation"):
                    # Alternatif metod denemesi
                    response = model.start_generation(
                        prompt=prompt,
                        generation_config=generation_config
                    )
                    print(f"Response tip: {type(response)}")
                    print(f"Response öznitelikleri: {dir(response)}")
                else:
                    # Hiçbir bilinen metod bulunamadıysa
                    return Response({
                        "error": "Video üretimi için uygun metod bulunamadı. Google GenAI API değişmiş olabilir.",
                        "available_methods": dir(model)
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                # Video dizini oluştur
                video_id = ''.join(c if c.isalnum() else '_' for c in prompt[:10])
                file_path = f"videos/{video_id}.mp4"
                os.makedirs("videos", exist_ok=True)
                
                # Debug için yanıtı kontrol et
                if hasattr(response, "text"):
                    print(f"Response text: {response.text}")
                
                return Response({
                    "status": "processing", 
                    "message": "Video üretimi başlatıldı. Detaylar için logları kontrol ediniz."
                })
                
            except AttributeError as e:
                print(f"AttributeError: {str(e)}")
                return Response({
                    "error": f"Metod kullanılamıyor: {str(e)}. Lütfen Veo API dökümantasyonunu kontrol ediniz.",
                    "available_methods": dir(model)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            print(f"Hata: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
