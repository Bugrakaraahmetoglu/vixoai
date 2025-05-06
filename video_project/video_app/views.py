import time
import os
import json
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
        
        # Aspect ratio validasyonu
        if aspect_ratio not in ["16:9", "9:16"]:
            return Response({"error": "Geçersiz aspect_ratio. Sadece '16:9' veya '9:16' olabilir."}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
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
            
            # Video üretimini başlat
            try:
                # Prompt içerisine aspect ratio bilgisini ekleyelim
                full_prompt = f"Create a video with aspect ratio {aspect_ratio}. {prompt}"
                print(f"Kullanılan prompt: {full_prompt}")
                
                # Video üretimi için API isteği
                response = model.generate_content(full_prompt)
                
                print(f"Response tipi: {type(response)}")
                if hasattr(response, "candidates"):
                    print(f"Candidates sayısı: {len(response.candidates)}")

                # Video için dizin oluştur
                video_id = ''.join(c if c.isalnum() else '_' for c in prompt[:10])
                file_path = f"videos/{video_id}.mp4"
                os.makedirs("videos", exist_ok=True)
                
                # Video içeriğini kaydet (API yanıtının yapısına bağlı olarak bu kısım değişebilir)
                # Bu kısım Veo API'nin gerçek yanıt yapısına göre düzenlenmelidir
                if hasattr(response, "candidates") and len(response.candidates) > 0:
                    if hasattr(response.candidates[0], "content") and hasattr(response.candidates[0].content, "parts"):
                        for part in response.candidates[0].content.parts:
                            if hasattr(part, "video_url"):
                                # Video URL'sini indir ve dosyaya kaydet
                                # Bu kısım API'nin gerçek yapısına göre düzenlenmelidir
                                print(f"Video URL: {part.video_url}")
                                # (İndirme kodları burada)
                                # Örnek: download_video(part.video_url, file_path)
                                return Response({"video_path": file_path})
                
                # Eğer video doğrudan yanıtta bulunmuyorsa
                print("Video yanıt içerisinde bulunamadı, yanıt yapısı:")
                print(response.__dict__ if hasattr(response, "__dict__") else "Yanıt yapısı görüntülenemiyor")
                
                # Dönen yanıtı HTTP 200 ile gönder, ancak debug bilgisiyle
                return Response({
                    "status": "processing",
                    "message": "API yanıtı alındı ancak video verisi bulunamadı. Logları kontrol edin.",
                    "response_text": response.text if hasattr(response, "text") else "Yanıt metni yok"
                })
                                
            except Exception as e:
                print(f"API isteği hatası: {str(e)}")
                return Response({"error": f"Video üretim hatası: {str(e)}"}, 
                              status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            print(f"Genel hata: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
