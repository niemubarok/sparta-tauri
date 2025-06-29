# Exit Gate System

A Tauri + Quasar application for managing parking exit gates, designed for Raspberry Pi deployment.

## Features

### Core Functionality
- **USB Barcode Scanner Integration**: Accepts input from USB barcode scanners
- **Transaction Validation**: Checks PouchDB for active parking transactions
- **Gate Control**: Serial communication with gate hardware
- **Automatic Processing**: Seamless exit processing and database updates

### Hardware Integration
- **Serial Port Communication**: Controls gate hardware via serial commands
- **USB Barcode Scanner**: Plug-and-play barcode scanner support
- **Raspberry Pi Optimized**: Lightweight and efficient for embedded systems

### Database Features
- **PouchDB Integration**: Local-first database with sync capabilities
- **Transaction Management**: Compatible with entry gate system schema
- **Real-time Statistics**: Daily exit counts and revenue tracking

## Installation & Usage

See the full documentation below for detailed setup instructions, configuration, and troubleshooting.

## Quick start

Note: Need to **Rust edition 2024 Release** or later.

### Install the dependencies

```bash
pnpm install
```

### Start the app in development mode

```bash
pnpm tauri:dev
```

### Lint the files

```bash
pnpm lint
```

### Build the app

Change the bundle identifier in `tauri.conf.json > tauri > bundle > identifier`, then

```bash
pnpm tauri:build
```
## Preview

![preview.png](preview.png)

## Customize the configuration

https://vitejs.dev/

https://vuejs.org/

https://quasar.dev/

https://tauri.app/
