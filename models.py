from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

# Tedarikçiler Tablosu
class Supplier(Base):
    __tablename__ = "suppliers" # Veritabanındaki tablonun adı

    id = Column(Integer, primary_key=True, index=True) # Her kaydın benzersiz kimliği (1, 2, 3...)
    name = Column(String, index=True)                  # Firma Adı
    contact_email = Column(String, unique=True)        # İletişim E-postası (unique: aynı e-posta 2 kez eklenemez)
    phone = Column(String)                             # Telefon Numarası

    # İlişki: Bir tedarikçinin birden fazla parçası olabilir. (One-to-Many)
    # Bu özellik veritabanında sütun oluşturmaz, Python'da kod yazarken bize kolaylık sağlar.
    parts = relationship("SparePart", back_populates="supplier")


# Yedek Parçalar Tablosu
class SparePart(Base):
    __tablename__ = "spare_parts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)                  # Parça Adı (Örn: Fren Balatası)
    description = Column(Text)                         # Parça Açıklaması
    price = Column(Float)                              # Fiyatı (Ondalıklı sayı)
    stock_quantity = Column(Integer, default=0)        # Stoktaki adet (Varsayılan 0)
    
    # Foreign Key (Dış Anahtar): Bu parçanın hangi tedarikçiye ait olduğunu tutar
    supplier_id = Column(Integer, ForeignKey("suppliers.id")) 

    # İlişki: Bu parçanın sahibi olan tedarikçiye Python üzerinden kolayca erişmek için
    supplier = relationship("Supplier", back_populates="parts")