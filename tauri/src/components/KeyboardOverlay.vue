<template>
  <div class="fixed-bottom-left q-ma-md row z-top">
    <q-btn push v-show="modifierKey" class="text-grey-9 q-pa-md q-mr-sm">
      {{ modifierKey }}
    </q-btn>
    <q-btn push v-show="activeKey" class="text-grey-9 q-pa-md">
      {{ activeKey }}
    </q-btn>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";

const activeKey = ref(null);
const modifierKey = ref(null);

const keys = [
  ["escape", "f4"],
  ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
  ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
  ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
  ["z", "x", "c", "v", "b", "n", "m"],
];

const modifierKeys = ["ctrl", "alt", "shift"];

const handleKeyUp = (event) => {
  if (modifierKeys.includes(event.key.toLowerCase())) {
    modifierKey.value = null;
  }
  if (keys.flat().includes(event.key.toLowerCase())) {
    activeKey.value = null;
  }
};

const handleKeyDown = (event) => {
  if (event.shiftKey) {
    if (modifierKeys.includes(event.key.toLowerCase())) {
      modifierKey.value = event.key;
    }
  }
  if (keys.flat().includes(event.key.toLowerCase())) {
    activeKey.value = event.key.toLowerCase();
  }
};

onMounted(() => {
  window.addEventListener("keydown", handleKeyDown);
  window.addEventListener("keyup", handleKeyUp);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleKeyDown);
});
</script>

<style scoped>
/* .glass {
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  background-color: rgba(0, 0, 0, 0.096);
  border-radius: 5px;
  border: 1px solid rgba(14, 13, 13, 0.125);
} */
</style>
