<template>
  <div>
    <!-- <img :src="streamUrl" />
    <form>
      <div>
        <label for="id">ID:</label>
        <input type="text" id="id" v-model="formData.id" />
      </div>

      <div>
        <label for="no_pol">No Pol:</label>
        <input type="text" id="no_pol" v-model="formData.no_pol" />
      </div>

      <div>
        <label for="id_kendaraan">ID Kendaraan:</label>
        <input type="text" id="id_kendaraan" v-model="formData.id_kendaraan" />
      </div>

      <div>
        <label for="id_pintu_masuk">ID Pintu Masuk:</label>
        <input
          type="text"
          id="id_pintu_masuk"
          v-model="formData.id_pintu_masuk"
        />
      </div>

      <div>
        <label for="waktu_masuk">Waktu Masuk:</label>
        <input
          type="datetime-local"
          id="waktu_masuk"
          v-model="formData.waktu_masuk"
        />
      </div>
      <div>
        <label for="pic_body_masuk">FOTO MASUK</label>
        <input type="file" id="pic_body_masuk" @change="onFilePicked($event)" />
      </div>


      <button @click="storeData()">Submit</button>
    </form> -->

    <q-btn
      color="primary"
      icon="check"
      label="Open"
      @click="componentStore.openGate()"
    />
    <q-btn
      color="primary"
      icon="check"
      label="Close"
      @click="componentStore.closeGate()"
    />
    <q-btn
      color="primary"
      icon="check"
      label="home"
      @click="$router.push('/')"
    />
    <!-- <img :src="imageUrl" alt="Gambar" /> -->
  </div>

  <!-- {{ formData.pic_body_masuk }} -->

  <!-- <div id="struk" class="q-ma-lg">
    <Struk />
  </div> -->
  <q-btn
    color="primary"
    icon="check"
    label="cetakStruk"
    @click="onClickCetakStruk"
  />
  <q-btn
    color="primary"
    icon="check"
    label="Open gate"
    @click="openGateDialogue"
  />

  <div
    class="q-mt-xl"
    style="border: 1px solid black; width: 400px; height: 400px; margin: 0 auto"
  >
    <struk ref="strukRef" />
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from "vue";
import { Buffer } from "buffer";
import axios from "axios";
import { useTransaksiStore } from "src/stores/transaksi-store";
import { useComponentStore } from "src/stores/component-store";
import { useQuasar } from "quasar";
import OpenGateDialog from "src/components/OpenGateDialog.vue";
import { toPng } from "html-to-image";
import Struk from "src/components/Struk.vue";

// Usage example:

const componentRef = ref();
const strukRef = ref(null);

const $q = useQuasar();
// const struk = ref(null);

const formData = ref({
  id: "098760",
  no_pol: "1234",
  id_kendaraan: "A",
  status: 0,
  id_pintu_masuk: null,
  id_pintu_keluar: null,
  waktu_masuk: "",
  waktu_keluar: null,
  id_op_masuk: null,
  id_op_keluar: "00001",
  id_shift_masuk: null,
  id_shift_keluar: "S3",
  kategori: null,
  status_transaksi: "0",
  bayar_masuk: null,
  bayar_keluar: 32000,
  jenis_system: null,
  tanggal: "2023-03-03T18:34:07.000Z",
  pic_body_masuk: "",
  pic_body_keluar: null,
  pic_driver_masuk: null,
  pic_driver_keluar: null,
  pic_no_pol_masuk: null,
  pic_no_pol_keluar: null,
  sinkron: 0,
  adm: null,
  alasan: null,
  pmlogin: null,
  pklogin: "2015-03-03T14:45:00.000Z",
  upload: 0,
  manual: 0,
  veri_kode: null,
  veri_check: null,
  veri_adm: null,
  veri_date: null,
  denda: null,
  extra_bayar: null,
  no_barcode: null,
  jenis_langganan: null,
  post_pay: 0,
  reff_kode: "",
  valet_adm: null,
  waktu_valet: null,
  valet_charge: null,
  valet_ops: null,
  valet_nopol: null,
  login_waktu_valet: null,
  cara_bayar: null,
  unit_member: null,
  reserved: 0,
  no_voucher: null,
  seri_voucher: null,
  no_access_in: null,
  no_access_out: null,
  inap: null,
  casual_denda: null,
});
const transaksiStore = useTransaksiStore();
const componentStore = useComponentStore();

// const transaksi = {
//   platNomor: "B9876AB",
//   waktuMasuk: "10:00:00",
//   waktuKeluar: "11:00:00",
//   lamaParkir: "1",
//   biayaParkir: "3000",
// };

const onClickCetakStruk = () => {
  transaksiStore.onClickCetakStruk();
};
const onFilePicked = (event) => {
  const files = event.target.files;
  const file = files[0];
  let filename = file.name;

  const fileReader = new FileReader();

  fileReader.addEventListener("load", () => {
    // Set the file data to a variable
    const fileData = fileReader.result;
    console.log(fileData);
    formData.value.pic_body_masuk = fileData;

    // Display the file in HTML using an <img> tag
    const imageElement = document.createElement("img");
    // imageElement.src = fileData;

    // Append the image element to a container element
    const containerElement = document.getElementById("imageContainer");
    containerElement.innerHTML = ""; // Clear the existing image
    containerElement.appendChild(imageElement);
  });

  fileReader.readAsDataURL(file);
  // console.log(formData.value.pic_body_masuk);
};
const storeData = async () => {
  console.log(formData.value);
  const store = await axios.post(
    process.env.API_URL + "/transactions/create",
    formData.value
  );
  console.log(store);
};

const openGateDialogue = () => {
  const openGate = $q.dialog({
    component: OpenGateDialog,
    noBackdropDismiss: true,
  });
  openGate.update();
};

// onMounted(async () => {
//   console.log(print);
// });

// const getStreamUrl = async () => {
//   const url = `http://10.40.38.51:80/ISAPI/Streaming/channels/1/picture`;
//   const headers = {
//     Authorization: getAuthorizationHeader(),
//   };

//   try {
//     const response = await axios.get(url, { headers });
//     console.log(response);
//     streamUrl.value = response.data;
//   } catch (error) {
//     console.error(error);
//   }
// };

// const generateNonce = () => {
//   return Math.random().toString(36).substr(2, 16);
// };
// const generateCNonce = () => {
//   const randomChars = '0123456789abcdef';
//   let result = '';
//   for (let i = 0; i < 16; i++) {
//     result += randomChars[Math.floor(Math.random() * randomChars.length)];
//   }
//   return result;
// };

// const getAuthorizationHeader = () => {
//   const nonce = generateNonce();
//   const realm = "IP Camera(AA568)";
//   const algorithm = "MD5";
//   const method = "GET";
//   const uri = "ISAPI/Streaming/channels/1/picture";

//   const ha1 = md5(`${username}:${realm}:${password}`);
//   const ha2 = md5(`${method}:${uri}`);
//   const response = md5(`${ha1}:${nonce}:${ha2}`);

//   return `Digest username="${username}", realm="${realm}", nonce="${nonce}", uri="${uri}", response="${response}", qop="auth"`;
// };

// onMounted(async () => {
//   // componentStore.openGate();

//   try {
//     const transaksi = await transaksiStore.getTransaksiByNopol("B0987");
//     const response = await axios.post(
//       process.env.API_URL + "/transactions/pic",
//       {
//         no_pol: "G2565AY",
//       }
//     );
//     imageUrl.value = response.data;
//     console.log(imageUrl.value);
//   } catch (error) {
//     console.error(error);
//   }
// });
</script>
