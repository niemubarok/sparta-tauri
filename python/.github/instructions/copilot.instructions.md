---
applyTo: '**'
---
aplikasi terdiri dari exit gate dan entry-gate

full manless

full python 
aplikasi harus sangat ringan karena akan dijalankan di raspi
bisa simulasi di desktop

# stack
- websocket untuk komunikasi antara server dan raspi
- fast-alpr untuk deteksi plat nomor (https://github.com/ankandrew/fast-alpr)
- gpio untuk mengontrol palang
- database couchdb untuk menyimpan data transaksi dan gambar dari cctv sebagai attachment 
- cctv untuk mengambil gambar kendaraan

# cctv
- cctv terhubung ke raspi melalui lan
- cctv harus bisa mengambil gambar full kendaraan
- contoh url snapshot cctv: http://<username>:<password>@<ip_address>:<port>/snapshot
- cctv harus bisa diakses melalui http untuk mengambil snapshot

# gpio
- gpio digunakan untuk mengontrol palang
- pastikan gpio sudah terpasang dan terkonfigurasi dengan benar di raspi
- gunakan library RPi.GPIO untuk mengontrol gpio di raspi
- pastikan gpio sudah diatur untuk mengirim sinyal high untuk membuka palang dan low untuk menutup palang
- pin :
    - trigger gpio: pin 18 (bisa diganti sesuai kebutuhan)
    - loop1 gpio: pin 23 (bisa diganti sesuai kebutuhan)
    - loop2 gpio: pin 24 (bisa diganti sesuai kebutuhan)
    - struk gpio: pin 25 (bisa diganti sesuai kebutuhan)
    - led live: pin 17 (bisa diganti sesuai kebutuhan)
    - busy gpio: pin 22 (bisa diganti sesuai kebutuhan)

# Entry Gate
- entry gate adalah tempat masuk kendaraan
- flow:
  1. kendaraan mendekati entry gate terdeteksi oleh sensor yang mengirim sinyal ke loop1 
  2. loop2 mengaktifkan kamera untuk mengambil gambar full kendaraan dan memainkan suara Selamat Datang silahkan tempelkan kartu atau tekan tombol
  3. gambar plat nomor diproses di server menggunakan library fast-alpr (https://github.com/ankandrew/fast-alpr) (opsional bisa pakai alpr bisa juga tidak tergantung mode di setting)
  jika mode alpr tidak aktif, maka:
     - simpan data transaksi dan gambar sebagai attachment dari cctv ke database
     - print ticket (jika non member) lalu buka palang melalui gpio (kirim sinyal high ke trigger gpio lalu setelah 1 detik kirim sinyal low ke trigger gpio)
     - kendaraan masuk dan palang tertutup otomatis
    jika mode alpr aktif, maka:
  4. cek apakah plat nomor terdaftar di database
     - jika terdaftar, maka:
       1. Simpan data transaksi (termasuk plat yang terdeteksi) dengan type member_entry dengan gambar sebagai attachment ke database
       2. buka palang melalui gpio (kirim sinyal high ke trigger gpio lalu setelah 1 detik kirim sinyal low ke trigger gpio)
       3. kendaraan masuk dan palang tertutup otomatis
     - jika tidak terdaftar, maka:
       1. Simpan data transaksi (termasuk plat yang terdeteksi) dengan type member_entry dengan gambar sebagai attachment ke database
       3. print ticket (jika non member) lalu buka palang melalui gpio (kirim sinyal high ke trigger gpio lalu setelah 1 detik kirim sinyal low ke trigger gpio)
       4. kendaraan masuk dan palang tertutup otomatis
    5. Mainkan suara Terima Kasih silahkan masuk

# Exit Gate sudah ada di folder exit-gate, disesuaikan
- exit gate adalah tempat keluar kendaraan
- aplikasi berupa texbox untuk scan barcode atau kartu member
- flow:
    1. kendaraan mendekati exit gate terdeteksi oleh sensor yang mengirim sinyal ke loop1 
    2. loop2 mengaktifkan kamera untuk mengambil gambar full kendaraan
    3. gambar plat nomor diproses di server menggunakan library fast-alpr (https://github.com/ankandrew/fast-alpr)
    4. cek apakah plat nomor terdaftar di database di transaksi terakhir
       - jika terdaftar, maka:
         1. Simpan data transaksi (termasuk plat yang terdeteksi) dengan type member_exit dengan gambar sebagai attachment ke database
         2. buka palang melalui gpio (kirim sinyal high ke trigger gpio lalu setelah 1 detik kirim sinyal low ke trigger gpio)
         3. kendaraan keluar dan palang tertutup otomatis
       - jika tidak terdaftar, maka:
         1. update data transaksi (termasuk plat yang terdeteksi) dengan type member_exit dengan gambar sebagai attachment ke database
         2. print struk pembayaran (jika non member) lalu buka palang melalui gpio (kirim sinyal high ke trigger gpio lalu setelah 1 detik kirim sinyal low ke trigger gpio)
         3. kendaraan keluar dan palang tertutup otomatis

# admin
- aplikasi admin untuk mengelola data member, transaksi, dan setting
- aplikasi admin bisa diakses melalui web
- aplikasi admin harus bisa menampilkan data member, transaksi, dan setting
- aplikasi admin harus bisa menambah, mengedit, dan menghapus data member
- aplikasi admin harus bisa mengatur mode alpr aktif atau tidak
- aplikasi admin harus bisa mengatur setting gpio, cctv, dan database
- aplikasi admin harus bisa menampilkan data transaksi terakhir
- aplikasi admin harus bisa menampilkan data transaksi yang sudah diproses
- ada chart
