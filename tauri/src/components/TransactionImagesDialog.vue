<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide" maximized>
    <q-card class="column">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Gambar CCTV - Transaksi {{ transactionId }}</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <q-card-section class="col">
        <div v-if="loading" class="flex flex-center">
          <q-spinner size="50px" />
          <div class="q-ml-md">Memuat gambar...</div>
        </div>
        
        <div v-else class="row q-gutter-md">
          <!-- Gambar Masuk -->
          <div class="col-12 col-md-6">
            <q-card>
              <q-card-section>
                <div class="text-h6 text-center">📷 Gambar Masuk</div>
              </q-card-section>
              
              <q-card-section class="q-pa-none">
                <div class="row">
                  <!-- Kamera Plat Masuk -->
                  <div class="col-6">
                    <div class="text-subtitle2 text-center q-pa-sm bg-grey-3">
                      🚗 Kamera Plat Nomor
                    </div>
                    <div v-if="images.plateEntrance" class="image-container">
                      <q-img 
                        :src="images.plateEntrance" 
                        fit="contain"
                        class="cursor-pointer"
                        @click="showImageModal(images.plateEntrance, 'Plat Nomor - Masuk')"
                      >
                        <template v-slot:error>
                          <div class="absolute-full flex flex-center bg-grey-3 text-grey-7">
                            Gambar tidak dapat dimuat
                          </div>
                        </template>
                      </q-img>
                    </div>
                    <div v-else class="image-placeholder">
                      <q-icon name="no_photography" size="50px" color="grey-5" />
                      <div class="text-grey-5">Tidak ada gambar</div>
                    </div>
                  </div>

                  <!-- Kamera Driver Masuk -->
                  <div class="col-6">
                    <div class="text-subtitle2 text-center q-pa-sm bg-grey-3">
                      👤 Kamera Driver
                    </div>
                    <div v-if="images.driverEntrance" class="image-container">
                      <q-img 
                        :src="images.driverEntrance" 
                        fit="contain"
                        class="cursor-pointer"
                        @click="showImageModal(images.driverEntrance, 'Driver - Masuk')"
                      >
                        <template v-slot:error>
                          <div class="absolute-full flex flex-center bg-grey-3 text-grey-7">
                            Gambar tidak dapat dimuat
                          </div>
                        </template>
                      </q-img>
                    </div>
                    <div v-else class="image-placeholder">
                      <q-icon name="no_photography" size="50px" color="grey-5" />
                      <div class="text-grey-5">Tidak ada gambar</div>
                    </div>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Gambar Keluar -->
          <div class="col-12 col-md-6">
            <q-card>
              <q-card-section>
                <div class="text-h6 text-center">📷 Gambar Keluar</div>
              </q-card-section>
              
              <q-card-section class="q-pa-none">
                <div class="row">
                  <!-- Kamera Plat Keluar -->
                  <div class="col-6">
                    <div class="text-subtitle2 text-center q-pa-sm bg-grey-3">
                      🚗 Kamera Plat Nomor
                    </div>
                    <div v-if="images.plateExit" class="image-container">
                      <q-img 
                        :src="images.plateExit" 
                        fit="contain"
                        class="cursor-pointer"
                        @click="showImageModal(images.plateExit, 'Plat Nomor - Keluar')"
                      >
                        <template v-slot:error>
                          <div class="absolute-full flex flex-center bg-grey-3 text-grey-7">
                            Gambar tidak dapat dimuat
                          </div>
                        </template>
                      </q-img>
                    </div>
                    <div v-else class="image-placeholder">
                      <q-icon name="no_photography" size="50px" color="grey-5" />
                      <div class="text-grey-5">Tidak ada gambar</div>
                    </div>
                  </div>

                  <!-- Kamera Driver Keluar -->
                  <div class="col-6">
                    <div class="text-subtitle2 text-center q-pa-sm bg-grey-3">
                      👤 Kamera Driver
                    </div>
                    <div v-if="images.driverExit" class="image-container">
                      <q-img 
                        :src="images.driverExit" 
                        fit="contain"
                        class="cursor-pointer"
                        @click="showImageModal(images.driverExit, 'Driver - Keluar')"
                      >
                        <template v-slot:error>
                          <div class="absolute-full flex flex-center bg-grey-3 text-grey-7">
                            Gambar tidak dapat dimuat
                          </div>
                        </template>
                      </q-img>
                    </div>
                    <div v-else class="image-placeholder">
                      <q-icon name="no_photography" size="50px" color="grey-5" />
                      <div class="text-grey-5">Tidak ada gambar</div>
                    </div>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Tutup" color="primary" v-close-popup />
      </q-card-actions>
    </q-card>

    <!-- Modal untuk melihat gambar full size -->
    <q-dialog v-model="imageModal" maximized>
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">{{ modalImageTitle }}</div>
          <q-space />
          <q-btn icon="close" flat round dense @click="imageModal = false" />
        </q-card-section>
        
        <q-card-section class="flex flex-center">
          <q-img 
            :src="modalImageSrc" 
            fit="contain"
            style="max-height: 80vh; max-width: 100%;"
          />
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useDialogPluginComponent, useQuasar } from 'quasar';
import { useTransaksiStore } from 'src/stores/transaksi-store';

const props = defineProps({
  transactionId: {
    type: String,
    required: true
  }
});

const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent();
const transaksiStore = useTransaksiStore();
const $q = useQuasar();

const loading = ref(true);
const images = ref({
  plateEntrance: null,
  driverEntrance: null,
  plateExit: null,
  driverExit: null
});

const imageModal = ref(false);
const modalImageSrc = ref('');
const modalImageTitle = ref('');

const loadImages = async () => {
  try {
    loading.value = true;
    const attachments = await transaksiStore.getTransactionAttachments(props.transactionId);
    images.value = attachments;
    
    console.log('📸 Loaded transaction images:', attachments);
  } catch (error) {
    console.error('❌ Error loading transaction images:', error);
    $q.notify({
      type: 'negative',
      message: 'Gagal memuat gambar transaksi',
      position: 'top'
    });
  } finally {
    loading.value = false;
  }
};

const showImageModal = (imageSrc, title) => {
  modalImageSrc.value = imageSrc;
  modalImageTitle.value = title;
  imageModal.value = true;
};

onMounted(() => {
  loadImages();
});

defineEmits([
  ...useDialogPluginComponent.emits
]);
</script>

<style scoped>
.image-container {
  height: 200px;
  border: 1px solid #e0e0e0;
}

.image-placeholder {
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px solid #e0e0e0;
  background-color: #f5f5f5;
}

.cursor-pointer {
  cursor: pointer;
}

.cursor-pointer:hover {
  opacity: 0.8;
}
</style>
