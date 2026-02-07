# WellNest - AI-Powered Health & Calorie Tracking

> **Yapay Zeka Destekli Kapsamli Saglik ve Kalori Takip Uygulamasi**
> Fotoğraftan otomatik besin tanıma, kişiselleştirilmiş kalori hesaplama ve profesyonel sporcu metrikleri.

---

## Mimari Genel Bakış

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WellNest Architecture                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────────┐ │
│  │   Mobile App     │     │   Web Dashboard   │     │  Wearable Devices   │ │
│  │  (React Native)  │     │     (React)       │     │ (HealthKit/Fit)     │ │
│  └────────┬─────────┘     └────────┬─────────┘     └──────────┬───────────┘ │
│           │                        │                          │             │
│           └────────────────────────┼──────────────────────────┘             │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         API Gateway (FastAPI)                           ││
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────────────┐ ││
│  │  │    Auth     │ │   Health    │ │  AI Vision  │ │   Integrations    │ ││
│  │  │   Module    │ │   Module    │ │   Module    │ │     Module        │ ││
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └───────────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                    │                                        │
│           ┌────────────────────────┼────────────────────────┐               │
│           │                        │                        │               │
│           ▼                        ▼                        ▼               │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────────┐   │
│  │   PostgreSQL    │     │  Claude Vision  │     │   External APIs     │   │
│  │   (Supabase)    │     │      API        │     │ (HealthKit/Fit)     │   │
│  └─────────────────┘     └─────────────────┘     └─────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Ana Ozellikler

### Genel Kullanıcılar İçin
- **Fotoğraftan Kalori Hesaplama**: Claude Vision API ile yemek fotoğrafını çek, otomatik besin ve kalori tanıma
- **Kişiselleştirilmiş Kalori Bütçesi**: Mifflin-St Jeor formülü ile BMR hesaplama
- **Basit Kalori Barı**: Günlük hedef vs alınan kalori görsel takibi
- **Su Takibi**: Günlük su tüketimi kaydı
- **Kilo Takibi**: İnteraktif grafiklerle kilo değişimi analizi

### Profesyonel Sporcular İçin
- **Detaylı Makro Dağılımı**: Protein, Karbonhidrat, Yağ gram ve yüzde bazında takip
- **Hedef Makro Hesaplama**: Aktivite seviyesi ve hedefe göre otomatik makro önerileri
- **Recovery (Toparlanma) Skoru**: Uyku ve nabız verisiyle toparlanma analizi
- **Performans Metrikleri**: Antrenman yoğunluğu ve ilerleme takibi
- **HealthKit/Google Fit Entegrasyonu**: Otomatik veri senkronizasyonu

---

## Teknoloji Yığını

### Backend
| Teknoloji | Kullanım |
|-----------|----------|
| **FastAPI** | Modern, async Python web framework |
| **SQLAlchemy** | ORM ve veritabanı işlemleri |
| **PostgreSQL/Supabase** | Production veritabanı |
| **SQLite** | Development veritabanı |
| **Pydantic v2** | Veri validasyonu |
| **Python-jose** | JWT token yönetimi |
| **Passlib + BCrypt** | Şifre hashleme |
| **Anthropic SDK** | Claude Vision API entegrasyonu |

### Frontend (Web)
| Teknoloji | Kullanım |
|-----------|----------|
| **React 19** | UI framework |
| **Vite** | Build tool |
| **Tailwind CSS v3** | Utility-first styling |
| **Framer Motion** | Animasyonlar |
| **Recharts** | Veri görselleştirme |
| **React Router v7** | Client-side routing |
| **Axios** | HTTP client |

### Mobile (React Native/Expo)
| Teknoloji | Kullanım |
|-----------|----------|
| **Expo SDK 50+** | Cross-platform framework |
| **Expo Camera** | Fotoğraf çekme |
| **Expo Image Picker** | Galeri erişimi |
| **AsyncStorage** | Offline veri saklama |
| **React Navigation** | Mobil navigasyon |

