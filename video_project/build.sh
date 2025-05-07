#!/usr/bin/env bash
# Django projesi için dağıtım komut dosyası

# Python bağımlılıklarını yükle
pip install -r requirements.txt

# Statik dosyaları topla
python manage.py collectstatic --no-input

# Veritabanı geçişlerini uygula
python manage.py migrate