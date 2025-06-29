# EXIT GATE CCTV CAMERA IMPLEMENTATION

## Summary
Successfully implemented CCTV camera functionality in exit-gate system to capture images when barcode is scanned and save them as `exit_pic` in the database.

## Changes Made

### 1. **Backend Camera Handler**
- **File**: `exit-gate/src-tauri/src/command/camera_handler.rs`
- **Functionality**: HTTP snapshot capture from CCTV cameras
- **Method**: Uses reqwest to fetch JPEG images from camera snapshot endpoints
- **Benefits**: No FFmpeg dependency, simpler than RTSP streaming

### 2. **Dependencies Updated**
- **File**: `exit-gate/src-tauri/Cargo.toml`
- **Added**: `base64`, `chrono`, `reqwest` for camera functionality
- **Updated**: `lib.rs` to include camera handler in invoke commands

### 3. **Camera Component**
- **File**: `exit-gate/src/components/Camera.vue`
- **Functionality**: Vue component for CCTV camera display and image capture
- **Features**: 
  - Snapshot-based image capture
  - Error handling and retry logic
  - Integration with Tauri backend

### 4. **Database Schema Updates**
- **File**: `exit-gate/src/services/database.ts`
- **Added camera settings**:
  - `plate_camera_ip`, `plate_camera_username`, `plate_camera_password`
  - `driver_camera_ip`, `driver_camera_username`, `driver_camera_password`
  - `plate_camera_snapshot_path`, `driver_camera_snapshot_path`
- **Default values**: Pre-configured for common CCTV cameras

### 5. **Exit Gate UI Integration**
- **File**: `exit-gate/src/pages/exit-gate.vue`
- **Features**:
  - CCTV camera preview displays
  - Automatic image capture when barcode is scanned
  - Settings loaded from database
  - `exit_pic` field populated with base64 image data

## Camera Configuration

### Default Settings
```typescript
plate_camera_ip: '192.168.1.100'
plate_camera_username: 'admin'
plate_camera_password: 'admin123'
plate_camera_snapshot_path: 'Streaming/Channels/1/picture'

driver_camera_ip: '192.168.1.101'
driver_camera_username: 'admin'
driver_camera_password: 'admin123'
driver_camera_snapshot_path: 'Streaming/Channels/1/picture'
```

### Snapshot URL Format
- HTTP-based snapshot capture
- Format: `http://username:password@ip_address/snapshot_path`
- Example: `http://admin:admin123@192.168.1.100/Streaming/Channels/1/picture`

## Image Capture Workflow

1. **Barcode Scanned** → `handleBarcodeScanned()`
2. **Transaction Found** → `processExit()`
3. **Images Captured** → `captureExitImages()`
4. **Image Saved** → `exit_pic` field in database
5. **Gate Opened** → Vehicle exit completed

## Features Implemented

✅ **CCTV Camera Integration**: Both plate and driver cameras  
✅ **Snapshot Capture**: HTTP-based image capture  
✅ **Database Storage**: Images saved as base64 in `exit_pic` field  
✅ **Error Handling**: Graceful fallback if cameras fail  
✅ **Settings Management**: Camera configuration from database  
✅ **Auto Capture**: Images captured automatically on barcode scan  
✅ **CORS Solution**: Uses Tauri backend to bypass browser CORS restrictions

## CORS Issue Resolution

### Problem
Browser CORS policy blocks direct HTTP requests to CCTV cameras:
```
Access to fetch at 'http://192.168.1.11/snapshot' from origin 'http://localhost:1421' has been blocked by CORS policy
```

### Solution
Use Tauri backend (`capture_cctv_image` command) instead of frontend fetch:

**❌ Frontend Direct Fetch (Blocked by CORS):**
```typescript
const response = await fetch('http://192.168.1.11/snapshot')
```

**✅ Tauri Backend Request (Bypasses CORS):**
```typescript
const response = await invoke('capture_cctv_image', {
  username: 'admin',
  password: 'admin123', 
  ip_address: '192.168.1.11',
  snapshot_path: 'snapshot'
})
```

### Implementation Details
- **Frontend**: `camera-service.ts` uses `invoke()` instead of `fetch()`
- **Backend**: `camera_handler.rs` makes HTTP requests using `reqwest`
- **No CORS**: Tauri backend is not subject to browser CORS restrictions  

## Testing

### Camera Test URLs
Test these URLs in browser to verify camera accessibility:
- Plate Camera: `http://admin:admin123@192.168.1.100/Streaming/Channels/1/picture`
- Driver Camera: `http://admin:admin123@192.168.1.101/Streaming/Channels/1/picture`

### Troubleshooting
1. **No Image Captured**: Check IP address, credentials, and snapshot path
2. **Connection Timeout**: Verify camera is accessible on network
3. **Invalid Image**: Ensure snapshot endpoint returns JPEG format
4. **Database Error**: Check if `exit_pic` field exists in transaction schema

## Next Steps
1. **Configuration UI**: Add settings page for camera configuration
2. **Image Compression**: Implement image compression for storage efficiency
3. **Retry Logic**: Enhanced error recovery for camera failures
4. **Multiple Formats**: Support for PNG and other image formats
