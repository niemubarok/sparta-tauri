# Sparta Parking System - Codebase Documentation

## Project Overview
Sparta Parking System is a Tauri-based desktop application for managing parking operations, built with Vue.js and PouchDB for offline-first data management.

## Tech Stack
- **Frontend**: Vue 3 + Quasar Framework
- **Desktop Runtime**: Tauri
- **Database**: PouchDB (with CouchDB sync support)
- **Languages**: TypeScript, JavaScript, Rust (Tauri backend)

## Core Features
1. **Parking Management**
   - Entry/Exit gate control
   - Vehicle tracking
   - Payment processing
   - Member management

2. **ALPR Integration**
   - Automatic License Plate Recognition
   - Camera management
   - Real-time plate detection

3. **Payment Systems**
   - Prepaid mode (pay at entry)
   - Postpaid mode (pay at exit)
   - Member billing

4. **Sync System**
   - Offline-first architecture
   - Real-time sync with central server
   - Fallback mechanisms

## Project Structure

### Root Directory
```
├── src/                  # Main source code
├── src-tauri/           # Tauri backend code
├── public/              # Static assets
├── scripts/             # Database and utility scripts
└── docs/               # Documentation files
```

### Source Code Organization

#### `src/`
- **components/**: Vue components
  - `Camera.vue`: Camera handling
  - `PaymentDialog.vue`: Payment processing
  - `ManualEntryGate.vue`: Manual entry interface
  
- **stores/**: Pinia stores
  - `transaksi-store.ts`: Transaction management
  - `kendaraan-store.ts`: Vehicle data
  - `component-store.js`: UI state management

- **boot/**: Application initialization
  - `pouchdb.ts`: Database setup and sync
  - `axios.ts`: API client setup

#### `scripts/`
- Database initialization scripts
- View creation and updates
- Member database management

## Key Components

### 1. Database Design
PouchDB is used with multiple design documents for efficient querying:

```javascript
_design/members
├── by_member_id
├── by_license_plate
├── by_phone
└── by_status

_design/transaksi
├── by_date
├── out_by_date
└── by_no_pol
```

### 2. Sync System
The application implements a robust sync system with:
- Immediate sync for critical operations
- Fallback mechanisms for sync failures
- Extended timeouts for reliability
- Real-time sync status monitoring

### 3. UI Components
- **ManualEntryGate**: Main interface for entry operations
- **PaymentDialog**: Handles payment processing
- **Camera Integration**: ALPR and manual capture support

## Development Guidelines

### 1. Database Operations
- Always use design documents for queries
- Implement proper error handling
- Use immediate sync for critical transactions

### 2. Component Development
- Follow Vue 3 Composition API patterns
- Use Pinia for state management
- Implement proper type definitions

### 3. Error Handling
- Implement comprehensive error catching
- Use fallback mechanisms
- Provide user feedback

## Customization Points

### 1. Payment Configuration
- Tariff settings in `kendaraan-store.ts`
- Payment mode toggles in components

### 2. Camera Setup
- ALPR configuration in camera components
- Device selection in settings

### 3. Sync Settings
- Timeout configurations
- Sync intervals
- Server endpoints

## Troubleshooting

Common issues and solutions are documented in:
- `SYNC_TROUBLESHOOTING.md`
- `SYNC_IMPROVEMENT_DOCUMENTATION.md`
- `TIMEOUT_SYNC_FIX_DOCUMENTATION.md`

## Testing

### Manual Testing Points
1. Entry/Exit gate operations
2. Payment processing
3. Sync functionality
4. Member management
5. Camera operations

### Integration Points
- ALPR system integration
- Payment gateway integration
- Central server sync
- Printer integration

## Future Considerations
1. Enhanced sync reliability
2. Additional payment methods
3. Advanced reporting features
4. Multi-location support
