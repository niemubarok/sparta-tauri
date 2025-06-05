<template>
  <q-card class="q-ml-xl q-mt-md" style="width: 97%; height: 90vh">
    <!-- <q-btn label="Export"  /> -->
    <q-card-section class="row">
      <div>
        <q-chip
          icon="fact_check"
          label="Daftar Transaksi"
          class="text-weight-bolder"
        />
      </div>
      <q-space />
      <div :style="!$q.screen.gt.sm ? '' : 'margin-top:10px;'">
        <q-space v-if="$q.screen.lt.sm" />
        <q-btn-group rounded>
          <q-btn
            rounded
            label="Semua"
            @click="onFilterStatus('all')"
            :color="filterStatus === 'all' ? 'primary' : 'grey'"
          />
          <q-btn
            rounded
            label="Masuk"
            @click="onFilterStatus(1)"
            :color="filterStatus === 1 ? 'primary' : 'grey'"
          />
          <q-btn
            rounded
            label="Keluar"
            @click="onFilterStatus(0)"
            :color="filterStatus === 0 ? 'primary' : 'grey'"
          />
        </q-btn-group>
        <q-btn
          v-model:selected="todaySelected"
          style="z-index: 1"
          class="shadow-4 q-ma-sm"
          rounded
          :class="isToday ? 'bg-secondary text-white' : 'bg-grey-7 text-grey-2'"
          dark
          @click="todayBtn()"
          >Hari Ini</q-btn
        >
        <q-btn
          style="z-index: 2"
          icon="event"
          rounded
          :label="startDateSelected ? startDateLabel() : 'Pilih Tanggal'"
          :class="
            startDateSelected && !todaySelected
              ? 'bg-secondary text-white'
              : 'bg-grey-7 text-grey-2'
          "
        >
          <q-popup-proxy
            transition-show="scale"
            transition-hide="scale"
            class="z-max"
            @before-show="updateProxy"
          >
            <q-date v-model="proxyDate" :options="optionFn">
              <div class="row items-center justify-end q-gutter-sm">
                <q-btn
                  v-close-popup
                  label="Cancel"
                  color="primary"
                  flat
                  @click="
                    startDateSelected = false;
                    endDateSelected = false;
                  "
                />
                <q-btn
                  v-close-popup
                  label="OK"
                  color="primary"
                  flat
                  @click="save('start')"
                />
              </div>
            </q-date>
          </q-popup-proxy>
        </q-btn>
        <span class="q-mx-sm">s/d</span>
        <q-btn
          style="z-index: 2"
          icon="event"
          rounded
          :label="endDateSelected ? endDateLabel() : 'Pilih Tanggal'"
          :class="
            endDateSelected && !todaySelected
              ? 'bg-secondary text-white'
              : 'bg-grey-7 text-grey-2'
          "
        >
          <q-popup-proxy
            transition-show="scale"
            transition-hide="scale"
            class="z-max"
            @before-show="updateProxy"
          >
            <q-date v-model="proxyDate" :options="optionFn">
              <div class="row items-center justify-end q-gutter-sm">
                <q-btn v-close-popup label="Cancel" color="primary" flat />
                <q-btn
                  v-close-popup
                  label="OK"
                  color="primary"
                  flat
                  @click="save('end')"
                />
              </div>
            </q-date>
          </q-popup-proxy>
        </q-btn>
      </div>
    </q-card-section>
    <!-- <q-card-section> -->
    <q-linear-progress
      :indeterminate="isLoading"
      color="primary"
      :visible="isLoading"
    />
    <!-- height="50vh" -->
    <q-table
      :style="
        reports.dataTransaksiPerTanggal.length > 0
          ? 'height: 75vh'
          : 'height: 200px'
      "
      class="sticky-header-table"
      v-model:pagination="pagination"
      :loading="isLoading"
      :rows="reports.dataTransaksiPerTanggal"
      :columns="columns"
      row-key="index"
      :rows-per-page-options="[10]"
      virtual-scroll
      :virtual-scroll-item-size="40"
    >
      <!-- @request="onRequest" -->
      <template v-slot:no-data>
        <div class="flex flex-center full-width q-pa-md">
          <q-icon name="warning" size="100px" color="grey-5" />
          <div class="text-h6 text-grey-5 q-ml-md">
            Tidak ada data transaksi
          </div>
        </div>
      </template>
      <template v-slot:body="props">
        <q-tr
          :props="props"
          :class="{
            'bg-grey-2':
              props.rowIndex % 2 !== 0 && selectedRow !== props.rowIndex,
            'bg-green-9 text-white': selectedRow === props.rowIndex,
          }"
        >
          <!-- class="cursor-pointer"
        @click.right.prevent="onRightClick(props.rowIndex)" -->
          <q-td key="index" :props="props">
            {{ (page - 1) * 10 + props.rowIndex + 1 }}
          </q-td>
          <q-td key="waktu_masuk" :props="props">
            {{
              new Date(props.row.waktu_masuk).toLocaleDateString("id-ID", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              })
            }}
          </q-td>
          <q-td key="waktu_keluar" :props="props">
            {{
              new Date(props.row.waktu_keluar).toLocaleDateString("id-ID", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              })
            }}
          </q-td>
          <q-td key="no_pol" :props="props">
            {{ props.row.no_pol }}
          </q-td>
          <q-td key="pic_body_masuk" :props="props" class="cursor-pointer">
            <template v-if="props.row.pic_body_masuk_base64">
              <q-img
                :src="
                  'data:image/jpeg;base64,' + props.row.pic_body_masuk_base64
                "
                :ratio="16 / 9"
                spinner-color="primary"
                spinner-size="82px"
                @click="
                  openImageDialog(
                    props.row.pic_body_masuk_base64,
                    'Gambar Pintu Masuk'
                  )
                "
              />
            </template>
            <template v-else>
              <div class="flex flex-center">
                <q-chip square label="No Image" icon="image_not_supported" />
              </div>
            </template>
          </q-td>
          <q-td key="pic_body_keluar" :props="props" class="cursor-pointer">
            <!-- {{ props.row.pic_body_keluar_base64 }} -->
            <template v-if="props.row.pic_body_keluar_base64">
              <q-img
                :src="
                  'data:image/jpeg;base64,' + props.row.pic_body_keluar_base64
                "
                :ratio="16 / 9"
                spinner-color="primary"
                spinner-size="82px"
                @click="
                  openImageDialog(
                    props.row.pic_body_keluar_base64,
                    'Gambar Pintu Keluar'
                  )
                "
              />
            </template>
            <template v-else>
              <div class="flex flex-center">
                <q-chip square label="No Image" icon="image_not_supported" />
              </div>
            </template>

            <!-- <q-icon v-else name="file_image_remove" /> -->
          </q-td>
          <q-td key="status" :props="props">
            {{ props.row.status === 1 ? "Masuk" : "Keluar" }}
          </q-td>
          <q-td key="tarif" :props="props">
            {{
              props.row.bayar_keluar
                ? formatCurrency(props.row.bayar_keluar)
                : 0
            }}
          </q-td>
        </q-tr>

        <!-- Image Dialog -->
        <q-dialog v-model="imageDialog" :maximized="true" class="no-scroll">
          <q-card class="glass full-width relative">
            <!-- <q-card-section class="row items-center justify-between"> -->
            <!-- <div>
                  <div class="text-h6">{{ currentImageLabel }}</div> -->
            <div>
              <q-avatar
                size="40px"
                class="cursor-pointer z-top absolute-top-right q-ma-sm"
                text-color="grey-3"
                color="red-9"
                icon="close"
                @click="imageDialog = false"
              />
            </div>
            <!-- </q-card-section> -->
            <q-img :src="currentImage" fit="cover" class="full-height" />
          </q-card>
        </q-dialog>
      </template>

      <template v-slot:bottom>
        <div class="row full-width justify-between">
          <div>
            <span class="text-h6 text-dark"> Total </span>
            <span class="text-weight-bolder text-h6 text-dark q-mr-sm">{{
              reports.totalPendapatanPerTanggal
                ?.toLocaleString("id-ID", {
                  style: "currency",
                  currency: "IDR",
                })
                .split(",")[0]
            }}</span>
          </div>
          <div>
            <q-pagination
              v-model="page"
              :max="reports.metaDataTransaksiPerTanggal.last_page"
              @update:model-value="onPageChange"
              prev-icon="chevron_left"
              next-icon="chevron_right"
              boundary-links
              direction-links
              :max-pages="5"
            />
          </div>
        </div>
      </template>
    </q-table>
    <!-- </q-card-section> -->
    <!-- <q-card-section>
      
    </q-card-section> -->
  </q-card>
