<style scoped lang="scss">
code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, "Courier New",
    monospace;
}

.card {
  // width: 60%;
  margin-bottom: 1rem;
  height: 254px;
  // box-shadow: 1px 5px 60px 0px #100a886b;
}

.card .card-border-top {
  width: 60%;
  height: 3%;
  // background: #6b64f3;
  margin: auto;
  border-radius: 0px 0px 15px 15px;
}
</style>

<template>
  <div class="card glass q-mb-lg" style="width: 50vw; height: 35vh">
    <MemberRibbon />
    <div class="card-border-top bg-primary"></div>
    <div class="column q-pa-md text-dark flex items-center">
      <PlatNomor style="transform: scale(1.2)" />
    </div>
    <!-- <q-separator spaced light /> -->
    <div class="bg-grey-4 column items-start q-pa-lg">
      <!-- <q-chip
        square
        class="bg-transparent text-primary text-h5 text-weight-bolder"
      > -->
      <div class="text-subtitle2">
        <q-chip style="width: 150px" label="Nama Pelanggan " />
        <span class="text-h6"> : {{ props.nama }}</span>
      </div>
      <div class="text-subtitle2">
        <q-chip style="width: 150px" label="Alamat " />
        <span class="text-h6"> : </span
        ><span class="text-subtitle2"> {{ props.alamat || "-" }}</span>
      </div>
      <div class="text-subtitle2">
        <q-chip style="width: 150px" label="Masa Berlaku " />

        <span class="text-h6"> : </span
        ><span
          class="text-subtitle"
          :class="transaksiStore.isMemberExpired ? 'text-red' : ''"
        >
          {{ props.expiration }}</span
        >
      </div>
      <!-- </q-chip
      > -->
    </div>
  </div>

  <!-- <div class="bg">
    <h1>Kiberbash</h1>
  </div> -->
  <!-- <div
    class="nft relative"
    style="height: 40vh; width: 100%"
    :class="$q.screen.lt.md ? 'full-width' : ''"
  >
    <MemberRibbon />
    <div class="main">
      <h4 class="text-white text-weight-bold flex justify-start">
        {{ props.nama }}
        <q-separator spaced />
        <div class="">
          <q-card
            tag="div"
            bordered
            class="no-shadow bg-transparent rounded-corner q-pa-md text-subtitle2 text-grey-3"
            style="
              width: 60%;
              overflow-x: visible;
              overflow-wrap: break-word;
              border-color: grey;
            "
          >
            label="lorem kadhkuashdiuagwdhbaskjdghaughdhadha dsagdagdabdhas
            dasjhgdjagdagduyagd"
          </q-card>
        </div>
        <div class="flex row absolute-bottom-left">
          <q-chip
            square
            style="border-bottom-left-radius: 7px"
            class="text-grey-10 bg-grey-4"
            icon="schedule"
            :label="props.expiration"
          />
        </div>
        <div class="full-width q-mt-xl flex justify-end">
          <PlatNomor class="q-ma-lg" style="transform: scale(1.5)" />
        </div>
      </h4>
    </div>
  </div> -->
</template>

<script setup>
import { useTransaksiStore } from "src/stores/transaksi-store";
import MemberRibbon from "./MemberRibbon.vue";
import PlatNomor from "./PlatNomor.vue";

const props = defineProps({
  nama: String,
  alamat: String,
  expiration: String,
});

const transaksiStore = useTransaksiStore();
</script>
