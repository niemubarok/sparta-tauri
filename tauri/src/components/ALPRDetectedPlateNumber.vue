<template>
  <q-card
    class="plate-card"
  >
    <q-chip
      class="plate-chip"
    >
      <q-badge
        style="top: -10px; left: 7px"
        class="text-white absolute-top-left inset-shadow"
        :color="badge > 0.85 ? 'positive' : 'warning'"
        :label="`C: ${badge} %`"
      />
      <span
      class="text-dark"
        style="width: 100%; text-align: center; font-weight: bolder; 
        font-size: clamp(0.2rem, 2vw, 2rem);
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);"
      >
        {{
          plate_number?.replace(/(\D)(\d+)(\D)/, "$1 $2 $3")
        }}
      </span>
    </q-chip>
  </q-card>
</template>

<script setup>
const props = defineProps({
    plate_number: {
      type: String,
      required: true,
    },
    badge: {
      type: [String, Number],
      default: "ALPR",
    },
});
</script>

<style scoped>
.plate-card.q-card {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000000 !important;
  padding: 4px;
  max-width: 20dvw;
  height: 8dvh;
}

.plate-chip {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  padding: 0 1rem;
  margin: 0;
}
</style>
