# Sistem Member Sparta Parking

Sistem manajemen member untuk aplikasi parkir Sparta yang terintegrasi dengan PouchDB/CouchDB.

## 📋 Fitur

### ✨ Manajemen Member
- ✅ CRUD Member (Create, Read, Update, Delete)
- ✅ CRUD Tipe Membership
- ✅ Validasi nomor polisi dan data member
- ✅ Status membership (Aktif, Akan Berakhir, Kadaluarsa)
- ✅ Multi kendaraan per member
- ✅ Kontak darurat
- ✅ Perpanjangan membership

### 🎫 Integrasi Gate Entry/Exit
- ✅ Lookup member berdasarkan nomor polisi
- ✅ Validasi status membership
- ✅ Perhitungan diskon member otomatis
- ✅ Notifikasi member (selamat datang, diskon, peringatan)
- ✅ Recording aktivitas member

### 💰 Sistem Diskon
- ✅ Diskon berdasarkan kategori member:
  - VIP: 50% diskon
  - Premium: 30% diskon
  - Corporate: 25% diskon
  - Regular: 15% diskon

### 📊 Dashboard & Laporan
- ✅ Widget dashboard member
- ✅ Statistik member (total, aktif, akan berakhir)
- ✅ Notifikasi member yang akan berakhir
- ✅ Laporan pendapatan membership

## 🗄️ Struktur Database

### Members Collection
```javascript
{
  _id: "member_timestamp_random",
  type: "member",
  member_id: "MBR001",
  name: "John Doe",
  email: "john@example.com",
  phone: "081234567890",
  address: "Alamat lengkap",
  identity_number: "KTP/ID number",
  vehicles: [
    {
      type: "Mobil",
      license_plate: "B1234ABC",
      brand: "Toyota",
      model: "Avanza",
      color: "Putih",
      year: "2020"
    }
  ],
  membership_type_id: "membership_type_id",
  start_date: "2024-01-01",
  end_date: "2024-12-31",
  payment_status: "paid", // pending, paid, overdue
  notes: "Catatan tambahan",
  emergency_contact: {
    name: "Contact Name",
    phone: "081234567891",
    relationship: "Hubungan"
  },
  active: 1,
  createdAt: "2024-01-01T00:00:00.000Z",
  updatedAt: "2024-01-01T00:00:00.000Z"
}
```

### Membership Types Collection
```javascript
{
  _id: "membership_type_timestamp_random",
  type: "membership_type",
  name: "Premium Member",
  category: "PREMIUM", // VIP, PREMIUM, REGULAR, CORPORATE
  price: 200000,
  area_type: "residential", // residential, commercial
  max_vehicles: 3,
  operating_hours: {
    start: "00:00",
    end: "23:59"
  },
  duration_months: 12,
  description: "Membership premium dengan fasilitas lengkap",
  facilities: ["CCTV 24 Jam", "Keamanan", "Valet Parking"],
  benefits: ["Diskon 30%", "Priority Access"],
  access_areas: ["main_parking", "premium_area"],
  createdAt: "2024-01-01T00:00:00.000Z",
  updatedAt: "2024-01-01T00:00:00.000Z"
}
```

## 🚀 Setup & Instalasi

### 1. Inisialisasi Database Member

```bash
# Inisialisasi database dengan tipe membership default
npm run member:init

# Inisialisasi dengan data sample
npm run member:init:sample

# Reset database dan buat ulang dengan sample data
npm run member:reset

# Verifikasi setup database
npm run member:verify
```

### 2. Import Components

```javascript
// Di halaman/component yang membutuhkan
import { useMembershipStore } from 'src/stores/membership-store'
import MemberLookupDialog from 'src/components/MemberLookupDialog.vue'
import MemberInputField from 'src/components/MemberInputField.vue'
import MemberWidget from 'src/components/MemberWidget.vue'
```

### 3. Penggunaan di Gate Entry

```vue
<template>
  <div>
    <!-- Input field dengan integrasi member -->
    <MemberInputField
      v-model="selectedMember"
      :plate-number="plateNumber"
      :parking-fee="parkingFee"
      :show-fee-calculation="true"
      @member-selected="onMemberSelected"
      @fee-calculated="onFeeCalculated"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import MemberInputField from 'src/components/MemberInputField.vue'

const selectedMember = ref(null)
const plateNumber = ref('')
const parkingFee = ref(0)

const onMemberSelected = (member) => {
  console.log('Member selected:', member)
  // Handle member selection
}

const onFeeCalculated = (feeCalculation) => {
  console.log('Fee calculation:', feeCalculation)
  // Use calculated fee with discount
  parkingFee.value = feeCalculation.finalFee
}
</script>
```

