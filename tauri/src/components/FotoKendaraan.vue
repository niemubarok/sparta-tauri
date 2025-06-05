<template>
  <q-card flat class="bg-transparent relative">
    <div class="absolute z-top">
      <q-chip dense square icon="image" :label="title" class="glass" />
    </div>
    <div
      v-if="props.type == 'image'"
      class="relative glass overflow-hidden q-mt-sm"
      style="width: 49vw; height: 49vh; border-radius: 5px"
    >
      <img
        class="absolute full-width full-height"
        :src="props.url"
        style="
          object-fit: cover;
          width: 100%;
          height: 100%;
          transform: scale(2);
        "
      />
      <!-- top: 150px;
      right: 240px; -->

      <!-- <vue-image-zoomer
        style="width: 29vw; height: 30vh"
        :regular="props.url"
        :zoom="props.url"
        :auto-zoom="true"
        :zoom-amount="2"
      /> -->
    </div>
    <!-- style="height: 40vh; width: 30vw" -->
    <div v-else-if="props.type == 'video'">
      <slot name="video"> </slot>
    </div>
    <div class="full-width" v-else>
      <q-skeleton class="full-width">Tidak ada Kamera </q-skeleton>
    </div>
  </q-card>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { VueImageZoomer } from "vue-image-zoomer";
import "vue-image-zoomer/dist/style.css";

const props = defineProps({
  title: String,
  type: String,
  url: String,
});

// const { detectLicensePlateArea } = window.electron;
// onMounted(() => {
//   detectLicensePlateArea(props.url);
// });
</script>

<style scoped>
.glass {
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  background-color: rgba(255, 255, 255, 0.63);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.125);
}
</style>
