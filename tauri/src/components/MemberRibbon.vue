<template>
  <div class="ribbon ribbon-top-right z-top">
    <span
      :class="membershipStore.isExpired(endDate) ? 'bg-red-10 text-white' : ''"
      >{{ membershipStore.isExpired(endDate) ? "Expired" : "Member" }}</span
    >
  </div>
</template>

<script setup>
import { useMembershipStore } from "src/stores/membership-store";

const propt= defineProps({
  // nama: String,
  // jenisMember: String,
  endDate: String,
  // isExpired: Boolean,
});

const membershipStore = useMembershipStore();
</script>

<style scoped>
.ribbon {
  width: 150px;
  height: 150px;
  overflow: hidden;
  position: absolute;
}
.ribbon::before,
.ribbon::after {
  position: absolute;
  z-index: -1;
  content: "";
  display: block;
  border: 5px solid #2980b9;
}
.ribbon span {
  position: absolute;
  display: block;
  width: 225px;
  padding: 15px 0;
  background-color: #ffd700;
  box-shadow: 0 5px 10px rgba(0, 0, 0, 0.1);
  color: #070707;
  font: 700 18px/1 "Courier Prime", sans-serif;
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.2);
  text-transform: uppercase;
  text-align: center;
}

/* top left*/
.ribbon-top-left {
  top: -10px;
  left: -10px;
}
.ribbon-top-left::before,
.ribbon-top-left::after {
  border-top-color: transparent;
  border-left-color: transparent;
}
.ribbon-top-left::before {
  top: 0;
  right: 0;
}
.ribbon-top-left::after {
  bottom: 0;
  left: 0;
}
.ribbon-top-left span {
  right: -25px;
  top: 30px;
  transform: rotate(-45deg);
}

/* top right*/
.ribbon-top-right {
  top: -10px;
  right: -10px;
}
.ribbon-top-right::before,
.ribbon-top-right::after {
  border-top-color: transparent;
  border-right-color: transparent;
}
.ribbon-top-right::before {
  top: 0;
  left: 0;
}
.ribbon-top-right::after {
  bottom: 0;
  right: 0;
}
.ribbon-top-right span {
  left: -25px;
  top: 30px;
  transform: rotate(45deg);
}
</style>
