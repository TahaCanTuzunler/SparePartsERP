# 1. İçinde Python 3.11 yüklü olan hafif (slim) bir işletim sistemi indir
FROM python:3.11-slim

# 2. Konteyner içinde çalışma klasörümüzü /app olarak belirle
WORKDIR /app

# 3. Kütüphane listesini konteynerin içine kopyala
COPY requirements.txt .

# 4. Kütüphaneleri indir ve kur
RUN pip install --no-cache-dir -r requirements.txt

# 5. Senin yazdığın tüm kodları (main.py, html dosyaları vs.) konteynere kopyala
COPY . .

# 6. Uygulamayı 8000 portundan dışarıya yayınlayarak çalıştır
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]