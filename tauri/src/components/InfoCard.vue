<template>
  <q-card
    flat
    bordered
    rounded
    class="items-center q-ma-md text-center relative"
    style="width: 15vw; height: 10vh; border-radius: 20px"
  >
    <div class="absolute-top" style="top: -20px">
      <q-chip class="bg-secondary text-body text-yellow text-bold">
        {{ $props.title }}
      </q-chip>
    </div>
    <!-- <q-img class="full-height"> -->
    <div class="row justify-center q-mt-md text-center transparent">
      <!-- style="background-color: #2d1a3c" -->
      <q-chip class="text-h5 text-primary text-center text-weight-bolder">
        {{ props.jumlah }}
      </q-chip>
    </div>
    <!-- </q-img> -->
  </q-card>
</template>

<script setup>
const props = defineProps({
  title: String,
  jumlah: String,
});
</script>
