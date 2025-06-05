<template>
  <div>
    <q-item class="glass q-mt-md">
            <q-item-section avatar>
              <q-avatar color="primary" text-color="white" :icon="props.icon" />
            </q-item-section>
            <q-item-section>
              <q-item-label>{{props.title}}</q-item-label>
              <q-item-label caption lines="2">
                <span class="text-h6 text-weight-bolder text-black">{{
                  props.label
                }}</span></q-item-label
              >
            </q-item-section>
            <q-item-section side>
              <q-btn push text-color="white" style="width: 60px" color="black"
                >{{props.shortcut}}</q-btn
              >
              <!-- <q-icon name="star" color="yellow" /> -->
            </q-item-section>
          </q-item>
  </div>
</template>

<script setup>

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  label: {
    type: String,
    required: true
  },
  shortcut: {
    type: String,
    required: true
  }

});


</script>


<style lang="scss" scoped>
.glass {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}
</style>
