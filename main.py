from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse # HTML dosyamızı sunmak için eklendi
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine

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