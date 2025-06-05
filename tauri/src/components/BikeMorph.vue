<template>
  <div>
    <!-- border-bottom-left-radius: 2em; -->
    <q-card
      flat
      v-morph:tiket:bike:100.tween="morphStore.morphBikeModel"
      class="fixed-bottom-left q-ma-md bg-white text-teal"
      style="width: 40vw; left: 3vw; bottom: 1vh"
    >
      <q-card-section class="text-h6 flex no-wrap justify-start">
        <div>
          <div>
            <q-avatar
              size="40px"
              class="cursor-pointer z-top absolute-top-right q-ma-sm"
              text-color="grey-7"
              color="grey-5"
              icon="close"
              @click="morphStore.nextBikeMorph()"
            />
          </div>
          <q-icon name="directions_car" />

          Mobil
        </div>
      </q-card-section>
      <!-- <div> -->
      <!-- </div> -->

      <q-card-section class="text-subtitle1">
        <q-chip
          style="width: 200px"
          class="q-ma-md rounded-corner q-px-md bg-dark text-h4 text-white justify-center relative"
        >
          <q-badge
            style="top: -10px; left: -5px"
            class="bg-teal-8 absolute-top-left"
            text-color="text-white"
            label="Plat Nomor"
          />
          <span class="text-center text-weight-bolder">
            {{ transaksiStore.nomorTiket }}
          </span>
        </q-chip>
        <q-input
          class="bg-teal rounded-corner relative"
          label-color="white"
          color="teal"
          standout="bg-teal text-white font-bold"
          v-model="transaksiStore.nomorTiket"
          label="Masukkan Nomor Struk"
          ref="strukRef"
          autofocus
          @keydown.enter="
            [morphStore.nextBikeMorph(), transaksiStore.setCheckIn(true)]
          "
        >
          <template v-slot:append>
            <q-btn
              push
              class="bg-white text-dark"
              icon="keyboard_return"
              @click="
                [morphStore.nextBikeMorph(), transaksiStore.setCheckIn(true)]
              "
            />
          </template>
        </q-input>
      </q-card-section>

      <!-- <q-card-actions align="right">
        <q-btn flat label="Next" @click="morphStore.nextBikeMorph()" />
      </q-card-actions> -->
    </q-card>
  </div>
</template>
<script setup>
import { useMorphStore } from "src/stores/morph-store";
import { useTransaksiStore } from "src/stores/transaksi-store";
import { nextTick, onMounted, ref } from "vue";

const morphStore = useMorphStore();
const transaksiStore = useTransaksiStore();
const strukRef = ref(null);

const props = defineProps({
  title: String,
  title_icon: String,
});

onMounted(() => {
  nextTick(() => {
    strukRef.value.focus();
  });
});

// const nextCarMorphStep = {
//   btn: "ticket",
//   ticket: "payment",
//   payment: "btn",
// };

// const morphCarModel = store.morphCarModel;
// const nextCarMorph = () => {
//   morphCarModel.value = nextCarMorphStep[morphCarModel.value];
// };
</script>