</template>

<script setup>
import { useReportStore } from "src/stores/report-store";
// import { transaksiStore } from "src/stores/transaksi-store";
import { onMounted, ref, computed, watch } from "vue";
import { date, useQuasar } from "quasar";
// import DetailTransaksiDialog from "src/components/dialogues/DetailTransaksiDialog.vue";
// import DeleteTransaksiDialog from "src/components/dialogues/DeleteTransaksiDialog.vue";
import ls from "localstorage-slim";
import { formatCurrency } from "src/utils/helpers";
// import { generatePDF } from "src/utils/helpers";
// import jsPDF from 'jspdf';
// import 'jspdf-autotable';

// const exportTableToPDF = ()=> {
// let columns = ["No", "Tanggal", "Total"]; // Ganti dengan nama kolom tabel Anda
// let data = reports.pendapatanPerHari.map((item, index) => [
//   index + 1,
//   new Date(item.tanggal).toLocaleDateString('id-ID', { day: '2-digit', month: '2-digit', year: 'numeric' }),
//   formatCurrency(item.total)
// ]);

// Calculate total pendapatan
// let totalPendapatan = reports.totalPendapatanPerHari;

// Add total row at the bottom
// data.push(["", "Total Keseluruhan", formatCurrency(totalPendapatan)]);

