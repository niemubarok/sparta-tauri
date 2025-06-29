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
        // Untuk aplikasi Tauri, redirect langsung ke manual-gate
        if (window && window.__TAURI__) {
            route.redirect = '/manual-gate';
        } else {
            route.meta = {
                isSidebar: true,
                isHeader: true,
                requiresAuth: true,
            }
        }
    }

    if (route.path === '/manual-gate') {
        route.meta = {
            isSidebar: false,
            isHeader: false,
            requiresAuth: false,
        }
        route.name = 'manualGate'
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

// Tambahkan route eksplisit untuk manual-gate jika belum ada
const hasManualGateRoute = routes.some(route => route.path === '/manual-gate');
if (!hasManualGateRoute) {
    routes.push({
        path: '/manual-gate',
        name: 'manual-gate',
        component: () => import('../pages/manual-gate.vue'),
        meta: {
            isSidebar: false,
            isHeader: false,
            requiresAuth: false,
        }
    });
}

routes.push({
    path: '/:catchAll(.*)*',
    redirect: window && window.__TAURI__ ? '/manual-gate' : '/',
})

export default route(function(/* { store, ssrContext } */) {
    const routerMode
    = process.env.VUE_ROUTER_MODE === 'history'
        ? createWebHistory
        : createWebHashHistory
    const createHistory = routerMode

    const router = createRouter({
        scrollBehavior: () => ({ left: 0, top: 0 }),
        routes,
        history: createHistory(process.env.VUE_ROUTER_BASE),
    })

    // Router guard untuk aplikasi Tauri - langsung ke manual-gate
    router.beforeEach((to, from, next) => {
        // Jika ini adalah aplikasi Tauri
        if (window && window.__TAURI__) {
            // Jika route adalah root atau halaman lain yang tidak diperlukan, redirect ke manual-gate
            if (to.path === '/' || to.path === '/dashboard' || to.path === '/login') {
                next('/manual-gate')
            } else {
                next()
            }
        } else {
            next()
        }
    })

    return router
})
