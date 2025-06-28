# CCTV Connection Fix

## Problem Solved
Fixed the CCTV connection issue where cameras were not displaying and test capture was failing.

## Root Cause
**Parameter Mismatch** between Frontend (Camera.vue) and Backend (Rust camera_handler.rs):

- **Frontend** was sending: `{ args: { ipAddress, rtspStreamPath } }`
- **Backend** was expecting: `{ ip_address, rtsp_stream_path }`

## Solutions Applied

### 1. Fixed Rust Parameter Structure
**File**: `src-tauri/src/command/camera_handler.rs`

```rust
// Changed from camelCase to snake_case
#[derive(Deserialize)]
#[serde(rename_all = "snake_case")] // Was: camelCase
pub struct CaptureCctvImageArgs {
    username: Option<String>,
    password: Option<String>,
    ip_address: String,        // Frontend sends this
    rtsp_stream_path: String,  // Frontend sends this
}
```

### 2. Fixed Frontend Parameter Sending
**File**: `src/components/Camera.vue`

```javascript
// Fixed fetchCameraImage function
const args = {
    username: props.username || null,
    password: props.password || null,
    ip_address: props.ipAddress,        // Match Rust expectation
    rtsp_stream_path: props.rtspStreamPath, // Match Rust expectation
};

// Send directly, not wrapped in { args: ... }
const response = await invoke('capture_cctv_image', args);
```

### 3. Added Enhanced Logging
**Backend logging**:
```rust
println!("📸 Capture CCTV Image called with args: ip={}, user={}, rtsp_path={}", 
         args.ip_address, 
         args.username.as_deref().unwrap_or("None"), 
         args.rtsp_stream_path);
```

**Frontend logging**:
```javascript
console.log('📸 Capturing CCTV image with config:', {
    ...args,
    password: args.password ? '***' : null
});
```

### 4. Improved Test Connection Function
Enhanced test in `manual-gate.vue` to show more detailed information:
- RTSP paths for each camera
- Detailed error messages
- Better status indicators

## How to Debug CCTV Issues

### 1. Check Browser Console
Look for these logs:
```
📸 Capturing CCTV image with config: { ip_address: "192.168.1.11", username: "admin", ... }
```

### 2. Check Tauri Console (Terminal)
Look for these logs:
```
📸 Capture CCTV Image called with args: ip=192.168.1.11, user=admin, rtsp_path=Streaming/Channels/101
🔗 Constructed RTSP URL: rtsp://admin:***@192.168.1.11:554/Streaming/Channels/101
🎬 Using FFmpeg at: ../../scripts/ffmpeg/ffmpeg.exe
✅ Successfully captured CCTV image. Size: 12345 bytes
```

### 3. Test Settings Configuration
In manual-gate.vue, use admin tools:
- **Test Koneksi** button - Tests both cameras
- **Test Capture** button - Tests image capture
- **Reload Config** button - Reloads camera configuration

### 4. Common RTSP URL Issues
**Format**: `rtsp://username:password@ip:554/path`

**Common errors**:
- Wrong credentials → "Invalid data found when processing input"
- Wrong IP → Connection timeout
- Wrong RTSP path → "Invalid data found when processing input"
- Camera not supporting RTSP → Connection refused

### 5. Settings Dialog Verification
Check in Settings (F7) → Camera Settings:
- **CCTV IP Address**: Must be reachable camera IP
- **CCTV Username/Password**: Must match camera credentials
- **CCTV RTSP Path**: Common paths:
  - Hikvision: `Streaming/Channels/101`
  - Dahua: `cam/realmonitor?channel=1&subtype=0`
  - Generic: `stream1`, `video1`, `live`

## Testing Steps After Fix

1. **Open manual-gate.vue**
2. **Check console logs** for configuration
3. **Use "Test Koneksi" button** (admin only)
4. **Verify camera displays** show green status chips
5. **Try "Test Capture"** to verify image capture works

## Camera Status Indicators

In UI, camera chips show:
- 🟢 **Green**: Camera configured and working
- 🟡 **Yellow**: Using default/test configuration
- 🔴 **Red**: Camera connection failed

## FFmpeg Troubleshooting

If FFmpeg errors persist:
1. Check FFmpeg path in `get_ffmpeg_path()`
2. Verify FFmpeg binary exists and is executable
3. Test RTSP URL manually with FFmpeg:
   ```bash
   ffmpeg -rtsp_transport tcp -i "rtsp://admin:password@192.168.1.11:554/Streaming/Channels/101" -frames:v 1 -f image2 test.jpg
   ```

## Next Steps
- Test with physical cameras
- Verify all camera types (USB vs CCTV)
- Test live streaming mode
- Performance optimization for high-resolution cameras
