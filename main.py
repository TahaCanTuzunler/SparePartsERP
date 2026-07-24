from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine

# Veritabanı tablolarının oluşturulduğundan emin oluyoruz (Daha önce create_tables.py ile yapmıştık)
models.Base.metadata.create_all(bind=engine)

# FastAPI uygulamamızı başlatıyoruz
app = FastAPI(title="Spare Parts ERP API")

# Her API isteğinde veritabanına bağlanıp, işlem bitince bağlantıyı kapatan yardımcı fonksiyon
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Sitenin ana dizinine girildiğinde çalışacak basit bir karşılama mesajı
@app.get("/")
def read_root():
    return {"mesaj": "Spare Parts ERP Sistemine Hos Geldiniz!"}

# Yeni bir tedarikçi eklemek için POST isteği
@app.post("/suppliers/", response_model=schemas.SupplierResponse)
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):
    # Aynı e-posta adresiyle başka bir tedarikçi var mı kontrolü
    db_supplier = db.query(models.Supplier).filter(models.Supplier.contact_email == supplier.contact_email).first()
    if db_supplier:
        raise HTTPException(status_code=400, detail="Bu e-posta adresi zaten kayitli.")
    
    # SQLAlchemy modeline dönüştürüp veritabanına kaydediyoruz
    new_supplier = models.Supplier(**supplier.model_dump())
    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)
    return new_supplier

# Sistemdeki tüm tedarikçileri listelemek için GET isteği
@app.get("/suppliers/", response_model=list[schemas.SupplierResponse])
def read_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    suppliers = db.query(models.Supplier).offset(skip).limit(limit).all()
    return suppliers

# Yeni bir yedek parça eklemek için POST isteği
@app.post("/parts/", response_model=schemas.SparePartResponse)
def create_spare_part(part: schemas.SparePartCreate, db: Session = Depends(get_db)):
    # Parçanın ekleneceği tedarikçi veritabanında gerçekten var mı?
    db_supplier = db.query(models.Supplier).filter(models.Supplier.id == part.supplier_id).first()
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Tedarikci bulunamadi.")
        
    # Parçayı veritabanına kaydet
    new_part = models.SparePart(**part.model_dump())
    db.add(new_part)
    db.commit()
    db.refresh(new_part)
    return new_part

# Sistemdeki tüm yedek parçaları listelemek için GET isteği
@app.get("/parts/", response_model=list[schemas.SparePartResponse])
def read_parts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    parts = db.query(models.SparePart).offset(skip).limit(limit).all()
    return parts