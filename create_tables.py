from database import engine, Base
import models # Yazdığımız modelleri içeri aktarıyoruz ki SQLAlchemy onları görsün

# Bu sihirli kod, modelleri tarar ve PostgreSQL'de tabloları oluşturur
Base.metadata.create_all(bind=engine)
print("Tablolar PostgreSQL üzerinde başarıyla oluşturuldu!")