<template>
  <div class="bg-primary card">
    <div class="card__info justify-center">
      <q-badge
        v-if="props.shortkey"
        floating
        color="dark"
        text-color="grey-3"
        :label="props.shortkey"
        class="q-pa-xs q-px-sm text-weight-bold z-top"
      />
      <q-separator inset class="bg-white" />
      <div class="card__logo text-center text-white">{{ props.title }}</div>

      <!-- <div class="card__type">debit</div> -->
      <div class="card__number justify-center">
        <span class="card__digit-group text-h5 text-weight-bolder">{{
          props.jumlah
        }}</span>
      </div>
    </div>
    <div class="card__texture"></div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useTransaksiStore } from "src/stores/transaksi-store";

const transaksiStore = useTransaksiStore();

const props = defineProps({
  title: String,
  shortkey: String,
  jumlah: String,
});

onMounted(async () => {
  await transaksiStore.getCountVehicleInToday();
  await transaksiStore.getCountVehicleOutToday();
  await transaksiStore.getCountVehicleInside();
});
</script>

<style scoped>
* {
  border: 0;
  box-sizing: border-box;
}
:root {
  --hue: 223;
  --bg: hsl(var(--hue), 10%, 90%);
  --fg: hsl(var(--hue), 10%, 10%);
  --primary: hsl(var(--hue), 90%, 55%);
  font-size: calc(20px + (30 - 20) * (100vw - 320px) / (1280 - 320));
}

/* .card,
.card__chip {
  overflow: hidden;
  position: relative;
} */
.card,
.card__chip-texture,
.card__texture {
  animation-duration: 3s;
  animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
}
.card {
  animation-name: rotate;
  background-color: var(--primary);
  background-image: radial-gradient(
      circle at 100% 0%,
      hsla(0, 0%, 100%, 0.08) 29.5%,
      hsla(0, 0%, 100%, 0) 30%
    ),
    radial-gradient(
      circle at 100% 0%,
      hsla(0, 0%, 100%, 0.08) 39.5%,
      hsla(0, 0%, 100%, 0) 40%
    ),
    radial-gradient(
      circle at 100% 0%,
      hsla(0, 0%, 100%, 0.08) 49.5%,
      hsla(0, 0%, 100%, 0) 50%
    );
  border-radius: 0.5em;
  /* border-left: 3px solid hsla(0, 0%, 0%, 0.1); */
  box-shadow: 0 0 0 hsl(0, 0%, 80%), 0 0 0 hsl(0, 0%, 100%),
    -0.2rem 0 0.75rem 0 hsla(0, 0%, 0%, 0.3);
  color: hsl(0, 0%, 100%);
  width: 13.3em;
  height: 6em;
  transform: translate3d(0, 0, 0);
}
.card__info,
.card__chip-texture,
.card__texture {
  position: absolute;
}
.card__chip-texture,
.card__texture {
  animation-name: texture;
  top: 0;
  left: 0;
  width: 200%;
  height: 100%;
}
.card__info {
  font: "DM Sans", sans-serif;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  padding: 0.75rem;
  inset: 0;
}
.card__logo,
.card__number {
  width: 100%;
}
.card__logo {
  font-weight: bold;
  font-style: normal;
}
.card__chip-texture {
  background-image: linear-gradient(
    -80deg,
    hsla(0, 0%, 100%, 0),
    hsla(0, 0%, 100%, 0.6) 48% 52%,
    hsla(0, 0%, 100%, 0)
  );
}
.card__type {
  align-self: flex-end;
  margin-left: auto;
}
.card__digit-group,
.card__exp-date,
.card__name {
  background: linear-gradient(
    hsl(0, 0%, 100%),
    hsl(0, 0%, 85%) 15% 55%,
    hsl(0, 0%, 70%) 70%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-family: "Courier Prime", monospace;
  filter: drop-shadow(0 0.05rem hsla(0, 0%, 0%, 0.3));
}
.card__number {
  font-size: 0.8rem;
  display: flex;

  /* justify-content: space-between; */
}
.card__texture {
  animation-name: texture;
  background-image: linear-gradient(
    -80deg,
    hsla(0, 0%, 100%, 0.3) 25%,
    hsla(0, 0%, 100%, 0) 45%
  );
}

/* Dark theme */
@media (prefers-color-scheme: dark) {
  :root {
    --bg: hsl(var(--hue), 10%, 30%);
    --fg: hsl(var(--hue), 10%, 90%);
  }
}

/* Animation */
/* @keyframes rotate {
  from,
  to {
    animation-timing-function: ease-in;
    box-shadow: 0 0 0 hsl(0, 0%, 63%), 0.1rem 0 0 hsl(0, 0%, 61%),
      -0.2rem 0 0.75rem 0 hsla(0, 0%, 0%, 0.3);
    transform: rotateY(-10deg);
  }
  25%,
  75% {
    animation-timing-function: ease-out;
    box-shadow: 0 0 0 hsl(0, 0%, 80%), 0 0 0 hsl(0, 0%, 55%),
      -0.25rem -0.05rem 1rem 0.15rem hsla(0, 0%, 0%, 0.3);
    transform: rotateY(0deg);
  }
  50% {
    animation-timing-function: ease-in;
    box-shadow: -0.1rem 0 0 hsl(0, 0%, 64%), 0 0 0 hsl(0, 0%, 100%),
      -0.3rem -0.1rem 1.5rem 0.3rem hsla(0, 0%, 0%, 0.3);
    transform: rotateY(10deg);
  }
} */
@keyframes texture {
  from,
  to {
    transform: translate3d(0, 0, 0);
  }
  40% {
    transform: translate3d(-40%, 0, 0);
  }
}
</style>
