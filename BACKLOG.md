# Agent Reach UI Backlog

Bu backlog, Agent Reach icin yerel bir web arayuzu olusturmak uzere hazirlandi.
Stack: FastAPI + HTMX
Hedef: install, configure, doctor, setup, uninstall islemlerini UI uzerinden yonetmek.

## Epic 1 - Web API Temeli

### Story 1.1 - FastAPI iskeleti

- Priority: P0
- Estimate: 3 SP
- Tasks:

  - FastAPI app girisi olustur
  - / api ve / ui route ayrimini belirle
  - Web sunucusu icin script entrypoint ekle

- Acceptance Criteria:

  - Localde tek komutla UI ayaga kalkar
  - Ana sayfa acilir ve hata vermez

### Story 1.2 - Komut calistirma adaptor katmani

- Priority: P0
- Estimate: 5 SP
- Tasks:

  - allowlist tabanli komut cagirimi (install/configure/doctor/uninstall)
  - stdout/stderr ve exit code yakalama
  - PATH ve Python executable uyum kontrolleri

- Acceptance Criteria:

  - UI uzerinden tetiklenen komutlar ayni CLI davranisini verir
  - Hata durumunda guvenli mesaj doner

## Epic 2 - Doctor Dashboard

### Story 2.1 - Kanal saglik ekrani

- Priority: P0
- Estimate: 5 SP
- Tasks:

  - doctor sonucunu kart bazli goster
  - tier bazli grupla (0/1/2)
  - durum rozetleri (ok/warn/off/error)

- Acceptance Criteria:

  - doctor bilgisi UI yuklendiginde gorunur
  - Refresh ile yeni durum aninda gorulur

### Story 2.2 - JSON API

- Priority: P1
- Estimate: 2 SP
- Tasks:

  - /api/doctor endpoint ekle
  - JSON kontratini dokumante et

- Acceptance Criteria:

  - Endpoint kanal sozlugunu dondurur

## Epic 3 - Install ve Configure

### Story 3.1 - Install paneli

- Priority: P0
- Estimate: 5 SP
- Tasks:

  - env/safe/dry-run/proxy alanlari
  - install komutunu backend uzerinden calistir
  - sonucu pre blokta goster

- Acceptance Criteria:

  - Formdan install tetiklenir
  - Exit code ve log ekranda gorunur

### Story 3.2 - Configure paneli

- Priority: P0
- Estimate: 5 SP
- Tasks:

  - key/value configure formu
  - browser tabanli cookie import formu
  - sonuc ve hata mesajlarinin guvenli gosterimi

- Acceptance Criteria:

  - proxy/github-token/groq-key/twitter-cookies gibi keyler UI'den girilir
  - browser import tetiklenebilir

## Epic 4 - Setup Wizard

### Story 4.1 - Guided setup

- Priority: P1
- Estimate: 5 SP
- Tasks:

  - Exa enable toggle
  - github token/reddit proxy/groq key alanlari
  - Apply sonrasi optional doctor refresh

- Acceptance Criteria:

  - Setup formu ile temel konfigurasyon uygulanir
  - Exa mevcutsa tekrar eklemeye calismaz

## Epic 5 - Uninstall Guvenligi

### Story 5.1 - Guvenli kaldirma paneli

- Priority: P1
- Estimate: 3 SP
- Tasks:

  - dry-run ve keep-config secenekleri
  - tek butonla uninstall cagirimi
  - onay notu ve sonuc logu

- Acceptance Criteria:

  - Dry-run beklenen ciktiyi verir
  - Keep-config secenegi config klasorunu korur

## Epic 6 - Frontend UX ve Tasarim

### Story 6.1 - Distinctive UI

- Priority: P1
- Estimate: 3 SP
- Tasks:

  - ifade guclu tipografi
  - cesur ama okunakli renk sistemi
  - responsive grid + mobil uyum
  - yuklenis ve kart animasyonlari

- Acceptance Criteria:

  - Masaustu ve mobilde duzgun gorunum
  - Orta hizli aglarda akici deneyim

## Epic 7 - Guvenlik ve Gozlenebilirlik

### Story 7.1 - Hassas veri koruma

- Priority: P0
- Estimate: 5 SP
- Tasks:

  - credential alanlarini masked input yap
  - loglarda token/cookie redaction
  - allowlist disi komutlara 400 don

- Acceptance Criteria:

  - UI ciktilarinda ham token gorunmez
  - disaridan keyfi komut calistirilamaz

### Story 7.2 - Operasyonel gozlem

- Priority: P2
- Estimate: 3 SP
- Tasks:

  - son calisan komut ozeti
  - cagrilarda sure olcumu
  - hata eventlerini normalize et

- Acceptance Criteria:

  - Her aksiyondan sonra sure ve exit code gorulur

## Epic 8 - Test ve Kalite

### Story 8.1 - API testleri

- Priority: P1
- Estimate: 5 SP
- Tasks:

  - doctor endpoint testleri
  - allowlist ve hata kodu testleri
  - setup endpoint davranis testleri

- Acceptance Criteria:

  - Kritik endpointler icin test kapsamı mevcut

### Story 8.2 - UI smoke test

- Priority: P2
- Estimate: 3 SP
- Tasks:

  - ana sayfa render testi
  - form endpoint smoke testleri

- Acceptance Criteria:

  - CI ortaminda temel UI smoke testleri yesil

## Cikis Kriterleri (MVP)

- [ ] UI localde calisir
- [ ] Doctor dashboard aktif
- [ ] Install formu aktif
- [ ] Configure formu aktif
- [ ] Setup wizard aktif
- [ ] Uninstall dry-run aktif
- [ ] Kritik endpoint testleri mevcut
