from database import engine
from sqlalchemy import text

try:
    
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("BAŞARILI! Python ve PostgreSQL başarıyla el sıkıştı. Veritabanı köprüsü aktif.")
except Exception as e:
    print("BAĞLANTI HATASI! Lütfen şifrenizi veya veritabanı adını kontrol edin.")
    print(f"Hata detayı: {e}")