from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse # HTML dosyamızı sunmak için eklendi
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine

import joblib
import pandas as pd
from datetime import datetime
from sqlalchemy.sql import func

# Veritabanı tablolarının oluşturulduğundan emin oluyoruz
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Spare Parts ERP API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- FRONTEND (ARAYÜZ) SUNUCUSU ---
# Artık ana sayfaya girildiğinde index.html dosyasını gösterecek
@app.get("/", response_class=FileResponse)
def read_root():
    return "index.html"

# --- TEDARİKÇİ (SUPPLIER) UÇ NOKTALARI ---
@app.post("/suppliers/", response_model=schemas.SupplierResponse)
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):
    db_supplier = db.query(models.Supplier).filter(models.Supplier.contact_email == supplier.contact_email).first()
    if db_supplier:
        raise HTTPException(status_code=400, detail="Bu e-posta adresi zaten kayitli.")
    new_supplier = models.Supplier(**supplier.model_dump())
    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)
    return new_supplier

@app.get("/suppliers/", response_model=list[schemas.SupplierResponse])
def read_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Supplier).offset(skip).limit(limit).all()

@app.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    # 1. Önce silinecek tedarikçiyi bul
    db_supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    
    # 2. Eğer öyle bir tedarikçi yoksa hata fırlat
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Silinmek istenen tedarikçi bulunamadı.")
        
    # 3. Bulunduysa veritabanından sil ve onayla
    db.delete(db_supplier)
    db.commit()
    return {"message": f"Tedarikçi (ID: {supplier_id}) başarıyla silindi."}

# --- YEDEK PARÇA (SPARE PART) UÇ NOKTALARI ---
@app.post("/parts/", response_model=schemas.SparePartResponse)
def create_spare_part(part: schemas.SparePartCreate, db: Session = Depends(get_db)):
    db_supplier = db.query(models.Supplier).filter(models.Supplier.id == part.supplier_id).first()
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Tedarikci bulunamadi.")
    new_part = models.SparePart(**part.model_dump())
    db.add(new_part)
    db.commit()
    db.refresh(new_part)
    return new_part

@app.get("/parts/", response_model=list[schemas.SparePartResponse])
def read_parts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.SparePart).offset(skip).limit(limit).all()

@app.delete("/parts/{part_id}")
def delete_spare_part(part_id: int, db: Session = Depends(get_db)):
    # 1. Silinecek parçayı veritabanında ara
    db_part = db.query(models.SparePart).filter(models.SparePart.id == part_id).first()
    
    # 2. Parça yoksa 404 hatası döndür
    if not db_part:
        raise HTTPException(status_code=404, detail="Silinmek istenen yedek parça bulunamadı.")
    
    # 3. Bulunduysa sil ve veritabanına kaydet
    db.delete(db_part)
    db.commit()
    return {"message": f"Yedek parça (ID: {part_id}) başarıyla silindi."}

@app.patch("/parts/{part_id}", response_model = schemas.SparePartUpdate)
def update_spare_part(part_id: int, part: schemas.SparePartUpdate, db: Session = Depends(get_db)):
    db_part = db.query(models.SparePart).filter(models.SparePart.id == part_id).first()

    if not db_part:
        raise HTTPException(status_code=404, detail="Güncellenmek istenen yedek parça bulunamadı.")

    update_data = part.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_part, key, value)

    db.commit()
    db.refresh(db_part)
    
    return db_part

# --- STOK HAREKETLERİ (STOCK MOVEMENTS) UÇ NOKTALARI ---
@app.post("/movements/", response_model=schemas.StockMovementResponse)
def create_stock_movement(movement: schemas.StockMovementCreate, db: Session = Depends(get_db)):
    db_part = db.query(models.SparePart).filter(models.SparePart.id == movement.part_id).first()
    if not db_part:
        raise HTTPException(status_code=404, detail="Hata: Yedek parça bulunamadi.")
    
    movement.movement_type = movement.movement_type.upper()
    if movement.movement_type not in ["IN", "OUT"]:
        raise HTTPException(status_code=400, detail="Hata: Hareket tipi sadece 'IN' veya 'OUT' olmalidir.")
    
    if movement.movement_type == "OUT":
        if db_part.stock_quantity < movement.quantity:
            raise HTTPException(status_code=400, detail=f"Hata: Yetersiz stok! Mevcut stok: {db_part.stock_quantity}")
        db_part.stock_quantity -= movement.quantity
    elif movement.movement_type == "IN":
        db_part.stock_quantity += movement.quantity

    new_movement = models.StockMovement(**movement.model_dump())
    db.add(new_movement)
    db.commit()
    db.refresh(new_movement)
    return new_movement

@app.get("/movements/", response_model=list[schemas.StockMovementResponse])
def read_movements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    movements = db.query(models.StockMovement).offset(skip).limit(limit).all()
    return movements