// let doc = new jsPDF('p', 'pt');
// const title = "Laporan Pendapatan Per Hari";
// doc.text(title, doc.internal.pageSize.getWidth() / 2, 40, { align: 'center' });
// doc.text("Depok Fantasy Land", doc.internal.pageSize.getWidth() / 2, 55, { align: 'center' });
// doc.autoTable(columns, data, {startY: 60});

//       doc.save('table.pdf');
//     }

const $q = useQuasar();
const todaySelected = ref(false);
const startDateSelected = ref(false);
const endDateSelected = ref(false);
const reports = useReportStore();
const timeStamp = date.formatDate(Date.now(), "YYYY/MM/DD");
const datePicker = ref(timeStamp);
const proxyDate = ref(Date.now());
const isToday = ref(false);
const startDate = ref("");
const endDate = ref("");
const columns = [
  {
    name: "index",
    required: true,
    label: "No",
    align: "left",
    field: (row) => row.id,
    format: (val) => `${val}`,
    sortable: true,
  },
  {
    name: "waktu_masuk",
    required: true,
    label: "Waktu Masuk",
    align: "left",
    field: (row) => row.waktu_masuk,
    format: (val) => `${val}`,
    sortable: true,
  },
  {
    name: "waktu_keluar",
    required: true,
    label: "Waktu Keluar",
    align: "left",
    field: (row) => row.waktu_keluar,
    format: (val) => `${val}`,
    sortable: true,
  },
  {
    name: "no_pol",
    required: true,
    label: "No. Polisi",
    align: "left",
    field: (row) => row.no_pol,
    format: (val) => `${val}`,
    sortable: true,
  },
  {
    name: "pic_body_masuk",
    required: true,
    label: "Foto Masuk",
    align: "left",
    field: (row) => row.pic_body_masuk,
    format: (val) => `${val}`,
    sortable: true,
  },
  {
    name: "pic_body_keluar",
    required: true,
    label: "Foto Keluar",
    align: "left",
    field: (row) => row.pic_body_keluar,
    format: (val) => `${val}`,
    sortable: true,
  },
  {
    name: "status",
    required: true,
    label: "Status",
    align: "center",
    // field: (row) => row.status,
    // format: (val) => `${val}`,
    sortable: true,
  },
  {
    name: "tarif",
    required: true,
    label: "TARIF",
    align: "right",
    // field: (row) => row.status,
    // format: (val) => `${val}`,
    sortable: true,
  },
];

const selectedRow = ref();
const isLoading = ref(false);
const page = ref(1);

const imageDialog = ref(false);
const currentImage = ref("");
const currentImageLabel = ref("");

const filterStatus = ref("all");

const openImageDialog = (imageBase64, label) => {
  currentImage.value = "data:image/jpeg;base64," + imageBase64;
  currentImageLabel.value = label;
  imageDialog.value = true;
};

