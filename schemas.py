from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

from typing import Optional # Update özelliği eklemek için Optional'ı import ediyoruz

# --- TEDARİKÇİ ŞEMALARI ---
class SupplierBase(BaseModel):
    name: str
    contact_email: EmailStr
    phone: str

class SupplierCreate(SupplierBase):
    pass

class SupplierResponse(SupplierBase):
    id: int

    class Config:
        from_attributes = True

# --- YEDEK PARÇA ŞEMALARI ---
class SparePartBase(BaseModel):
    name: str
    description: str
    price: float
    stock_quantity: int
    supplier_id: int

class SparePartCreate(SparePartBase):
    pass

class SparePartResponse(SparePartBase):
    id: int

class SparePartUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    supplier_id: Optional[int] = None

    class Config:
        from_attributes = True

# --- YENİ: STOK HAREKETİ ŞEMALARI ---

# Kullanıcıdan API'ye gelirken beklediğimiz veri yapısı
class StockMovementCreate(BaseModel):
    part_id: int
    movement_type: str # Sadece "IN" veya "OUT" olmasını bekliyoruz
    quantity: int

# API'den kullanıcıya (Swagger'a) dönerken göstereceğimiz yapı
class StockMovementResponse(BaseModel):
    id: int
    part_id: int
    movement_type: str
    quantity: int
    movement_date: datetime # Modeldeki tarihi de gösteriyoruz

    class Config:
        # SQLAlchemy objelerini Pydantic sözlüklerine çevirmesi için gerekli sihirli ayar
        from_attributes = True