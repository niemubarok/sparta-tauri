# Inisialisasi Project Tauri + Quasar

## Langkah-langkah Inisialisasi

1. **Clone repository ini**
   ```bash
   git clone <repo-url>
   cd tauri
   ```

2. **Install dependencies**
   ```bash
   pnpm install
   ```

3. **Jalankan aplikasi dalam mode development**
   ```bash
   pnpm tauri:dev
   ```

4. **Linting (opsional)**
   ```bash
   pnpm lint
   ```

5. **Build aplikasi**
   - Ubah bundle identifier di `tauri.conf.json > tauri > bundle > identifier` jika diperlukan.
   ```bash
   pnpm tauri:build
   ```

## Prasyarat

- Node.js & pnpm
- Rust edition 2024 atau lebih baru

## Dokumentasi

- [Vite](https://vitejs.dev/)
- [Vue 3](https://vuejs.org/)
- [Quasar](https://quasar.dev/)
- [Tauri](https://tauri.app/)
