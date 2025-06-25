<template>
  <q-page class="q-pa-md">
    <div class="row">
      <div class="col-12">
        <div class="flex items-center justify-between q-my-md">
          <h4 class="q-my-none">
            <q-icon name="admin_panel_settings" class="q-mr-sm" />
            Administration Panel
          </h4>
          <div class="q-gutter-sm">
            <q-btn
              color="secondary"
              icon="person"
              label="Petugas"
              outline
              @click="$router.push('/petugas')"
            />
            <q-btn
              color="orange"
              icon="directions_car"
              label="Kendaraan"
              outline
              @click="$router.push('/kendaraan')"
            />
            <q-btn
              color="primary"
              icon="home"
              label="Home"
              @click="$router.push('/')"
            />
          </div>
        </div>
        <q-separator class="q-mb-md" />
      </div>
    </div>

    <div class="row">
      <div class="col-12">
        <!-- Seed Data Section -->
        <AdminSeedData />
        
        <!-- System Statistics -->
        <div class="q-mt-md">
          <SystemStatistics />
        </div>
        
        <!-- Validation Demo -->
        <div class="q-mt-md">
          <PetugasValidationDemo />
        </div>
        
        <!-- System Information -->
        <q-card class="q-mt-md">
          <q-card-section>
            <div class="text-h6 q-mb-md">
              <q-icon name="settings" class="q-mr-sm" />
              System Information
            </div>
            
            <q-list bordered separator>
              <q-item>
                <q-item-section>
                  <q-item-label>Application Version</q-item-label>
                  <q-item-label caption>Sparta Parking System v1.0.0</q-item-label>
                </q-item-section>
              </q-item>
              
              <q-item>
                <q-item-section>
                  <q-item-label>Database Status</q-item-label>
                  <q-item-label caption>PouchDB - Local Storage Active</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-icon name="circle" color="green" />
                </q-item-section>
              </q-item>
              
              <q-item>
                <q-item-section>
                  <q-item-label>Framework</q-item-label>
                  <q-item-label caption>Quasar + Vue 3 + TypeScript + Tauri</q-item-label>
                </q-item-section>
              </q-item>
              
              <q-item>
                <q-item-section>
                  <q-item-label>Features</q-item-label>
                  <q-item-label caption>ALPR, Manual Entry, Blacklist, Multi-level Access</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
          </div>
        </div>
      </q-page>
    </template>
<script setup>
import PetugasValidationDemo from 'src/components/PetugasValidationDemo.vue';
import { onMounted } from 'vue';
import AdminSeedData from 'src/components/AdminSeedData.vue';
import SystemStatistics from 'src/components/SystemStatistics.vue';
import { usePetugasStore } from 'src/stores/petugas-store';
import { useKendaraanStore } from 'src/stores/kendaraan-store';

const petugasStore = usePetugasStore();
const kendaraanStore = useKendaraanStore();

onMounted(async () => {
  // Load data for statistics display
  await petugasStore.loadFromLocal();
  await kendaraanStore.loadJenisKendaraanFromLocal();
  await kendaraanStore.getAllBlacklist();
});
</script>