const onRequest = async () => {
  isLoading.value = true;
  await reports.getDataTransaksiPerTanggal(/* parameter yang diperlukan */);
  isLoading.value = false;
};

const onPageChange = async (newPage) => {
  isLoading.value = true;
  page.value = newPage;
  await reports.getDataTransaksiPerTanggal(
    startDate.value,
    endDate.value,
    page.value,
    filterStatus.value
  );
  isLoading.value = false;
};
const onFilterStatus = async (newStatus) => {
  isLoading.value = true;
  filterStatus.value = newStatus;
  console.log("filterStatus.value", filterStatus.value);
  await reports.getDataTransaksiPerTanggal(
    startDate.value,
    endDate.value,
    1,
    filterStatus.value
  );
  reports.metaDataTransaksiPerTanggal.current_page = 1;
  isLoading.value = false;
};

const onRightClick = (index) => {
  selectedRow.value = index;
};

const onDelete = async (no_transaksi) => {
  const deleteDialog = $q.dialog({
    component: DeleteTransaksiDialog,
    componentProps: {
      no_transaksi: no_transaksi,
    },
  });

  deleteDialog.update();
};
const onMenuHide = (index) => {
  if (selectedRow.value === index) {
    selectedRow.value = "";
  }
};

// const onClickDetail = async (no_transaksi) => {
//   await transaksiStore().getDetailTransaksi(no_transaksi);
//   const detailDialog = $q.dialog({
//     component: DetailTransaksiDialog,
//     props: {},
//   });
//   detailDialog.update();
// };

// const onClickPrint = async (diskon, no_transaksi, namaPaket) => {
//   const detailTransaksi = await transaksiStore().getDetailTransaksi(
//     no_transaksi
//   );

//   console.log("detailTransaksi", detailTransaksi);
//   // console.log("diskon", diskon);

//   await wahanaStore().getWahanaFromDB();
//   let paket = {
//     diskon,
//     namaPaket: namaPaket,
//     idWahana: detailTransaksi.map((item) => item.id_wahana),
//   };

//   wahanaStore().pilihPaket(paket, wahanaStore().daftarWahana);

//   const data = {
//     no_transaksi,
//     transaksi: JSON.stringify(transaksiStore().detailTransaksi),
//     diskon: transaksiStore().diskon,
//     totalAfterDiskon: transaksiStore().totalAfterDiskon,
//     totalBayar: transaksiStore().totalBayar,
//     namaPaket: wahanaStore().namaPaketTerpilih,
//   };

//   // console.log("data di daftarTransaksi", data);
//   // return;
//   window.electron.createPDFStruk(data, ls.get("namaPrinter"));
//   // generatePDF(data);

//   // window.electron.print(ls.get("namaPrinter"));
//   $q.notify({
//     message: "Berhasil",
//     color: "green",
//     position: "top",
//   });
//   transaksiStore().resetTransaksi();
// };
const todayBtn = async () => {
  isToday.value = true;
  startDateSelected.value = false;
  endDateSelected.value = false;
  // Ensure the time zone offset is accounted for so that startDate and endDate are set to today's date
  const today = new Date();
  today.setMinutes(today.getMinutes() - today.getTimezoneOffset());
  const formattedToday = date.formatDate(today, "YYYY-MM-DD");
  reports.startDate = formattedToday;
  reports.endDate = formattedToday;
  await reports.getDataTransaksiPerTanggal(
    reports.startDate,
    reports.endDate,
    page.value,
    filterStatus.value
  );
};

const dayLabel = (dateValue) => {
  const daysInIndonesian = {
    Sunday: "Minggu",
    Monday: "Senin",
    Tuesday: "Selasa",
    Wednesday: "Rabu",
    Thursday: "Kamis",
    Friday: "Jumat",
    Saturday: "Sabtu",
  };
  const dayInEnglish = date.formatDate(dateValue, "dddd");
  const dateInIndonesian = daysInIndonesian[dayInEnglish];

  return dateValue
    ? `${dateInIndonesian}, ${date.formatDate(dateValue, "DD-MM-YYYY")}`
    : "PILIH TANGGAL";
};

const startDateLabel = () => dayLabel(startDate.value);
const endDateLabel = () => dayLabel(endDate.value);

