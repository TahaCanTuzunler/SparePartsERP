import pandas as pd
from database import engine
from xgboost import XGBRegressor
import joblib

print("Veritabanından geçmiş satış verileri çekiliyor...")

# 1. Veriyi Çekme
query = """
SELECT part_id, movement_date, quantity
FROM stock_movements
WHERE movement_type = 'OUT'
"""
df = pd.read_sql(query, engine)

print("Kaggle Stili Feature Engineering (Lag Features) yapılıyor...")

# 2. Veri Hazırlama
df['movement_date'] = pd.to_datetime(df['movement_date'])
df['year'] = df['movement_date'].dt.year
df['month'] = df['movement_date'].dt.month

# Aylık satışları grupluyoruz
monthly_sales = df.groupby(['part_id', 'year', 'month'])['quantity'].sum().reset_index()

# Zaman hesaplamalarının doğru olması için veriyi tarihe göre sıralıyoruz
monthly_sales = monthly_sales.sort_values(by=['part_id', 'year', 'month'])

# EN KRİTİK ADIM: Bir önceki ayın satış rakamını (Lag Feature) yeni bir kolon olarak ekliyoruz
monthly_sales['prev_month_sales'] = monthly_sales.groupby('part_id')['quantity'].shift(1)

# İlk ayların (geçmişi olmadığı için) NaN dönen değerlerini 0 ile dolduruyoruz
monthly_sales.fillna(0, inplace=True)

# 3. Bağımlı (y) ve Bağımsız (X) Değişkenleri Ayırma
X = monthly_sales[['part_id', 'month', 'prev_month_sales']]
y = monthly_sales['quantity']

print("XGBoost Modeli eğitiliyor...")

# 4. Modeli Eğitme (XGBoost)
model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
model.fit(X, y)

# 5. Modeli Kaydetme
joblib.dump(model, "sales_forecasting_xgboost.pkl")

print("BAŞARILI! Model 'sales_forecasting_xgboost.pkl' adıyla kaydedildi.")