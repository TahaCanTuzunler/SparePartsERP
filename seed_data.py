import random
from datetime import datetime, timedelta
from database import SessionLocal
import models

db = SessionLocal()

# 1. Tedarikçileri Oluştur
suppliers = []
for i in range(1, 6):
    sup = models.Supplier(
        name=f"Tedarikçi {i}",
        contact_email=f"iletisim{i}@tedarikci.com",
        phone=f"555-100{i}"
    )
    db.add(sup)
    db.commit() # Veritabanına yazıp ID atamasını sağlıyoruz
    db.refresh(sup)
    suppliers.append(sup)

# 2. Parçaları Oluştur (20 Çeşit)
parts = []
part_names = [
    "Spor Fren Balatası (M Performance)", "İridyum Buji", "Tam Sentetik Motor Yağı", 
    "Açık Hava Filtresi", "Silecek Takımı", "LED Far Ampulü", "AGM Akü", 
    "Coilover Amortisör", "Performans Debriyaj Seti", "Triger Kayışı",
    "Karbon Polen Filtresi", "Termostat", "Alüminyum Radyatör", "Su Pompası", 
    "Titanyum Egzos Susturucu", "Rot Başı", "Salıncak", "Direksiyon Kutusu", 
    "Krank Sensörü", "Oksijen Sensörü"
]

for i in range(20):
    part = models.SparePart(
        name=f"{part_names[i]}",
        description=f"{part_names[i]} - Orijinal Ekipman",
        price=random.uniform(250.0, 5000.0),
        stock_quantity=random.randint(50, 200),
        supplier_id=random.choice(suppliers).id
    )
    db.add(part)
    db.commit()
    db.refresh(part)
    parts.append(part)

# 3. Satışları (OUT) Oluştur (Ocak 2025 - Temmuz 2026)
start_date = datetime(2025, 1, 1)
end_date = datetime(2026, 7, 28) # Tam 1.5 yıllık aralık
delta_days = (end_date - start_date).days

print("Satış verileri (OUT) oluşturuluyor...")

# Her bir parça için DÜZENLİ döngü (Sadece ID=1 hatasını çözdüğümüz yer)
for part in parts:
    # Her parça bu 1.5 yıllık süreçte rastgele 40 ila 90 farklı günde satılmış olsun
    num_sales_days = random.randint(40, 90) 
    
    for _ in range(num_sales_days):
        random_day_offset = random.randint(0, delta_days)
        sale_date = start_date + timedelta(days=random_day_offset)
        
        movement = models.StockMovement(
            part_id=part.id,
            movement_type="OUT",
            quantity=random.randint(1, 10), # O gün 1 ila 10 adet arası satılmış
            movement_date=sale_date
        )
        db.add(movement)

db.commit()
db.close()
print("MÜKEMMEL! 20 farklı parça için, Ocak 2025'ten Temmuz 2026'ya kadar binlerce satış kaydı başarıyla eklendi.")