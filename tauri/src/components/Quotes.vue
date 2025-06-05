<template>
  <div class="container">
    <span class="typed-text text-primary text-center">
      <span v-if="typeValue">"</span>{{ typeValue }}
      <span class="blinking-cursor">|</span>
      <span v-if="typeValue">" </span>
    </span>
    <span class="cursor" :class="{ typing: typeStatus }">&nbsp;</span>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useSettingsService } from "src/stores/settings-service"; // Diubah

const typeValue = ref("");
const typeStatus = ref(false);
// const settingsStore.pesan = ["Demo", "Aplikasi Parkir", "Buatan Husni Mubarok"];
const typingSpeed = 50;
const erasingSpeed = 10;
const newTextDelay = 1000;
const indexText = ref(0);
const charIndex = ref(0);
const { globalSettings } = useSettingsService(); // Diubah
// TODO: Ambil 'pesan' dari globalSettings atau sumber data yang sesuai.
// Untuk sementara, gunakan array statis:
const pesan = ref(["Selamat Datang", "Aplikasi Parkir Spartakuler", "Versi Terbaru"]);

const typeText = () => {
  if (charIndex.value < pesan.value[indexText.value].length) { // Diubah
    if (!typeStatus.value) typeStatus.value = true;
    typeValue.value += pesan.value[indexText.value].charAt(
      charIndex.value
    ); // Diubah
    charIndex.value += 1;
    setTimeout(typeText, typingSpeed);
  } else {
    typeStatus.value = false;
    setTimeout(eraseText, newTextDelay);
  }
};
const eraseText = () => {
  if (charIndex.value > 0) {
    if (!typeStatus.value) typeStatus.value = true;
    typeValue.value = pesan.value[indexText.value].substring(
      0,
      charIndex.value - 1
    ); // Diubah
    charIndex.value -= 1;
    setTimeout(eraseText, erasingSpeed);
  } else {
    typeStatus.value = false;
    indexText.value += 1;
    if (indexText.value >= pesan.value.length) indexText.value = 0; // Diubah
    setTimeout(typeText, typingSpeed + 1000);
  }
};

onMounted(async () => {
  // await globalSettings.value?.getPesan(); // TODO: Sesuaikan jika getPesan ada di globalSettings atau pindahkan logika
  setTimeout(typeText(), newTextDelay + 200);
});
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
.container {
  // width: 30vw;
  // height: 10vh;
  display: flex;
  justify-content: center;
  flex: start;
}

// h1 {

span.typed-text {
  font-size: 1rem;
  font-weight: normal;
  color: #d59e46;
  overflow-wrap: normal;
  word-wrap: break-word;
}
// }

// Cursor blinking CSS Starts...
.blinking-cursor {
  font-size: 1rem;
  color: #2c3e50;
  -webkit-animation: 1s blink step-end infinite;
  -moz-animation: 1s blink step-end infinite;
  -ms-animation: 1s blink step-end infinite;
  -o-animation: 1s blink step-end infinite;
  animation: 1s blink step-end infinite;
  white-space: pre-wrap;
  overflow-wrap: normal;
  word-wrap: break-word;
}

@keyframes blink {
  from,
  to {
    color: transparent;
  }

  50% {
    color: #2c3e50;
  }
}

@-moz-keyframes blink {
  from,
  to {
    color: transparent;
  }

  50% {
    color: #2c3e50;
  }
}

@-webkit-keyframes blink {
  from,
  to {
    color: transparent;
  }

  50% {
    color: #2c3e50;
  }
}

@-ms-keyframes blink {
  from,
  to {
    color: transparent;
  }

  50% {
    color: #2c3e50;
  }
}

@-o-keyframes blink {
  from,
  to {
    color: transparent;
  }

  50% {
    color: #2c3e50;
  }
}

// Cursor blinking CSS Ends...
</style>