const updateProxy = () => {
  proxyDate.value = startDate.value
    ? date.formatDate(startDate.value, "YYYY/MM/DD")
    : datePicker.value;
  // chooseDateSelected.value = true;
};
const optionFn = (proxyDate) => {
  // const aWeek = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
  return proxyDate <= timeStamp;
};

const save = async (type) => {
  const isDateAfterToday = new Date(proxyDate.value).getTime() > Date.now();

  if (isDateAfterToday) {
    $q.notify({
      color: "negative",
      textColor: "white",
      icon: "error",
      message: "Tanggal tidak boleh lebih dari hari ini!",
    });
    return;
  }
  if (type === "start") {
    if (
      new Date(proxyDate.value).getTime() > new Date(endDate.value).getTime()
    ) {
      $q.notify({
        color: "negative",
        textColor: "white",
        icon: "error",
        message: "Tanggal mulai tidak boleh lebih dari tanggal akhir!",
      });
      return;
    }
    startDateSelected.value = true;
    startDate.value = proxyDate.value;
    reports.startDate = startDate.value;
    if (endDate.value === "") {
      endDate.value = proxyDate.value;
      endDateSelected.value = true;
      reports.endDate = startDate.value;
    }
    if (new Date(proxyDate.value).getDate() == new Date(Date.now()).getDate()) {
      isToday.value = true;
      todaySelected.value = true;
    } else {
      isToday.value = false;
      todaySelected.value = false;
    }
    await reports.getDataTransaksiPerTanggal(
      startDate.value,
      endDate.value,
      page.value,
      filterStatus.value
    );
    // console.log(reports.metaDataTransaksiPerTanggal);
  } else if (type === "end") {
    if (
      new Date(proxyDate.value).getTime() < new Date(startDate.value).getTime()
    ) {
      $q.notify({
        color: "negative",
        textColor: "white",
        icon: "error",
        message: "Tanggal akhir tidak boleh Kurang dari tanggal mulai!",
      });
      return;
    }

    endDateSelected.value = true;
    endDate.value = proxyDate.value;
    console.log("endate", endDate.value);
    console.log("startDate", startDate.value);
    reports.endDate = endDate.value;
    await reports.getDataTransaksiPerTanggal(
      startDate.value,
      endDate.value,
      page.value,
      filterStatus.value
    );
  }
};

onMounted(async () => {
  isLoading.value = true;
  await reports.getDataTransaksiPerTanggal(
    startDate.value,
    endDate.value,
    page.value
  );
  // filteredData.value = reports.dataTransaksiPerTanggal;
  // console.log("filteredData.value", filteredData.value);
  // console.log(reports.dataTransaksiPerTanggal)
  isLoading.value = false;
  isToday.value = true;
});
</script>

<style lang="sass">
.thead-sticky tr > *,
.tfoot-sticky tr > *
  position: sticky
  opacity: 1
  z-index: 1

.thead-sticky tr:last-child > *
  top: 0

.tfoot-sticky tr:first-child > *
  bottom: 0

.glass
  backdrop-filter: blur(10px) saturate(180%)
  -webkit-backdrop-filter: blur(16px) saturate(180%)
  background-color: rgba(255, 255, 255, 0.378)
  border-radius: 12px
  border: 1px solid rgba(255, 255, 255, 0.125)

:deep(.q-dialog__backdrop.fixed-full)
  background-color: rgba(0, 0, 0, 0.2)
  backdrop-filter: blur(10px)

.sticky-header-table
  // Mengatur tinggi tabel yang penting untuk tampilan sticky header */
  // height: 315px


.q-table__top,
// .q-table__bottom,
thead tr:first-child th
  // Warna latar belakang untuk header tabel sangat penting */
  background-color: #000 !important
  color: #fff
  font-weight: 500

thead tr th
  position: sticky
  z-index: 1
thead tr:first-child th
  top: 0

// Penyesuaian posisi saat indikator loading muncul
  &.q-table--loading thead tr:last-child th
  // Mengatur posisi top berdasarkan tinggi header sebelumnya 
  top: 40px

// Mencegah scrolling melewati header yang sticky saat fokus
  &.q-table--loading thead tr:first-child th
  top: 0
tbody
  // Margin top untuk body tabel agar tidak tertutup header 
  scroll-margin-top: 40px
</style>
