#  Fraud Shield: Real-Time Transaction Monitoring & MCP Platform

Bu proje, e-ticaret platformlarında gerçekleşen ödeme ve işlem verilerini toplayan, asenkron olarak analiz eden, şüpheli işlemleri (fraud) gerçek zamanlı tespit eden ve yapay zeka ajanları için Model Context Protocol (MCP) üzerinden veri sunan uçtan uca bir platformdur.

##  Proje Amacı ve Kapsamı
Fraud Shield, yüksek hacimli işlem verilerini düşük gecikme süresiyle işlemek üzere tasarlanmıştır. Temel amacı; kullanıcı bazlı davranış kurallarını (Hız, Tutar, Konum) denetleyerek anormallikleri tespit etmek ve bu verileri hem bir operatör panelinde görselleştirmek hem de LLM tabanlı yapay zeka ajanlarının sorgulayabileceği standart bir protokol (MCP) üzerinden dışa açmaktır.

##  Sistem Mimarisi ve Komponentler
Sistem **Mikroservis Mimarisi** prensiplerine uygun olarak 3 ana servis ve 3 altyapı bileşeninden oluşur:

1.  **API Service (FastAPI):** Dış dünyadan gelen işlem verilerini (REST) karşılar ve validasyon sonrası RabbitMQ kuyruğuna iletir.
2.  **Worker Service (Python):** Kuyruktaki verileri tüketir. Redis kullanarak state yönetimi yapar ve anomali kurallarını (Hız, Tutar, Konum) denetler.
3.  **MCP Server (Python/stdio):** Yapay zeka ajanları için `get_recent_frauds` ve `check_user_status` araçlarını sunan Model Context Protocol sunucusudur.
4.  **Frontend (React/Vite):** Canlı veri akışını, anomali grafiklerini ve uyarı panelini barındıran responsive dashboard.
5.  **Altyapı:** RabbitMQ (Mesaj Kuyruğu), Redis (In-memory Cache), PostgreSQL (Kalıcı Veri).

##  Teknoloji Seçimleri ve Gerekçeleri
- **FastAPI:** Asenkron yapısı ve otomatik Swagger desteği nedeniyle yüksek performanslı API trafiği için tercih edilmiştir.
- **RabbitMQ:** API ve Worker arasındaki iletişimi gevşek bağlı (loosely coupled) hale getirmek ve veri kaybını önlemek için asenkron kuyruklama sistemi olarak kullanılmıştır.
- **Redis:** Anomali tespitindeki "son 1 dakika" veya "son konum" gibi anlık durum kontrolleri (state management) için disk I/O gecikmesi yaşamamak adına in-memory tercih edilmiştir.
- **MCP (Model Context Protocol):** Modern yapay zeka ajanlarının sistem verilerine güvenli ve standart bir yolla erişebilmesi sağlanmıştır.

##  Kurulum Adımları
Tüm sistem `docker-compose` ile tek komutla ayağa kaldırılabilir.

**Gereksinimler:** Docker ve Docker Compose.

1.  Proje dizininde sistemi başlatın:
    ```bash
    docker compose up --build -d
    ```
2.  Tüm konteynerlerin ayağa kalktığından emin olun: `docker ps`

## 📖 Kullanım Rehberi ve Endpointler
- **Frontend Dashboard:** [http://localhost:5173](http://localhost:5173)
- **API Swagger Dokümantasyonu:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **RabbitMQ Yönetim Paneli:** [http://localhost:15672](http://localhost:15672) (guest/guest)

### MCP Test Yöntemi
MCP Server stdio üzerinden haberleşir. Test etmek için:
1.  `npx @modelcontextprotocol/inspector docker exec -i fraud_mcp python server.py` komutu kullanılabilir veya projedeki MCP servisi doğrudan LLM client'larına tanıtılabilir.

##  Veri Besleme ve Test Scriptleri
Sistemi beslemek için `scripts/` dizinindeki Bash scriptleri kullanılabilir:

**Manuel Giriş:**
```bash
./scripts/manual-input.sh <user_id> <amount> <location>
```

**Otomatik Test (Anomali Simülasyonu):**
```bash
./scripts/auto-test.sh --duration=60 --rate=2 --anomaly-chance=30
```

##  Anomali Tespiti Kriterleri
Bir işlem, aşağıdaki kriterlerden **en az ikisi** ihlal edildiğinde "Şüpheli" (FRAUD) olarak işaretlenir:
1.  **Hız Kontrolü:** Kullanıcının son 1 dakika içinde 5'ten fazla işlem yapması.
2.  **Tutar Kontrolü:** İşlem tutarının, kullanıcının geçmiş ortalamasının 3 katından fazla olması.
3.  **Konum Kontrolü:** Birbirini izleyen iki işlem arasındaki sürenin, lokasyonlar arası mesafeyi katetmek için fiziksel olarak imkansız olması (5 dk içinde şehir değişikliği vb.).

##  Sorun Giderme (Troubleshooting)
- **Bağlantı Hataları:** Konteynerlerin `healthy` durumda olduğunu `docker ps` ile kontrol edin.
- **Port Çakışması:** Eğer 5433, 6379 veya 5672 portları doluysa `docker-compose.yml` üzerinden port eşleşmelerini güncelleyin.
- **Frontend Boş Sayfa:** Browser önbelleğini temizleyin ve React derlemesinin tamamlanması için 10-15 saniye bekleyin.
