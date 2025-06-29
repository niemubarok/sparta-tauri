# Hikvision ISAPI URL Support

## Problem Solved
The original implementation didn't support Hikvision ISAPI URLs like:
```
http://username:password@192.168.1.11/ISAPI/Streaming/channels/101/picture
```

## Solution Implemented

### 1. **Full URL Support**
Added `plate_camera_full_url` and `driver_camera_full_url` fields to database settings:

```typescript
// Database Settings
plate_camera_full_url: 'http://username:password@192.168.1.11/ISAPI/Streaming/channels/101/picture'
```

### 2. **Flexible URL Construction**
The camera handler now supports both methods:

**Method A: Full URL (Recommended for Hikvision)**
```rust
// Camera Handler Args
{
  full_url: "http://username:password@192.168.1.11/ISAPI/Streaming/channels/101/picture"
}
```

**Method B: Component-based URL**
```rust
// Camera Handler Args  
{
  ip_address: "192.168.1.11",
  username: "username", 
  password: "password",
  snapshot_path: "ISAPI/Streaming/channels/101/picture"
}
```

### 3. **Enhanced Debugging**
Added comprehensive logging to help diagnose issues:

```
📸 Capture CCTV Image called with args: ip=192.168.1.11, user=username, snapshot_path=ISAPI/Streaming/channels/101/picture, full_url=http://username:***@192.168.1.11/ISAPI/Streaming/channels/101/picture
🔗 Constructed snapshot URL: http://username:***@192.168.1.11/ISAPI/Streaming/channels/101/picture
📸 CCTV capture response: {is_success: true, has_base64: true, message: "Success", timestamp: "2025-06-29..."}
✅ CCTV image captured successfully, size: 45678 bytes
```

## Configuration for Your Setup

### Your URL Format:
```
http://username:password@192.168.1.11/ISAPI/Streaming/channels/101/picture
```

### Database Settings Update:
```typescript
// Update these values in your database settings
plate_camera_full_url: 'http://username:password@192.168.1.11/ISAPI/Streaming/channels/101/picture'
plate_camera_ip: '192.168.1.11'  // Backup
plate_camera_username: 'username'
plate_camera_password: 'password'  
plate_camera_snapshot_path: 'ISAPI/Streaming/channels/101/picture'
```

## Testing Steps

1. **Update Database Settings**:
   - Set your actual username/password
   - Set the correct IP address
   - Use the full ISAPI URL

2. **Test in Browser** (should work if camera is configured):
   ```
   http://yourusername:yourpassword@192.168.1.11/ISAPI/Streaming/channels/101/picture
   ```

3. **Check Logs**:
   - Look for "📸 Capture CCTV Image called with args"
   - Check for "✅ CCTV image captured successfully"
   - Watch for error messages with HTTP status codes

## Common Hikvision ISAPI Endpoints

```
# Live picture/snapshot
/ISAPI/Streaming/channels/101/picture
/ISAPI/Streaming/channels/201/picture  # Channel 2

# Different resolutions
/ISAPI/Streaming/channels/101/picture?snapShotImageType=JPEG
/ISAPI/Streaming/channels/101/picture?videoResolutionWidth=1920&videoResolutionHeight=1080
```

## Troubleshooting

1. **Authentication**: Ensure username/password are correct
2. **Network**: Verify camera is reachable from your network  
3. **Channel**: Confirm channel number (101, 201, etc.)
4. **ISAPI**: Verify camera supports ISAPI (most Hikvision do)
5. **URL Format**: Ensure URL matches exactly what works in browser