### AI & Entegrasyonlar
| Teknoloji | Kullanım |
|-----------|----------|
| **Claude 3.5 Sonnet Vision** | Yemek fotoğrafı analizi |
| **Apple HealthKit** | iOS sağlık verileri |
| **Google Fit** | Android sağlık verileri |

---

## Veritabanı Şeması

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATABASE SCHEMA                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐         ┌─────────────────────┐                        │
│  │     users       │         │    user_profiles    │                        │
│  ├─────────────────┤         ├─────────────────────┤                        │
│  │ id (PK)         │◄───────►│ id (PK)             │                        │
│  │ email           │    1:1  │ user_id (FK)        │                        │
│  │ password_hash   │         │ height              │                        │
│  │ created_at      │         │ current_weight      │                        │
│  │ is_athlete      │         │ target_weight       │                        │
│  └────────┬────────┘         │ birth_date          │                        │
│           │                  │ gender              │                        │
│           │                  │ activity_level      │                        │
│           │                  │ goal_type           │                        │
│           │                  │ daily_calorie_goal  │                        │
│           │                  │ protein_goal        │                        │
│           │                  │ carbs_goal          │                        │
│           │                  │ fat_goal            │                        │
│           │                  │ onboarding_complete │                        │
│           │                  └─────────────────────┘                        │
│           │                                                                  │
│           │ 1:N              ┌─────────────────────┐                        │
│           ├─────────────────►│    food_logs        │                        │
│           │                  ├─────────────────────┤                        │
│           │                  │ id (PK)             │                        │
│           │                  │ user_id (FK)        │                        │
│           │                  │ food_name           │                        │
│           │                  │ calories            │                        │
│           │                  │ protein             │                        │
│           │                  │ carbs               │                        │
│           │                  │ fat                 │                        │
│           │                  │ fiber               │                        │
│           │                  │ serving_size        │                        │
│           │                  │ meal_type           │                        │
│           │                  │ image_url           │                        │
│           │                  │ ai_analyzed         │                        │
│           │                  │ confidence_score    │                        │
│           │                  │ logged_at           │                        │
│           │                  └─────────────────────┘                        │
│           │                                                                  │
│           │ 1:N              ┌─────────────────────┐                        │
│           ├─────────────────►│   weight_logs       │                        │
│           │                  ├─────────────────────┤                        │
│           │                  │ id (PK)             │                        │
│           │                  │ user_id (FK)        │                        │
│           │                  │ weight              │                        │
│           │                  │ body_fat_pct        │                        │
│           │                  │ muscle_mass         │                        │
│           │                  │ logged_at           │                        │
│           │                  └─────────────────────┘                        │
│           │                                                                  │
│           │ 1:N              ┌─────────────────────┐                        │
│           ├─────────────────►│   water_logs        │                        │
│           │                  ├─────────────────────┤                        │
│           │                  │ id (PK)             │                        │
│           │                  │ user_id (FK)        │                        │
│           │                  │ amount_ml           │                        │
│           │                  │ logged_at           │                        │
│           │                  └─────────────────────┘                        │
│           │                                                                  │
│           │ 1:N              ┌─────────────────────┐                        │
│           ├─────────────────►│   daily_stats       │                        │
│           │                  ├─────────────────────┤                        │
│           │                  │ id (PK)             │                        │
│           │                  │ user_id (FK)        │                        │
│           │                  │ date                │                        │
│           │                  │ total_calories      │                        │
│           │                  │ total_protein       │                        │
│           │                  │ total_carbs         │                        │
│           │                  │ total_fat           │                        │
│           │                  │ total_water_ml      │                        │
│           │                  │ steps               │                        │
│           │                  │ active_calories     │                        │
│           │                  │ sleep_hours         │                        │
│           │                  │ avg_heart_rate      │                        │
│           │                  │ recovery_score      │                        │
│           │                  └─────────────────────┘                        │
│           │                                                                  │
│           │ 1:N (Athletes)   ┌─────────────────────┐                        │
│           └─────────────────►│  athlete_metrics    │                        │
│                              ├─────────────────────┤                        │
│                              │ id (PK)             │                        │
│                              │ user_id (FK)        │                        │
│                              │ date                │                        │
│                              │ training_load       │                        │
│                              │ hrv_score           │                        │
│                              │ resting_hr          │                        │
│                              │ vo2_max_estimate    │                        │
│                              │ fatigue_level       │                        │
│                              │ readiness_score     │                        │
│                              │ notes               │                        │
│                              └─────────────────────┘                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Kurulum

