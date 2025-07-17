<script setup>
import { onMounted, ref } from 'vue'
import EssentialLink from 'components/EssentialLink.vue'
import KeyboardOverlay from 'src/components/KeyboardOverlay.vue'
import { useComponentStore } from 'stores/component-store'

const componentStore = useComponentStore()

const essentialLinks = [
    {
        title: 'Dashboard',
        caption: 'Lihat semua transaksi',
        icon: 'dashboard',
        link: '/',
    },
    {
        title: 'Data Transaksi',
        caption: 'Kelola transaksi parkir',
        icon: 'receipt_long',
        link: '/daftar-transaksi',
    },
    {
        title: 'Petugas',
        caption: 'Kelola data petugas',
        icon: 'person',
        link: '/petugas',
    },
    {
        title: 'Post Masuk',
        caption: 'Post Masuk',
        icon: 'directions_car',
        link: '/manual-gate',
    },
    {
        title: 'Tarif',
        caption: 'Kelola tarif parkir',
        icon: 'attach_money',
        link: '/tarif',
    },
    {
        title: 'Admin',
        caption: 'Seed data & system settings',
        icon: 'admin_panel_settings',
        link: '/admin',
    },
    // {
    //     title: 'ALPR Manager',
    //     caption: 'Kelola CCTV & ALPR',
    //     icon: 'videocam',
    //     link: '/alpr-manager',
    // },

    // {
    //   title: "Ticketing",
    //   caption: "",
    //   icon: "receipt",
    //   to: "/",
    // },

    // {
    //   title: "Laporan Tiket",
    //   caption: "",
    //   icon: "bar_chart",
    //   link: "/laporan/penjualan-tiket",
    // },
    // {
    //   title: "Data Transaksi",
    //   caption: "",
    //   icon: "fact_check",
    //   link: "/daftar-transaksi",
    // },
    // {
    //   title: "Laporan Transaksi Per Hari",
    //   caption: "",
    //   icon: "fact_check",
    //   link: "/laporan/transaksi/per-hari",
    // },
    // {
    //     title: 'Pos Keluar',
    //     caption: '',
    //     icon: 'output',
    //     link: '/',
    // },

    // {
    //   title: "Master Wahana",
    //   caption: "",
    //   icon: "apps",
    //   link: "/wahana",
    // },
    // {
    //   title: "Daftar Paket",
    //   caption: "",
    //   icon: "dataset",
    //   link: "/paket",
    // },
]

// const miniMode = ref(false);

const leftDrawerOpen = ref(false)

const toggleLeftDrawer = () => {
    componentStore.miniMode = !componentStore.miniMode
}

onMounted(() => {
    componentStore.miniMode = true

    // window.onkeydown = (key) => {
    //   if (key.key.startsWith("F")) {
    //     key.preventDefault();
    //   }
    // };
})
</script>

<template>
  <q-layout
    view="lHh Lpr lFf"
    class="bg-grey-3"
  >
    <!-- DEMO VERSI BETA Overlay (text only, no background) -->
    <!-- <div
      style="
        position: fixed;
        mix-blend-mode: multiply;
        bottom: 20vh;
        right: 32px;
        z-index: 9999;
        pointer-events: none;
        font-size: 6.5rem;
        font-weight: bold;
        color: #e53935;
        opacity: 0.2;
        font-style: italic;
        letter-spacing: 2px;
        transform: rotate(-5deg);
        user-select: none;
      "
    >
      DEMO VERSI BETA
    </div> -->
    <q-header v-if="$route.meta.isHeader">
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title> SPARTA </q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-if="$route.meta.isSidebar"
      v-model="leftDrawerOpen"
      show-if-above
      :mini="componentStore.miniMode"
      bordered
      class="bg-grey-10 text-white"
    >
      <q-list>
        <q-item-label header>
          Menu
        </q-item-label>

        <EssentialLink
          v-for="link in essentialLinks"
          :key="link.title"
          v-bind="link"
        />
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view class="full-width bg-gray-3" />
      <KeyboardOverlay class="z-top" />
    </q-page-container>
  </q-layout>
</template>
