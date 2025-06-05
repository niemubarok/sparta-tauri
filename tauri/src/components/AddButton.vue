<template>
  <section>
    <q-btn
      v-morph:btn:mygroup:300.resize="useComponentStore().morphGroupModel"
      class="fixed-bottom-right q-mr-sm"
      style="margin-bottom: 70px"
      fab
      color="brown-9"
      :label="props.label"
      size="xs"
      icon="add"
      @click="useComponentStore().nextMorph()"
    >
    </q-btn>

    <!-- height: 60%; -->
    <q-card
      v-morph:card1:mygroup:500.resize="useComponentStore().morphGroupModel"
      class="fixed-bottom-right q-ma-md bg-grey-1"
      style="width: 70%; border-bottom-left-radius: 2em; z-index: 2"
    >
      <q-banner class="text-grey-1 bg-brown-9 text-weight-bolder">
        <q-avatar
          size="20px"
          font-size="15px"
          color="yellow"
          text-color="brown"
          icon="close"
          class="float-right cursor-pointer text-weight-bolder"
          @click="useComponentStore().nextMorph()"
        />
        {{ props.title }}
      </q-banner>

      <q-card-section class="text-h6">
        <slot name="form"></slot>
      </q-card-section>

      <q-card-actions align="right">
        <slot name="button"></slot>
      </q-card-actions>
    </q-card>
  </section>
</template>

<script setup>
import { ref } from "vue";
import { useComponentStore } from "src/stores/component-store";

const props = defineProps({
  title: String,
  label: String,
});

// const nextMorph = () => {
//   useComponentStore().morphGroupModel =
//     useComponentStore().nextMorphStep[useComponentStore().morphGroupModel];
//   // console.log(morphGroupModel.value);
// };

// defineExpose({
//   nextMorph,
// });
</script>