### Gereksinimler
- Python 3.10+
- Node.js 18+
- Anthropic API Key (Claude Vision için)

### 1. Backend Kurulumu

```bash
cd wellnest-backend

# Virtual environment oluştur
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Environment değişkenlerini ayarla
cp .env.example .env
# .env dosyasını düzenle:
# - SECRET_KEY=your-secret-key
# - ANTHROPIC_API_KEY=your-anthropic-api-key
# - DATABASE_URL=sqlite:///./wellnest.db

# Veritabanını başlat
python -c "from app.db import init_db; init_db()"

# Sunucuyu başlat
uvicorn app.main:app --reload --host 0.0.0.0 --port 8004
```

### 2. Frontend Kurulumu (Web)

```bash
cd wellnest-frontend

# Bağımlılıkları yükle
npm install

# Development sunucusunu başlat
npm run dev
```

### 3. Mobile Kurulumu (Expo)

```bash
cd wellnest-mobile

# Bağımlılıkları yükle
npm install

# Expo'yu başlat
npx expo start
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/auth/register` | Yeni kullanıcı kaydı |
| POST | `/auth/token` | Giriş ve JWT token al |

### User Profile
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/users/me` | Mevcut kullanıcı bilgisi |
| PUT | `/users/profile` | Profil güncelleme |
| POST | `/users/onboarding` | Onboarding tamamlama |

### Health Tracking
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/health/food` | Yemek kaydı |
| GET | `/health/food` | Yemek geçmişi |
| POST | `/health/food/analyze` | AI ile yemek analizi |
| POST | `/health/weight` | Kilo kaydı |
| GET | `/health/weight` | Kilo geçmişi |
| POST | `/health/water` | Su kaydı |
| GET | `/health/dashboard` | Günlük özet |

### Athlete Metrics
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/athlete/metrics` | Sporcu metrikleri kaydı |
| GET | `/athlete/recovery` | Toparlanma skoru |
| GET | `/athlete/performance` | Performans analizi |

### Integrations
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/integrations/healthkit/sync` | HealthKit senkronizasyonu |
| POST | `/integrations/googlefit/sync` | Google Fit senkronizasyonu |

---

## Kalori Hesaplama (Mifflin-St Jeor)

### BMR (Bazal Metabolizma Hızı)

**Erkek:**
```
BMR = (10 × kilo[kg]) + (6.25 × boy[cm]) - (5 × yaş) + 5
```

**Kadın:**
```
BMR = (10 × kilo[kg]) + (6.25 × boy[cm]) - (5 × yaş) - 161
```

### TDEE (Günlük Toplam Enerji Harcaması)

| Aktivite Seviyesi | Çarpan |
|-------------------|--------|
| Sedanter (hareketsiz) | BMR × 1.2 |
| Hafif aktif (1-3 gün/hafta) | BMR × 1.375 |
| Orta aktif (3-5 gün/hafta) | BMR × 1.55 |
| Çok aktif (6-7 gün/hafta) | BMR × 1.725 |
| Ekstra aktif (profesyonel sporcu) | BMR × 1.9 |

### Hedef Bazlı Kalori Ayarlaması

| Hedef | Ayarlama |
|-------|----------|
| Kilo verme | TDEE - 500 kcal |
| Kilo koruma | TDEE |
| Kas yapma | TDEE + 300 kcal |

---

## Recovery (Toparlanma) Skoru Algoritması

