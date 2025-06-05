<template>
  <q-item clickable :to="link">
    <q-item-section v-if="icon" avatar>
      <q-icon :name="icon">
        <q-tooltip v-if="componentStore.miniMode">{{ title }}</q-tooltip>
      </q-icon>
    </q-item-section>

    <q-item-section>
      <q-item-label>
        {{ title }}
        <q-tooltip v-if="componentStore.miniMode">{{ title }}</q-tooltip>
      </q-item-label>
      <q-item-label caption>
        {{ caption }}
        <q-tooltip v-if="componentStore.miniMode">{{ caption }}</q-tooltip>
      </q-item-label>
    </q-item-section>
  </q-item>
</template>

<script setup>
import { useComponentStore } from "stores/component-store";

const componentStore = useComponentStore();
const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  caption: {
    type: String,
    default: "",
  },
  link: {
    type: String,
    default: "#",
  },
  icon: {
    type: String,
    default: "",
  },
});
</script>
