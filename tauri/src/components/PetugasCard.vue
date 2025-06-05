<template>
  <!-- Jumlah Surat card -->
  <!-- :class="$q.screen.lt.sm ? 'full-width q-ma-md ':''" -->
  <q-card
    class="bg-grey-4 items-center q-mr-md"
    style="width: 10vw; height: 10vh; border-radius: 10px"
  >
    <!-- <q-img class="full-height"> -->
    <div class="row full-height items-center fullwidth text-center transparent">
      <div class="col">
        <q-chip
          class="text-h6 text-yellow text-bold"
          style="background-color: #5769f9"
        >
          {{ $props.petugas }}
        </q-chip>

        <!-- <q-chip
            style="background-color: #8abee3"
            class="text-h6 text-dark text-center text-bold"
          >
            {{ props.jumlah }}
          </q-chip> -->
      </div>
    </div>
    <!-- </q-img> -->
  </q-card>
</template>

<script setup>
const props = defineProps({
  petugas: String,
  jumlah: String,
});
</script>