```python
def calculate_recovery_score(sleep_hours, resting_hr, avg_hr_baseline, hrv=None):
    """
    0-100 arası toparlanma skoru hesaplar.

    Faktörler:
    - Uyku kalitesi (40%)
    - Kalp atış hızı dinlenme (30%)
    - HRV (varsa) (30%)
    """

    # Uyku skoru (optimal: 7-9 saat)
    if 7 <= sleep_hours <= 9:
        sleep_score = 100
    elif sleep_hours < 7:
        sleep_score = max(0, sleep_hours / 7 * 100)
    else:
        sleep_score = max(0, 100 - (sleep_hours - 9) * 10)

    # Kalp atış skoru (baseline'a yakınlık)
    hr_diff = abs(resting_hr - avg_hr_baseline)
    hr_score = max(0, 100 - hr_diff * 5)

    # HRV skoru (varsa)
    if hrv:
        hrv_score = min(100, hrv * 1.5)
        return (sleep_score * 0.35) + (hr_score * 0.3) + (hrv_score * 0.35)

    return (sleep_score * 0.55) + (hr_score * 0.45)
```

---

## Proje Yapısı

```
WellNest/
├── README.md
├── docker-compose.yml
│
├── wellnest-backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI uygulama
│   │   ├── db.py                   # Veritabanı bağlantısı
│   │   ├── models.py               # SQLAlchemy modelleri
│   │   ├── schemas.py              # Pydantic şemaları
│   │   ├── crud.py                 # CRUD operasyonları
│   │   │
│   │   ├── api/
│   │   │   ├── deps.py             # Dependency injection
│   │   │   └── v1/
│   │   │       ├── auth.py         # Authentication
│   │   │       ├── health.py       # Sağlık takibi
│   │   │       ├── user.py         # Kullanıcı işlemleri
│   │   │       └── athlete.py      # Sporcu metrikleri
│   │   │
│   │   ├── core/
│   │   │   ├── config.py           # Konfigürasyon
│   │   │   ├── security.py         # JWT ve şifreleme
│   │   │   └── calculations.py     # Kalori hesaplamaları
│   │   │
│   │   └── services/
│   │       ├── ai_vision.py        # Claude Vision entegrasyonu
│   │       ├── healthkit.py        # Apple HealthKit
│   │       └── googlefit.py        # Google Fit
│   │
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── wellnest-frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Onboarding.jsx
│   │   │   ├── Camera.jsx
│   │   │   └── Profile.jsx
│   │   │
│   │   ├── components/
│   │   │   ├── Layout.jsx
│   │   │   ├── FoodLogger.jsx
│   │   │   ├── WeightChart.jsx
│   │   │   ├── MacroChart.jsx
│   │   │   ├── CalorieBar.jsx
│   │   │   ├── WaterTracker.jsx
│   │   │   └── RecoveryScore.jsx
│   │   │
│   │   ├── context/
│   │   │   ├── AuthContext.jsx
│   │   │   └── ThemeContext.jsx
│   │   │
│   │   └── api.js
│   │
│   ├── package.json
│   └── vite.config.js
│
└── wellnest-mobile/                # (Opsiyonel - React Native)
    ├── App.js
    ├── src/
    │   ├── screens/
    │   ├── components/
    │   └── services/
    ├── app.json
    └── package.json
```

---

## Güvenlik

- **HIPAA Uyumlu Yaklaşım**: Sağlık verileri şifreli saklanır
- **JWT Authentication**: Güvenli token tabanlı kimlik doğrulama
- **BCrypt Hashing**: Şifreler güvenli hash algoritması ile saklanır
- **HTTPS Only**: Production'da TLS zorunlu
- **Rate Limiting**: API istekleri sınırlandırılmış
- **Input Validation**: Pydantic ile veri doğrulama

---

## Edge Cases & Fallbacks

### Fotoğraf Analizi Başarısız
```
- AI güven skoru < 0.7 ise manuel giriş öner
- "Besin tanınamadı, lütfen manuel girin" mesajı göster
- Kullanıcıya benzer besinler öner
```

### Offline Mode
```
- AsyncStorage/localStorage ile yerel veri saklama
- İnternet bağlantısı geldiğinde otomatik senkronizasyon
- Conflict resolution: son değişiklik öncelikli
```

### Sağlık Entegrasyonu İzni Reddedildi
```
- Manuel veri girişi seçeneği sun
- İzin talebinin faydalarını açıkla
- Uygulama tam işlevsel kalır
```

---

## Lisans

MIT License - Detaylar için LICENSE dosyasına bakın.
