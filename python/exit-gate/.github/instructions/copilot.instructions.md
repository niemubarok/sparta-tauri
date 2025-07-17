---
applyTo: '**/*.py'
---
fokus ke folder python-app/app abaikan lainnya,

ini adalah aplikasi exit-gate parkit untuk di jalankan di raspberry pi 3 dengan python versi 3.10.14,
berikut detail pin gpio yang digunakan:
- GPIO 24: untuk membuka gate


INPUT BUTTON (Aktif low)

- loop 1 = gpio 18
- loop 2 = gpio 27


output relay (aktif high)

- Trigger 1 = gpio 24
- Trigger 2 = gpio 23

Output LED indikator (aktif high)
- LED live = gpio 25