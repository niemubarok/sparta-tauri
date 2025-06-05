<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide" persistent>
    <q-card
      class="q-px-md q-pt-sm glass relative"
      style="width: 500px; height: fit-content"
    >
      <q-card-section>
        <q-input
          v-model="username"
          label="Username"
          dense
          outlined
          autofocus
          autocomplete="off"
          @keydown.enter="passwordInput.focus()"
        ></q-input>
        <q-input
          ref="passwordInput"
          v-model="password"
          label="Password"
          dense
          outlined
          type="password"
          class="q-mt-md"
          autocomplete="new-password"
          @keydown.enter="onSubmit"
        ></q-input>
        <q-card-actions align="right">
          <q-btn
            push
            icon="keyboard_return"
            type="submit"
            color="primary"
            class="q-pa-xl"
          />
        </q-card-actions>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { useDialogPluginComponent, useQuasar } from "quasar";
// import SuccessCheckMark from "./SuccessCheckMark.vue";
import { onMounted, onBeforeUnmount, onBeforeMount, ref } from "vue";
import { useComponentStore } from "src/stores/component-store";
import SettingsDialog from "src/components/SettingsDialog.vue";
import ls from "localstorage-slim";
import { useTransaksiStore } from "src/stores/transaksi-store";
import axios from "axios";
import { useRouter } from "vue-router";
import ApiUrlDialog from "./ApiUrlDialog.vue";
import { userStore } from "src/stores/user-store";

const { dialogRef, onDialogHide } = useDialogPluginComponent();
const componentStore = useComponentStore();
const transaksiStore = useTransaksiStore();

const router = useRouter();
const $q = useQuasar();
const props = defineProps({
  type: String,
  url: String,
  component: String,
});

const username = ref("");
const password = ref("");
const shift = ref("S1");
const passwordInput = ref(null);

defineEmits([...useDialogPluginComponent.emits]);

const onSubmit = async () => {
  const user = await userStore().login(username.value, password.value);
  console.log(user);
  if (user) {
    if (props.type == "login") {
      // determineShift();
      ls.set("pegawai", user);
      window.location.reload();
    } else if (props.type === "check" && props.component === "SettingsDialog") {
      if (transaksiStore.isAdmin) {
        const SettingDialog = $q.dialog({
          component: SettingsDialog,
          persistent: true,
          noEscDismiss: true,
        });

        SettingDialog.update();
        dialogRef.value.hide();
      } else {
        $q.notify({
          type: "negative",
          message: "Anda tidak memilik akses",
          position: "top",
          timeout: 1000,
        });
      }
    }
  } else {
    $q.notify({
      type: "negative",
      message: "Cek kembali username dan password anda",
      position: "top",
      timeout: 1000,
    });
  }
};

const handleKeyDownOnLoginDialog = async (event) => {
  if (event.key === "Escape") {
    event.preventDefault();
    dialogRef.value.hide();
  }
};

onMounted(() => {
  window.addEventListener("keydown", handleKeyDownOnLoginDialog);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleKeyDownOnLoginDialog);
});
</script>

<style scoped>
.glass {
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  background-color: rgba(255, 255, 255, 0.378);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.125);
}

:deep(.q-dialog__backdrop.fixed-full) {
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
}
</style>
