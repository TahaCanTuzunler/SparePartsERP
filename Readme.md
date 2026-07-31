# AI-Powered Spare Parts ERP System

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.139-009688?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)
![XGBoost](https://img.shields.io/badge/Machine_Learning-XGBoost-FF9900?style=for-the-badge)


A modern, containerized, and AI-powered Automotive Spare Parts ERP project. In addition to inventory tracking, the system analyzes historical sales (OUT) data to forecast future demand using machine learning (XGBoost).

## Key Features
* **End-to-End CRUD:** Spare parts and supplier management.
* **Stock Movement Tracking:** Dynamic stock calculation via IN and OUT operations.
* **AI Integration:** Stock demand forecasting using the XGBoost model.
* **Complete Isolation:** Hardware-independent architecture that spins up with a single command using Docker and Docker Compose.
* **RESTful API:** Endpoints built with FastAPI and automatically documented via Swagger UI.

## Technologies Used
* **Backend:** Python, FastAPI, SQLAlchemy, Pydantic
* **Database:** PostgreSQL (psycopg2)
* **Machine Learning:** XGBoost, Scikit-Learn, Pandas, Joblib
* **Frontend:** HTML, Vanilla JavaScript, Fetch API
* **DevOps:** Docker, Docker Compose

## Installation & Running

The project is fully Dockerized. You only need to have Docker installed on your machine.

1. Clone the project:
```bash
git clone https://github.com/TahaCanTuzunler/SparePartsERP.git
cd spare-parts-erp
```

Build and run the containers:

`docker-compose up --build`

Visit the following addresses in your browser:

Dashboard: http://localhost:8000

API Documentation (Swagger): http://localhost:8000/docs

When you set up the database from scratch, it will be empty. You must enter data to test the model and view the graphs.

---

## Türkçe Versiyon

Modern, container mimarisine sahip ve yapay zeka destekli bir Otomotiv Yedek Parça ERP projesidir. Sistem, envanter takibinin yanı sıra geçmiş satış (OUT) verilerini analiz ederek makine öğrenmesi (XGBoost) ile gelecek talep tahminlemesi yapmaktadır.

## Temel Özellikler
* **Uçtan Uca CRUD:** Yedek parça ve tedarikçi yönetimi.
* **Stok Hareketi Takibi:** IN (Giriş) ve OUT (Çıkış) işlemleriyle dinamik stok hesaplama.
* **Yapay Zeka Entegrasyonu:** XGBoost modeli ile stok talep tahminlemesi.
* **Tam İzolasyon:** Docker ve Docker Compose ile tek tıkla ayağa kalkan, donanımdan bağımsız mimari.
* **RESTful API:** FastAPI ile yazılmış, Swagger UI ile otomatik dokümante edilmiş endpoint'ler.

##  Kullanılan Teknolojiler
* **Backend:** Python, FastAPI, SQLAlchemy, Pydantic
* **Veritabanı:** PostgreSQL (psycopg2)
* **Makine Öğrenmesi:** XGBoost, Scikit-Learn, Pandas, Joblib
* **Frontend:** HTML, Vanilla JavaScript, Fetch API
* **DevOps:** Docker, Docker Compose

##  Kurulum ve Çalıştırma

Proje tamamen Dockerize edilmiştir. Bilgisayarınızda sadece Docker yüklü olması yeterlidir.

1.Projeyi klonlayın:

```bash
git clone https://github.com/TahaCanTuzunler/SparePartsERP.git
cd spare-parts-erp
```

2.Konteynerleri inşa edin ve ayağa kaldırın:


`docker-compose up --build`
Tarayıcınızda şu adreslere gidin:

Arayüz (Dashboard): http://localhost:8000

API Dokümantasyonu (Swagger): http://localhost:8000/docs

Sistemi sıfırdan kurduğunuzda veritabanı boş gelecektir. Modeli test etmek ve grafikleri görebilmek için veri eklemeniz gerekmektedir.





