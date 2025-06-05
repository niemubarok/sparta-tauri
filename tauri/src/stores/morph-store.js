import { defineStore } from "pinia";
import { ref } from "vue";

export const useMorphStore = defineStore("morph", {
  state: () => ({
    nextCarMorphStep: ref({
      btn: "ticket",
      ticket: "btn",
      //   payment: "btn",
    }),
    morphCarModel: ref("btn"),
    nextBikeMorphStep: ref({
      btn: "tiket",
      tiket: "btn",
      //   payment: "btn",
    }),
    morphBikeModel: ref("btn"),
    nextBusMorphStep: ref({
      btn: "struk",
      struk: "btn",
      //   payment: "btn",
    }),
    morphBusModel: ref("btn"),
  }),

  actions: {
    nextBikeMorph() {
      console.log(this.morphBikeModel);
      this.morphBikeModel = this.nextBikeMorphStep[this.morphBikeModel];
    },
    nextCarMorph() {
      console.log(this.morphCarModel);
      this.morphCarModel = this.nextCarMorphStep[this.morphCarModel];
    },
    nextBusMorph() {
      console.log(this.morphBusModel);
      this.morphBusModel = this.nextBusMorphStep[this.morphBusModel];
    },
  },
});