@app.delete("/movements/{movement_id}")
def delete_stock_movement(movement_id: int, db: Session = Depends(get_db)):
    # 1. Silinecek stok hareketini bul
    db_movement = db.query(models.StockMovement).filter(models.StockMovement.id == movement_id).first()
    
    if not db_movement:
        raise HTTPException(status_code=404, detail="Silinmek istenen stok hareketi bulunamadı.")
        
    # 2. Harekete ait yedek parçayı bul (Stok miktarını düzeltmek için)
    db_part = db.query(models.SparePart).filter(models.SparePart.id == db_movement.part_id).first()
    
    if db_part:
        # 3. İşlemi tersine çevir (Geri alma mantığı)
        if db_movement.movement_type == "OUT":
            # Satış iptal edildi, mallar depoya geri döndü -> Stoğu artır
            db_part.stock_quantity += db_movement.quantity
        elif db_movement.movement_type == "IN":
            # Mal alımı iptal edildi -> Stoğu azalt
            db_part.stock_quantity -= db_movement.quantity

    # 4. Hareketi kalıcı olarak sil ve değişiklikleri veritabanına kaydet
    db.delete(db_movement)
    db.commit()
    
    return {"message": f"Stok hareketi (ID: {movement_id}) silindi ve stok miktarı başarıyla geri alındı."}

# Modeli uygulama başlarken bir kere hafızaya alıyoruz (Her istekte baştan yüklememek için)
try:
    ml_model = joblib.load("sales_forecasting_xgboost.pkl")
except Exception as e:
    ml_model = None
    print("Uyarı: Model dosyası bulunamadı!")

@app.get("/api/predict/{part_id}")
def predict_next_month_sales(part_id: int, db: Session = Depends(get_db)):
    if ml_model is None:
        return {"error": "Model yüklenemedi."}

    # 1. İçinde bulunduğumuz ayı ve yılı bul (Şu an Temmuz 2026)
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    # Tahmin edeceğimiz ay (Önümüzdeki ay -> Ağustos)
    next_month = current_month + 1 if current_month < 12 else 1

    # 2. XGBoost bizden 'prev_month_sales' istiyordu. 
    # Gelecek ay için (Ağustos) önceki ay, içinde bulunduğumuz aydır (Temmuz).
    # Veritabanına gidip "Bu parçadan Temmuz ayında toplam kaç tane satılmış?" diye soruyoruz:
    current_month_sales = db.query(func.sum(models.StockMovement.quantity))\
        .filter(models.StockMovement.part_id == part_id)\
        .filter(models.StockMovement.movement_type == "OUT")\
        .filter(func.extract('year', models.StockMovement.movement_date) == current_year)\
        .filter(func.extract('month', models.StockMovement.movement_date) == current_month)\
        .scalar()

    # Eğer bu ay hiç satış olmadıysa 0 sayıyoruz
    current_month_sales = current_month_sales if current_month_sales else 0

    # 3. XGBoost'un beklediği formata (Pandas DataFrame) çeviriyoruz
    # DİKKAT: Kolon isimleri train_model.py'dekiyle BİREBİR aynı olmalı!
    input_data = pd.DataFrame([{
        'part_id': part_id,
        'month': next_month,
        'prev_month_sales': current_month_sales
    }])

    # 4. Ve Sihir Gerçekleşiyor! Model tahmini yapıyor.
    prediction = ml_model.predict(input_data)
    
    # Küsuratlı araba parçası satılamayacağı için (Örn: 14.3) sayıyı yuvarlıyoruz
    predicted_value = int(round(prediction[0]))
    if predicted_value < 0: predicted_value = 0 # Eksi satış olmaz

    return {
        "part_id": part_id,
        "next_month": next_month,
        "current_month_sales": current_month_sales,
        "predicted_sales": predicted_value
    }

@app.get("/api/sales-history/{part_id}")
def get_sales_history(part_id: int, db: Session = Depends(get_db)):
    # Veritabanına gidip bu parçanın geçmiş aylardaki toplam satışlarını çekiyoruz
    history = db.query(
        func.extract('year', models.StockMovement.movement_date).label('year'),
        func.extract('month', models.StockMovement.movement_date).label('month'),
        func.sum(models.StockMovement.quantity).label('total_sales')
    ).filter(models.StockMovement.part_id == part_id)\
     .filter(models.StockMovement.movement_type == "OUT")\
     .group_by('year', 'month')\
     .order_by('year', 'month').all()

    # Frontend'in (Chart.js) kolayca okuyabileceği bir JSON listesine çeviriyoruz
    # Örnek Çıktı: [{"year": 2025, "month": 1, "total_sales": 15}, ...]
    result = []
    for row in history:
        result.append({
            "year": int(row.year),
            "month": int(row.month),
            "total_sales": int(row.total_sales) if row.total_sales else 0
        })
        
    return result

@app.get("/api/parts")
def get_parts_list(db: Session = Depends(get_db)):
    # Sadece ID ve İsimleri çekiyoruz ki gereksiz veri yükü olmasın
    parts = db.query(models.SparePart.id, models.SparePart.name).order_by(models.SparePart.id).all()
    return [{"id": p.id, "name": p.name} for p in parts]