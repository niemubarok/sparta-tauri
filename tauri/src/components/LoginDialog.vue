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
            @click="onSubmit"
            :loading="isLoading"
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
import { usePetugasStore } from "src/stores/petugas-store";
import axios from "axios";
import { useRouter } from "vue-router";
import ApiUrlDialog from "./ApiUrlDialog.vue";
import { userStore } from "src/stores/user-store";

const { dialogRef, onDialogHide } = useDialogPluginComponent();
const componentStore = useComponentStore();
const transaksiStore = useTransaksiStore();
const petugasStore = usePetugasStore();

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
const isLoading = ref(false);

defineEmits([...useDialogPluginComponent.emits]);

const onSubmit = async () => {
  if (!username.value || !password.value) {
    $q.notify({
      type: "negative",
      message: "Username dan password harus diisi",
      position: "top",
      timeout: 1000,
    });
    return;
  }

  isLoading.value = true;
  
  try {
    // Ensure petugas data is loaded
    await petugasStore.loadFromLocal();
    
    // If no petugas data exists, seed it
    console.log("🚀 ~ onSubmit ~ petugasStore.daftarPetugas:", petugasStore.daftarPetugas)
    if (petugasStore.daftarPetugas.length === 0) {
      console.log('No petugas data found, seeding...');
      await petugasStore.seedPetugasData();
    }
    
    // Try to authenticate using petugas store (offline first)
    const petugas = await petugasStore.authenticatePetugas(username.value, password.value);
    console.log("🚀 ~ onSubmit ~ petugas:", petugas)
    
    if (petugas) {
      // Determine shift based on current time
      const currentHour = new Date().getHours();
      let currentShift = 'S1'; // Default shift
      
      if (currentHour >= 6 && currentHour < 14) {
        currentShift = 'S1'; // Pagi: 06:00 - 14:00
      } else if (currentHour >= 14 && currentHour < 22) {
        currentShift = 'S2'; // Siang: 14:00 - 22:00
      } else {
        currentShift = 'S3'; // Malam: 22:00 - 06:00
      }

      // Set admin status based on level
      const adminLevels = ["ADM", "SPV", "0001", "0002", "0003"];
      const isAdmin = adminLevels.includes(petugas.level_code);
      
      // Save to localStorage
      ls.set("pegawai", petugas);
      ls.set("shift", currentShift);
      ls.set("timeLogin", new Date().toISOString());
      ls.set("tanggal", new Date().toISOString().split('T')[0]);
      ls.set("isAdmin", isAdmin);
      
      // Set transaksi store admin status
      // transaksiStore.isAdmin = isAdmin;
      
      if (props.type == "login") {
        $q.notify({
          type: "positive",
          message: `Selamat datang, ${petugas.nama}!`,
          position: "top",
          timeout: 2000,
        });
        
        // Hide dialog and reload page
        dialogRef.value.hide();
        setTimeout(() => {
          window.location.reload();
        }, 500);
        
      } else if (props.type === "check" && props.component === "SettingsDialog") {
        if (isAdmin) {
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
            message: "Anda tidak memiliki akses",
            position: "top",
            timeout: 1000,
          });
        }
      }
    } else {
      // If local authentication fails, try online (fallback)
      try {
        const user = await userStore().login(username.value, password.value);
        if (user) {
          if (props.type == "login") {
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
                message: "Anda tidak memiliki akses",
                position: "top",
                timeout: 1000,
              });
            }
          }
        } else {
          throw new Error('Online authentication failed');
        }
      } catch (onlineError) {
        console.log('Online authentication failed:', onlineError);
        $q.notify({
          type: "negative",
          message: "Username atau password salah",
          position: "top",
          timeout: 1000,
        });
      }
    }
  } catch (error) {
    console.error('Authentication error:', error);
    $q.notify({
      type: "negative",
      message: "Terjadi kesalahan saat login",
      position: "top",
      timeout: 1000,
    });
  } finally {
    isLoading.value = false;
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
