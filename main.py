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