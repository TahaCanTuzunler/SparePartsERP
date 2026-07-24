from pydantic import BaseModel, EmailStr
from typing import Optional

# Tedarikçi için temel şema (Hem veri alırken hem veri gönderirken ortak olan alanlar)
class SupplierBase(BaseModel):
    name: str
    contact_email: EmailStr  # Pydantic otomatik olarak email formatını (abc@xyz.com) kontrol edecek
    phone: Optional[str] = None

# Yeni tedarikçi eklerken (POST işlemi) kullanacağımız şema
class SupplierCreate(SupplierBase):
    pass

# Veritabanından kullanıcıya veri gönderirken (GET işlemi) kullanacağımız şema
class SupplierResponse(SupplierBase):
    id: int # Veritabanında otomatik oluşan ID'yi de dönmek istiyoruz

    # Bu ayar, SQLAlchemy modellerini (ORM) Pydantic şemalarına sorunsuz dönüştürmeyi sağlar
    class Config:
        from_attributes = True


# Yedek Parça için temel şema
class SparePartBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock_quantity: int = 0

# Yeni yedek parça eklerken kullanacağımız şema
class SparePartCreate(SparePartBase):
    supplier_id: int # Parçanın kime ait olduğunu belirtmek zorundayız

# Veritabanından kullanıcıya yedek parça verisi dönerken kullanılacak şema
class SparePartResponse(SparePartBase):
    id: int
    supplier_id: int

    class Config:
        from_attributes = True