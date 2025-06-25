import { route } from 'quasar/wrappers'
import {
    createMemoryHistory,
    createRouter,
    createWebHashHistory,
    createWebHistory,
} from 'vue-router'

// import ls from 'localstorage-slim'
declare global {
    interface Window { __TAURI__: any; }
}
import { setupLayouts } from 'virtual:generated-layouts'
import generatedRoutes from 'virtual:generated-pages'

const routes = setupLayouts(generatedRoutes)

// Add meta to specific routes
routes.forEach(route => {
    if (route.path === '/') {
        route.meta = {
            isSidebar: window && window.__TAURI__ ? false : true,
            isHeader: window && window.__TAURI__ ? false : true,
            requiresAuth: true,
        }

    // route.name = 'outgate'
    // route.component = async () => {
    //     // Logika pemilihan komponen berdasarkan gateType akan ditangani di App.vue atau komponen layout utama
    //     // if (window && window.__TAURI__) {
    //     //     // Contoh: const settings = await getGateSettings();
    //     //     // if (settings.gateType === 'exit') {
    //     //     //     return import("../pages/ExitGatePage.vue")
    //     //     // }
    //     //     // return import("../pages/EntryGate.vue")
    //     // } else {
    //     //     return import("../pages/LaporanTransaksiPerHari.vue")
    //     // }
    // }
    }

    if (route.path === '/dashboard') {
        route.meta = {
            isSidebar: true,
            isHeader: true,
            requiresAuth: true,
        }
        route.name = 'dashboard'
    }

    if (route.path === '/daftar-transaksi') {
        route.meta = {
            isSidebar: true,
            isHeader: true,
            requiresAuth: true,
        }
        route.name = 'daftarTransaksi'
    }

    if (route.path === '/transaksi/create') {
        route.meta = {
            isSidebar: false,
            isHeader: false,
            requiresAuth: true,
        }
        route.name = 'createTransaksi'
    }

    if (route.path === '/petugas') {
        route.meta = {
            isSidebar: true,
            isHeader: true,
            requiresAuth: true,
        }
        route.name = 'petugas'
    }

    if (route.path === '/kendaraan') {
        route.meta = {
            isSidebar: true,
            isHeader: true,
            requiresAuth: true,
        }
        route.name = 'kendaraan'
    }

    if (route.path === '/entry-gate') {
        route.meta = {
            isSidebar: false,
            isHeader: false,
            requiresAuth: false,
        }

    // route.name = 'entry-gate'
    // route.component = async ()=>{
    //     return import("src/pages/EntryGate.vue")
    // }
    }
    if (route.path === '/exit-gate') {
        route.meta = {
            isSidebar: false,
            isHeader: false,
            requiresAuth: false,
        }

    // route.name = 'exit-gate'
    // route.component = async ()=>{
    //     return import("src/pages/ExitGate.vue")
    // }
    }

    if (route.path === '/alpr-manager') {
        route.meta = {
            isSidebar: true,
            isHeader: true,
            requiresAuth: true,
        }
        route.name = 'alprManager'
    }

    if (route.path === '/kendaraan') {
        route.meta = {
            isSidebar: true,
            isHeader: true,
            requiresAuth: true,
        }
        route.name = 'kendaraan'
    }

    // if (route.path === '/tarif') {
    //     route.meta = {
    //         isSidebar: true,
    //         isHeader: true,
    //         requiresAuth: true,
    //     }
    //     route.name = 'tarif'
    // }
})

routes.push({
    path: '/:catchAll(.*)*',
    redirect: '/',
})

export default route(function(/* { store, ssrContext } */) {
    const routerMode
    = process.env.VUE_ROUTER_MODE === 'history'
        ? createWebHistory
        : createWebHashHistory
    const createHistory = routerMode

    return createRouter({
        scrollBehavior: () => ({ left: 0, top: 0 }),
        routes,
        history: createHistory(process.env.VUE_ROUTER_BASE),
    })
})
