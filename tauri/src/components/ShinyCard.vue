<template>
  <div class="card" :class="cardColorClass">
    <div class="card__info justify-center">
      <q-badge
        v-if="props.shortkey"
        floating
        :color="badgeColor"
        text-color="white"
        :label="props.shortkey"
        class="q-pa-xs q-px-sm text-weight-bold z-top animated-badge"
      />
      <q-separator inset class="bg-gradient" />
      <div class="card__logo text-center text-white animated-text">{{ props.title }}</div>

      <div class="card__number justify-center">
        <span class="card__digit-group text-h5 text-weight-bolder animated-number">{{
          props.jumlah
        }}</span>
      </div>
    </div>
    <div class="card__texture"></div>
    <div class="card__glow"></div>
    <div class="card__sparkle"></div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from "vue";
import { useTransaksiStore } from "src/stores/transaksi-store";

const transaksiStore = useTransaksiStore();

const props = defineProps({
  title: String,
  shortkey: String,
  jumlah: String,
  colorTheme: {
    type: String,
    default: 'rainbow' // rainbow, purple, blue, green, pink, orange
  }
});

// Computed properties for dynamic colors
const cardColorClass = computed(() => {
  return `card--${props.colorTheme}`;
});

const badgeColor = computed(() => {
  const colorMap = {
    rainbow: 'purple',
    purple: 'deep-purple',
    blue: 'blue',
    green: 'green',
    pink: 'pink',
    orange: 'orange'
  };
  return colorMap[props.colorTheme] || 'purple';
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

.card {
  overflow: hidden;
  position: relative;
  animation: rotate 4s ease-in-out infinite, colorShift 6s ease-in-out infinite;
  border-radius: 1em;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), 
              0 0 0 1px rgba(255, 255, 255, 0.1),
              inset 0 1px 0 rgba(255, 255, 255, 0.2);
  color: hsl(0, 0%, 100%);
  width: 13.3em;
  height: 6em;
  transform: translate3d(0, 0, 0);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Rainbow theme (default) */
.card--rainbow {
  background: linear-gradient(45deg, 
    #ff0081, #ff8c00, #ffd700, #32cd32, 
    #00bfff, #8a2be2, #ff1493, #ff0081);
  background-size: 400% 400%;
  animation: rainbow 3s ease infinite, rotate 4s ease-in-out infinite;
}

/* Purple theme */
.card--purple {
  background: linear-gradient(135deg, 
    #667eea 0%, #764ba2 100%);
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
}

/* Blue theme */
.card--blue {
  background: linear-gradient(135deg, 
    #74b9ff 0%, #0984e3 50%, #6c5ce7 100%);
  box-shadow: 0 8px 32px rgba(116, 185, 255, 0.4);
}

/* Green theme */
.card--green {
  background: linear-gradient(135deg, 
    #55efc4 0%, #00b894 50%, #00cec9 100%);
  box-shadow: 0 8px 32px rgba(0, 184, 148, 0.4);
}

/* Pink theme */
.card--pink {
  background: linear-gradient(135deg, 
    #fd79a8 0%, #e84393 50%, #a29bfe 100%);
  box-shadow: 0 8px 32px rgba(253, 121, 168, 0.4);
}

/* Orange theme */
.card--orange {
  background: linear-gradient(135deg, 
    #fdcb6e 0%, #e17055 50%, #fd79a8 100%);
  box-shadow: 0 8px 32px rgba(253, 203, 110, 0.4);
}

.card__info {
  font-family: "DM Sans", sans-serif;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  padding: 0.75rem;
  position: absolute;
  inset: 0;
  z-index: 2;
}

.card__logo,
.card__number {
  width: 100%;
}

.card__logo {
  font-weight: bold;
  font-style: normal;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.card__digit-group {
  background: linear-gradient(
    45deg,
    hsl(0, 0%, 100%),
    hsl(60, 100%, 90%) 25%,
    hsl(180, 100%, 85%) 50%,
    hsl(300, 100%, 90%) 75%,
    hsl(0, 0%, 100%)
  );
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-family: "Courier Prime", monospace;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
  background-size: 200% 200%;
  animation: textShimmer 2s ease-in-out infinite;
}

.card__number {
  font-size: 0.8rem;
  display: flex;
}

.card__texture {
  position: absolute;
  top: 0;
  left: 0;
  width: 200%;
  height: 100%;
  background-image: linear-gradient(
    -80deg,
    hsla(0, 0%, 100%, 0.4) 20%,
    hsla(0, 0%, 100%, 0.8) 25%,
    hsla(0, 0%, 100%, 0.4) 30%,
    hsla(0, 0%, 100%, 0) 45%
  );
  animation: texture 3s ease-in-out infinite;
  z-index: 1;
}

.card__glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, 
    rgba(255, 255, 255, 0.1) 0%, 
    rgba(255, 255, 255, 0.05) 30%, 
    transparent 70%);
  animation: glow 4s ease-in-out infinite;
  z-index: 0;
}

.card__sparkle {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.6) 2px, transparent 2px),
    radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.4) 1px, transparent 1px),
    radial-gradient(circle at 60% 30%, rgba(255, 255, 255, 0.3) 1px, transparent 1px);
  animation: sparkle 2s ease-in-out infinite;
  z-index: 1;
}

.bg-gradient {
  background: linear-gradient(90deg, 
    rgba(255, 255, 255, 0.3), 
    rgba(255, 255, 255, 0.8), 
    rgba(255, 255, 255, 0.3));
}

.animated-badge {
  animation: badgePulse 2s ease-in-out infinite;
}

.animated-text {
  animation: textGlow 3s ease-in-out infinite;
}

.animated-number {
  animation: numberPulse 2s ease-in-out infinite;
}

/* Animations */
@keyframes rainbow {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

@keyframes rotate {
  0%, 100% {
    transform: rotateY(-5deg) rotateX(2deg);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  }
  50% {
    transform: rotateY(5deg) rotateX(-2deg);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
  }
}

@keyframes texture {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(-25%); }
}

@keyframes glow {
  0%, 100% { 
    opacity: 0.5; 
    transform: scale(0.8); 
  }
  50% { 
    opacity: 0.8; 
    transform: scale(1.2); 
  }
}

@keyframes sparkle {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

@keyframes textShimmer {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

@keyframes badgePulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

@keyframes textGlow {
  0%, 100% { text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3); }
  50% { text-shadow: 0 0 20px rgba(255, 255, 255, 0.5); }
}

@keyframes numberPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}

@keyframes colorShift {
  0%, 100% { filter: hue-rotate(0deg); }
  50% { filter: hue-rotate(30deg); }
}

/* Dark theme */
@media (prefers-color-scheme: dark) {
  :root {
    --bg: hsl(var(--hue), 10%, 30%);
    --fg: hsl(var(--hue), 10%, 90%);
  }
  
  .card {
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6), 
                0 0 0 1px rgba(255, 255, 255, 0.1);
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .card {
    width: 12em;
    height: 5.5em;
  }
  
  :root {
    font-size: calc(18px + (25 - 18) * (100vw - 320px) / (768 - 320));
  }
}
</style>
