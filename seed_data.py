import random
from datetime import datetime, timedelta
from faker import Faker
from database import SessionLocal
import models

fake = Faker('tr_TR') # Türkçe isimler ve veriler üretsin

# Kış ve Yaz aylarını tanımlayalım (Mevsimsellik yaratmak için)
WINTER_MONTHS = [11, 12, 1, 2]
SUMMER_MONTHS = [5, 6, 7, 8]

# Gerçekçi Yedek Parça Listesi (İsim, Kışın mı çok satar Yazın mı?)
PART_TEMPLATES = [
    {"name": "Kış Lastiği", "desc": "Zorlu kış şartları için", "price": 2500.0, "season": "winter"},
    {"name": "Antifriz", "desc": "Motor soğutma sıvısı", "price": 150.0, "season": "winter"},
    {"name": "Klima Gazı", "desc": "Yaz aylarında serinlik için", "price": 300.0, "season": "summer"},
    {"name": "Yaz Lastiği", "desc": "Yüksek performanslı yaz lastiği", "price": 2200.0, "season": "summer"},
    {"name": "Fren Balatası", "desc": "Seramik fren balatası", "price": 850.0, "season": "all"},
    {"name": "Motor Yağı 5W-30", "desc": "Tam sentetik motor yağı", "price": 950.0, "season": "all"},
    {"name": "Silecek Takımı", "desc": "Ön cam silecekleri", "price": 200.0, "season": "all"},
    {"name": "Akü 72Ah", "desc": "Uzun ömürlü akü", "price": 1800.0, "season": "winter"}, # Kışın aküler daha çok biter
    {"name": "Hava Filtresi", "desc": "Kabin hava filtresi", "price": 120.0, "season": "summer"}, # Yaza girerken çok değişir
    {"name": "Buji Seti", "desc": "4'lü ateşleme bujisi", "price": 450.0, "season": "all"},
]

def seed_data():
    db = SessionLocal()
    try:
        print("Veritabanı temizleniyor (Mevcut veriler siliniyor)...")
        # Eski verileri sil (Yukarıdan aşağıya foreign key'leri ezmemek için)
        db.query(models.StockMovement).delete()
        db.query(models.SparePart).delete()
        db.query(models.Supplier).delete()
        db.commit()

        print("1. Tedarikçiler oluşturuluyor...")
        suppliers = []
        for _ in range(3): # 3 tane tedarikçi
            sup = models.Supplier(
                name=fake.company(),
                contact_email=fake.company_email(),
                phone=fake.phone_number()
            )
            db.add(sup)
            suppliers.append(sup)
        db.commit()
        
        # Eklenen tedarikçileri tekrar çekelim ki ID'lerini alabilelim
        for sup in suppliers:
            db.refresh(sup)

        print("2. Yedek Parçalar oluşturuluyor...")
        parts = []
        for template in PART_TEMPLATES:
            # Rastgele bir tedarikçi seç
            random_supplier = random.choice(suppliers)
            part = models.SparePart(
                name=template["name"],
                description=template["desc"],
                price=template["price"],
                stock_quantity=random.randint(50, 200), # Başlangıç stoğu
                supplier_id=random_supplier.id
            )
            # Mevsimsellik bilgisini geçici olarak saklayalım (veritabanına yazılmayacak)
            part._season_type = template["season"] 
            db.add(part)
            parts.append(part)
        db.commit()

        for p in parts:
            db.refresh(p)

        print("3. Geçmiş 1.5 yıllık Satış (OUT) hareketleri üretiliyor (Makine Öğrenmesi için)...")
        
        # Başlangıç tarihi: 1 Ocak 2025
        start_date = datetime(2025, 1, 1)
        # Bitiş tarihi: Bugün (27 Temmuz 2026'ya kadar)
        end_date = datetime.utcnow()
        
        total_days = (end_date - start_date).days
        
        movement_count = 0
        
        for p in parts:
            # Her parça için her gün belli bir ihtimalle satış yapalım
            for day_offset in range(total_days):
                current_date = start_date + timedelta(days=day_offset)
                current_month = current_date.month
                
                # Satış ihtimalini belirleme (Mevsimsellik kurgusu)
                sell_probability = 0.3 # Normalde her gün %30 ihtimalle satış olsun
                
                if p._season_type == "winter" and current_month in WINTER_MONTHS:
                    sell_probability = 0.8 # Kış parçası kışın %80 ihtimalle satar!
                elif p._season_type == "summer" and current_month in SUMMER_MONTHS:
                    sell_probability = 0.8 # Yaz parçası yazın %80 ihtimalle satar!
                
                # Rastgele bir sayı üret (0.0 ile 1.0 arası), ihtimalden küçükse satış yap
                if random.random() < sell_probability:
                    # Ne kadar satıldı?
                    qty_sold = random.randint(1, 5) 
                    
                    # Stok hareketi (Makbuz) oluştur
                    movement = models.StockMovement(
                        part_id=p.id,
                        movement_type="OUT",
                        quantity=qty_sold,
                        movement_date=current_date # Geçmiş tarihi veriyoruz!
                    )
                    db.add(movement)
                    movement_count += 1
        
        db.commit()
        print(f"BİTTİ! Başarıyla 3 Tedarikçi, {len(parts)} Parça ve toplam {movement_count} geçmiş stok hareketi (satış) oluşturuldu.")

    except Exception as e:
        print(f"Hata oluştu: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()