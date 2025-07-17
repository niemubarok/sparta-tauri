import { defineStore } from "pinia";
import { ref } from "vue";
import ls from "localstorage-slim";
import axios from "axios";  

export const useTransaksiStore = defineStore("transaksi", {
  state: () => ({
    API_URL: ref(ls.get("API_URL")) || "-",
    isAdmin: ref(false),
    dataCustomer: ref(""),
    transaksi: ref([]),
    lokasiPos: ref(ls.get("lokasiPos") || "-"),
    jenisKendaraan: [],
    selectedJenisKendaraan: ref(""),
    defaultJenisKendaraan: ref(
      ls.get("defaultJenisKendaraan") || "-"
    ),
    platNomor: ref(""),
    nomorTiket: ref(""),
    isMember: ref(false),
    isMemberExpired: ref(false),
    isCheckedIn: ref(false),
    waktuMasuk: ref(""),
    waktuKeluar: ref(""),
    durasi: ref(0),
    biayaParkir: ref(0),
    bayar: ref(),
    pic_body_keluar: ref(null),
    vehicleInToday: ref(0),
    totalVehicleOut: ref(0),
    totalVehicleInside: ref(0),
  }),
  actions: {
    setAPIURL(url) {
      ls.get("API_URL", url);
    },
    setTransaksi(transaksi) {
      this.transaksi = transaksi;
    },
    async setManualOpenGate() {
      try {
        const response = await axios.post(
          this.API_URL + "/transactions/manual-open-gate",
          {
            petugas: ls.get("pegawai").nama,
            id_shift: ls.get("shift"),
            id_pos: ls.get("lokasiPos").value,
            pic: this.pic_body_keluar,
          }
        );

        console.log(response.data);
        if (response.data) {
          $q.notify({
            type: "positive",
            message: "Tersimpan",
            position: "top",
            timeout: 1000,
          });
        }
      } catch (error) {}
    },
    async login(username, password) {
      try {
        const lokasiPos = ls.get("lokasiPos")?.value || null;
        const response = await axios.post(this.API_URL + "/user/login", {
          username: username,
          password: password,
          id_pos: lokasiPos,
        });

        // console.log(response);set
        ls.set("timeLogin", response.data.time_login);
        ls.set("shift", response.data.shift);
        ls.set("tanggal", response.data.tanggal);
        const adminLevels = ["0001", "0002", "0003", "0004"];
        this.isAdmin = adminLevels.includes(response.data.level_pegawai);

        return response.data;
      } catch (error) {
        console.log(error);
        // if (error.response && error.response.status === 401) {
        //   // Handle 401 error here
        //   console.log("Invalid username or password");
        //   $q.notify({
        //     type: "negative",
        //     message: "Cek kembali username dan password anda",
        //     position: "top",
        //     timeout: 1000,
        //   });
        // }
        // }
      }
    },
    async logout() {
      const id_petugas = ls.get("pegawai")?.id_pegawai;
      const id_shift = ls.get("shift");
      const pos = ls.get("lokasiPos")?.value;
      const time_login = ls.get("timeLogin");
      const tanggal = ls.get("tanggal");

      const res = await axios.post(this.API_URL + "/user/logout", {
        id_petugas,
        id_shift,
        pos,
        time_login,
        tanggal,
      });

      console.log(res);
    },
    getLocalDateTimeString() {
      const now = new Date();
      const formatter = new Intl.DateTimeFormat('id-ID', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      })
    
      // Menghasilkan string dengan format lokal dan mengganti karakter pemisah
      return formatter.format(now).replace(/\//g, '-').replace(',', '');
    },

    async updateTableTransaksi() {
      const formData = {
        // id: uuidv4(),
        nomorTiket: this.nomorTiket,
        no_pol: this.platNomor,
        id_kendaraan: this.selectedJenisKendaraan.id,
        status: 1,
        // id_pintu_masuk: null,
        // id_pintu_keluar: null,
        // entry_time: "",
        // waktu_keluar: this.getLocalDateTimeString(),
        // id_op_masuk: null,
        id_op_keluar: ls.get("pegawai")?.id_pegawai,
        // id_shift_masuk: null,
        id_shift_keluar: ls.get("shift"),
        // kategori: null,
        status_transaksi: "0",
        // bayar_masuk: null,
        bayar_keluar: this.biayaParkir,
        // jenis_system: null,
        // tanggal: this.getLocalDateTimeString(),
        // pic_body_masuk: "",
        pic_body_keluar: this.pic_body_keluar,
        // pic_driver_masuk: null,
        // pic_driver_keluar: null,
        // pic_no_pol_masuk: null,
        // pic_no_pol_keluar: null,
        // sinkron: 0,
        // adm: null,
        // alasan: null,
        // pmlogin: null,
        pklogin: ls.get("timeLogin"),
        // upload: 0,
        // manual: 0,
        // veri_kode: null,
        // veri_check: null,
        // veri_adm: null,
        // veri_date: null,
        // denda: null,
        // extra_bayar: null,
        no_barcode: this.nomorTiket,
        // jenis_langganan: null,
        // post_pay: 0,
        // reff_kode: "",
        // valet_adm: null,
        // waktu_valet: null,
        // valet_charge: null,
        // valet_ops: null,
        // valet_nopol: null,
        // login_waktu_valet: null,
        // cara_bayar: null,
        // unit_member: null,
        // reserved: 0,
        // no_voucher: null,
        // seri_voucher: null,
        // no_access_in: null,
        // no_access_out: null,
        // inap: null,
        // casual_denda: null,
      };

      // console.log(formData.pic_body_keluar);
      // return 200
      try {
        const update = await axios.patch(
          this.API_URL + "/transactions/update",
          {
            formData,
          }
        );
        console.log(update);
        if (update.status == 200) {
          console.log(update.data);
          return 200;
        }
      } catch (error) {}
    },
    setCheckIn(isCheckedIn) {
      this.isCheckedIn = isCheckedIn;
    },
    async getJenisKendaraan() {
      // const localData = ls.get("jenisKendaraan");
      // if (localData) {
      //   this.jenisKendaraan = JSON.parse(localData);
      // } else {
      const response = await fetch(this.API_URL + "/vehicles/all");
      const data = await response.json();
      const dataJenisKendaraan = data.map((data) => {
        return {
          label: data.nama,
          id: data.id,
          shortcut: data.short_cut,
        };
      });
      console.log(data);
      // this.jenisKendaraan = dataJenisKendaraan;
      ls.set("jenisKendaraan", JSON.stringify(dataJenisKendaraan));
      return dataJenisKendaraan;
      // }
    },
    async getTransaksiByNopol(no_pol) {
      // console.log(no_pol);
      const response = await axios.post(this.API_URL + "/transactions/nopol", {
        no_pol: no_pol,
      });
      const data = response.data;
      // console.log(data);
      this.transaksi.value = data;
      return data;
    },

    async getLokasiPos() {
      // const localData = ls.get("lokasiPos");
      // if (localData) {
      //   this.lokasiPos.value = JSON.parse(localData);
      // } else {
      const response = await fetch(this.API_URL + "/locations/all");
      const data = await response.json();
      const lokasiPos = data.map((data) => {
        return {
          label: data.nama,
          value: data.id,
          jenis: data.jenis,
        };
      });
      return lokasiPos;
      // console.log(data);
      // this.lokasiPos.value = data;
      // ls.set("lokasiPos", data);
      // }
    },
    async getCustomerByNopol() {
      try{

        const res = await axios.post(this.API_URL + "/customers/nopol", {
          no_pol: this.platNomor?.toUpperCase(),
        });
        
      if (res.data) {
        this.isMember = true;
        this.dataCustomer = res.data;
        console.log(res.data);
        return res.data;
      } else {
        this.isMember = false;
      }
    }catch (err){
      Notify.create({
        message: "gagal terhubung ke backend " + err.message,
        color: "negative",
        icon: "report_problem",
        position: "top",
      })

    }
    },

    async getTarifJenisKendaraan() {
      const response = await axios.post(this.API_URL + "/prices/type", {
        id_jenis_kendaraan: this.selectedJenisKendaraan.id,
      });
      const data = response.data[0];
      console.log(data);
      return data;
    },

    async calculateParkingFee(waktuMasuk, waktuKeluar) {
      if (this.isMember && !this.isMemberExpired) {
        return 0;
      } else {
        const tarif = await this.getTarifJenisKendaraan();
        const tarifAwal = parseInt(tarif?.tarif);
        const tarifBerikutnya = parseInt(tarif?.tarif_interval);
        const tarifMaksimal = parseInt(tarif?.maksimum);
        const interval = parseInt(tarif?.interval);

        const currentTime = new Date();
        const targetTime = new Date(waktuMasuk);
        const diffInMilliseconds = currentTime - targetTime;

        const durationInHour = Math.floor(
          diffInMilliseconds / (1000 * 60 * 60)
        );

        const interval24 = Math.floor(durationInHour / 24);
        // console.log("durationInHour", durationInHour);

        // Calculate the additional fee
        let additionalFee = durationInHour * tarifBerikutnya;
        let totalFee = 0;

        //jika dibawah 1 jam pakai tarif awal
        if (durationInHour <= 1) {
          totalFee = tarifAwal;
        }
        //jika diatas 1 jam tarif awal + tarif berikutnya
        else if (durationInHour > 1) {
          totalFee += additionalFee;
        }
        //jika total tarif lebih dari tarif maksimal
        if (totalFee > tarifMaksimal) {
          totalFee = tarifMaksimal;
        }

        // Calculate the number of 24-hour intervals
        const additionalHourAfter24 = durationInHour - interval24 * 24;
        // console.log("additionalHourAfter24", additionalHourAfter24);
        let additionalFeeAfter24 = additionalHourAfter24 * tarifBerikutnya;
        //jika lebih dari 24 jam tarif maksimal + tarif berikutnya
        if (interval24 > 0) {
          if (additionalFeeAfter24 > tarifMaksimal) {
            additionalFeeAfter24 = tarifMaksimal;
          }
          // console.log("additionalFeeAfter24", additionalFeeAfter24);
          totalFee = interval24 * tarifMaksimal + additionalFeeAfter24;
        }
        // console.log("interval24", interval24);
        if (this.isMember && !this.isMemberExpired) {
          totalFee = 0;
        }
        totalFee = Math.round(totalFee);

        this.biayaParkir = totalFee;
        return totalFee;
      }
    },

    async getCountVehicleInToday() {
      const response = await axios.get(
        this.API_URL + "/transactions/count/vehicle/in"
      );
      const data = response.data;
      this.vehicleInToday = data.count;
      return data.count;
    },
    async getCountVehicleOutToday() {
      const response = await axios.post(
        this.API_URL + "/transactions/count/vehicle/out",
        {
          shift_id: ls.get("shift"),
        }
      );
      const data = response.data;
      // console.log(data);
      if (data.length) {
        // const total = data.reduce(
        //   (total, item) => total + parseInt(item.count),
        //   0
        // );
        // const countPerVehicle = data.map((item) => ({
        //   nama: item.nama,
        //   count: item.count,
        // }));

        // const uangMasuk = data.map((item) => parseInt(item.uang_masuk));
        // console.log(uangMasuk);

        // const totalUangMasuk = data.reduce(
        //   (total, item) => total + parseInt(item.uang_masuk),
        //   0
        // );

        this.totalVehicleOut = Array.isArray(data)
          ? data.reduce((total, count) => total + Number(count.count), 0)
          : 0;
        return data;

        // // console.log(names);
        // console.log(uangMasuk);
        // return { total, countPerVehicle, uangMasuk };
      }
      return { count: 0, names: "Belum ada" };
    },
    async getCountVehicleInside() {
      const response = await axios.get(
        this.API_URL + "/transactions/count/vehicle/inside"
      );
      const data = response.data;
      this.totalVehicleInside = data.count;
      return data.count;
    },

    onClickCetakStruk() {
      const localeOptions = {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      };

      const pegawai = ls.get("pegawai")?.nama;
      const lokasiPosValue = ls.get("lokasiPos")?.value;

      const namaPerusahaan = process.env.COMPANY_NAME?.toUpperCase();
      // console.log(this.selectedJenisKendaraan.label);
      const transaksi = {
        jnsKendaraan: this.selectedJenisKendaraan.label,
        platNomor: this.platNomor
          ? this.platNomor.replace(/(\D)(\d+)(\D)/, "$1 $2 $3")
          : "",
        petugas: pegawai,
        idPintuKeluar: lokasiPosValue,
        waktuMasuk: this.waktuMasuk
          ? new Date(this.waktuMasuk).toLocaleString("id-ID", localeOptions)
          : "",
        waktuKeluar: this.waktuKeluar
          ? new Date(this.waktuKeluar).toLocaleString("id-ID", localeOptions)
          : "",
        lamaParkir: this.durasi,
        biayaParkir: this.biayaParkir
          .toLocaleString("id-ID", {
            style: "currency",
            currency: "IDR",
          })
          .split(",")[0],
      };
      window?.electron.createPDFStruk(namaPerusahaan, transaksi);
    },
  },
});
