from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

# Tedarikçiler Tablosu
class Supplier(Base):
    __tablename__ = "suppliers" 

    id = Column(Integer, primary_key=True, index=True) 
    name = Column(String, index=True)                  
    contact_email = Column(String, unique=True)        
    phone = Column(String)                             

    parts = relationship("SparePart", back_populates="supplier")

# Yedek Parçalar Tablosu
class SparePart(Base):
    __tablename__ = "spare_parts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)                  
    description = Column(Text)                         
    price = Column(Float)                              
    stock_quantity = Column(Integer, default=0)        
    
    supplier_id = Column(Integer, ForeignKey("suppliers.id")) 

    supplier = relationship("Supplier", back_populates="parts")
    
    # YENİ: Bir parçanın birden fazla stok hareketi (GİRİŞ/ÇIKIŞ) olabilir
    movements = relationship("StockMovement", back_populates="part")


# YENİ EKLENEN TABLO: Stok Hareketleri Tablosu
class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    
    # Hangi parça için hareket yapılıyor? (Dış Anahtar)
    part_id = Column(Integer, ForeignKey("spare_parts.id"))
    
    # Hareket tipi: "IN" (Depoya Giriş) veya "OUT" (Depodan Çıkış)
    movement_type = Column(String) 
    
    # Kaç adet girdi veya çıktı?
    quantity = Column(Integer)
    
    # İşlem ne zaman yapıldı? (Otomatik olarak o anın tarih ve saatini alır)
    movement_date = Column(DateTime, default=datetime.datetime.utcnow)

    # Bu hareketin ait olduğu parçaya Python'dan kolayca ulaşmak için
    part = relationship("SparePart", back_populates="movements")