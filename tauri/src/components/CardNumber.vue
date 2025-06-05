<template>
  <div>
    <q-responsive :ratio="16 / 9" style="min-height: 100px; min-width: auto">
      <q-card class="card glass-light">
        <q-card-section class="q-pa-md full-height flex flex-center">
          <div class="column justify-start">
            <div class="text-body text-weight-bolder q-mb-sm text-grey-7">
              {{ props.caption }}
            </div>
            <GrowingNumber
              :value="props.number"
              class="text-weight-bolder text-green-9"
              :class="{
                ' text-h5': props.number < 1000000000,
                'text-body': props.number >= 1000000000,
              }"
            />
          </div>
        </q-card-section>
      </q-card>
    </q-responsive>
  </div>
</template>

<script setup>
import GrowingNumber from "src/components/GrowingNumber.vue";

const props = defineProps({
  number: {
    type: Number,
    default: 0,
  },
  caption: {
    type: String,
    default: "",
  },
  icon: {
    type: String,
    default: null,
  },
});
</script>
<style scoped>
.card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease-in-out;
}
.card:hover {
  transform: translateY(-5px);
}

.clamp {
  font-size: clamp(1.5rem, 20vw, 1rem);
}
/* .number-animation {
  /* Add your desired animation styles here */
</style>