## 🎯 Integrasi dengan Gate System

### Check Member Status
```javascript
import { memberGateIntegration } from 'src/utils/member-gate-integration'

// Check member berdasarkan nomor polisi
const member = await memberGateIntegration.checkMemberStatus('B1234ABC')

if (member && member.canPark) {
  console.log(`Welcome ${member.name}!`)
  console.log(`Discount: ${member.discountPercentage}%`)
}
```

### Calculate Member Fee
```javascript
const baseFee = 10000
const feeCalculation = memberGateIntegration.calculateMemberFee(baseFee, member)

console.log(`Original: ${feeCalculation.originalFee}`)
console.log(`Discount: ${feeCalculation.discountAmount}`)
console.log(`Final: ${feeCalculation.finalFee}`)
```

### Record Member Activity
```javascript
await memberGateIntegration.recordMemberActivity(
  member,
  'B1234ABC',
  'entry',
  {
    gateId: 'gate_01',
    location: 'main_entrance',
    operator: 'operator_name'
  }
)
```

## 📱 Komponen UI

### 1. MemberLookupDialog
Dialog untuk mencari dan memilih member.

**Props:**
- `initialSearch`: String - Pencarian awal
  
**Events:**
- `memberSelected`: Member yang dipilih
- `memberRenewed`: Member yang diperpanjang

### 2. MemberInputField
Input field dengan integrasi lookup member dan kalkulasi fee.

**Props:**
- `modelValue`: Object - Member yang dipilih
- `plateNumber`: String - Nomor polisi
- `parkingFee`: Number - Biaya parkir
- `showFeeCalculation`: Boolean - Tampilkan kalkulasi fee
- `readonly`: Boolean - Read-only mode

**Events:**
- `memberSelected`: Member dipilih
- `memberCleared`: Member dihapus
- `feeCalculated`: Fee dikalkulasi dengan diskon

### 3. MemberWidget
Widget dashboard untuk overview member.

**Events:**
- `viewExpiring`: Lihat member yang akan berakhir
- `manageMembers`: Kelola member
- `addMember`: Tambah member baru
- `memberChecked`: Member dicek melalui widget

## 🔧 API Reference

### MembershipStore

```javascript
const membershipStore = useMembershipStore()

// Load data
await membershipStore.loadMembers()
await membershipStore.loadMembershipTypes()

// Add member
await membershipStore.addMember(memberData)

// Update member
await membershipStore.updateMember(id, memberData)

// Check membership
const member = await membershipStore.checkMembership('B1234ABC')

// Renew membership
await membershipStore.renewMembership(id, months)

// Generate member ID
const memberId = await membershipStore.generateMemberId()
```

### Member Gate Integration

```javascript
import { memberGateIntegration } from 'src/utils/member-gate-integration'

// Status check
const member = await memberGateIntegration.checkMemberStatus(plateNumber)

// Fee calculation
const feeCalc = memberGateIntegration.calculateMemberFee(baseFee, member)

// Activity recording
await memberGateIntegration.recordMemberActivity(member, plate, action, gateInfo)

// Validate vehicle access
const validation = memberGateIntegration.validateVehicleAccess(member, vehicleType)

// Get member privileges
const privileges = memberGateIntegration.getMemberPrivileges(member)
```

## 📈 Monitoring & Maintenance

### Database Health Check
```bash
npm run member:verify
```

### Backup Member Data
```javascript
const backup = await membershipStore.backupMembersData()
// Save backup data
```

### Restore Member Data
```javascript
await membershipStore.restoreMembersData(backupData)
```

## 🐛 Troubleshooting

### Common Issues

1. **Member tidak ditemukan**
   - Pastikan nomor polisi ditulis dengan benar
   - Check status aktif member
   - Verifikasi data di database

2. **Diskon tidak terapply**
   - Pastikan member aktif dan tidak expired
   - Check kategori membership
   - Verifikasi konfigurasi diskon

3. **Database connection error**
   - Check PouchDB/CouchDB connection
   - Verify database initialization
   - Run `npm run member:verify`

### Debug Mode
```javascript
// Enable debug logging
localStorage.setItem('member_debug', 'true')

// Check console for detailed logs
console.log(membershipStore.members)
console.log(membershipStore.statistics)
```

## 📝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

Private - Sparta Parking System

---

**Sparta Parking System** - Member Management Module
Version 1.0.0 - Built with ❤️ using Vue 3 + Quasar + PouchDB
