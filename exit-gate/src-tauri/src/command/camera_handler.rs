use serde::{Deserialize, Serialize};
use base64::{Engine as _, engine::general_purpose::STANDARD as BASE64};
use chrono::Utc;

#[derive(Serialize)]
pub struct CctvResponse {
    is_success: bool,
    base64: Option<String>,
    time_stamp: String,
    message: Option<String>,
}

#[derive(Deserialize)]
#[serde(rename_all = "snake_case")]
pub struct CaptureCctvImageArgs {
    username: Option<String>,
    password: Option<String>,
    ip_address: Option<String>, // Made optional since we can use full_url instead
    snapshot_path: Option<String>,
    full_url: Option<String>, // Added full_url field
}

#[tauri::command]
pub async fn capture_cctv_image(args: CaptureCctvImageArgs) -> Result<CctvResponse, String> {
    println!("📸 Capture CCTV Image called with args: ip={}, user={}, snapshot_path={}, full_url={}", 
             args.ip_address.as_deref().unwrap_or("None"), 
             args.username.as_deref().unwrap_or("None"), 
             args.snapshot_path.as_deref().unwrap_or("Default"),
             args.full_url.as_deref().unwrap_or("None"));
    
    // Construct snapshot URL
    let snapshot_url = if let Some(full_url) = &args.full_url {
        if !full_url.is_empty() {
            // Use full URL if provided (e.g., http://username:password@192.168.1.11/ISAPI/Streaming/channels/101/picture)
            full_url.clone()
        } else {
            // Validate inputs for manual construction
            let ip_address = args.ip_address.as_deref().unwrap_or("");
            if ip_address.is_empty() {
                return Err("IP address cannot be empty when full_url is not provided".to_string());
            }

            // Default snapshot paths for common CCTV brands
            let snapshot_path = args.snapshot_path.as_deref().unwrap_or("Streaming/Channels/1/picture");
            let clean_path = snapshot_path.trim_matches('/');
            
            // Construct HTTP snapshot URL
            if let (Some(user), Some(pass)) = (args.username.as_deref(), args.password.as_deref()) {
                if !user.is_empty() && !pass.is_empty() {
                    format!("http://{}:{}@{}/{}", user, pass, ip_address, clean_path)
                } else {
                    format!("http://{}/{}", ip_address, clean_path)
                }
            } else {
                format!("http://{}/{}", ip_address, clean_path)
            }
        }
    } else {
        // Validate inputs for manual construction
        let ip_address = args.ip_address.as_deref().unwrap_or("");
        if ip_address.is_empty() {
            return Err("IP address cannot be empty when full_url is not provided".to_string());
        }

        // Default snapshot paths for common CCTV brands
        let snapshot_path = args.snapshot_path.as_deref().unwrap_or("Streaming/Channels/1/picture");
        let clean_path = snapshot_path.trim_matches('/');
        
        // Construct HTTP snapshot URL
        if let (Some(user), Some(pass)) = (args.username.as_deref(), args.password.as_deref()) {
            if !user.is_empty() && !pass.is_empty() {
                format!("http://{}:{}@{}/{}", user, pass, ip_address, clean_path)
            } else {
                format!("http://{}/{}", ip_address, clean_path)
            }
        } else {
            format!("http://{}/{}", ip_address, clean_path)
        }
    };

    println!("🔗 Constructed snapshot URL: {}", 
             if let Some(pass) = &args.password {
                 if !pass.is_empty() {
                     snapshot_url.replace(pass, "***")
                 } else {
                     snapshot_url.clone()
                 }
             } else {
                 snapshot_url.clone()
             });

    // Create HTTP client with timeout
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(10))
        .build()
        .map_err(|e| format!("Failed to create HTTP client: {}", e))?;

    // Fetch image from CCTV snapshot endpoint
    let response = client
        .get(&snapshot_url)
        .send()
        .await
        .map_err(|e| format!("Failed to fetch snapshot: {}", e))?;

    if !response.status().is_success() {
        let error_msg = format!("HTTP error: {} - {}", response.status(), response.status().canonical_reason().unwrap_or("Unknown"));
        println!("❌ Snapshot fetch error: {}", error_msg);
        return Ok(CctvResponse {
            is_success: false,
            base64: None,
            time_stamp: Utc::now().to_rfc3339(),
            message: Some(error_msg),
        });
    }

    // Get image data
    let image_data = response
        .bytes()
        .await
        .map_err(|e| format!("Failed to read image data: {}", e))?;

    // Verify it's an image by checking content type or magic bytes
    if image_data.len() < 10 {
        return Ok(CctvResponse {
            is_success: false,
            base64: None,
            time_stamp: Utc::now().to_rfc3339(),
            message: Some("Received data is too small to be an image".to_string()),
        });
    }

    // Check for JPEG magic bytes (0xFF 0xD8)
    let is_jpeg = image_data.len() >= 2 && image_data[0] == 0xFF && image_data[1] == 0xD8;
    
    if !is_jpeg {
        return Ok(CctvResponse {
            is_success: false,
            base64: None,
            time_stamp: Utc::now().to_rfc3339(),
            message: Some("Received data is not a valid JPEG image".to_string()),
        });
    }

    let base64_string = format!(
        "data:image/jpeg;base64,{}",
        BASE64.encode(&image_data)
    );

    println!("✅ Successfully captured CCTV snapshot. Size: {} bytes", image_data.len());

    Ok(CctvResponse {
        is_success: true,
        base64: Some(base64_string),
        time_stamp: Utc::now().to_rfc3339(),
        message: Some("Berhasil mengambil gambar dari CCTV".to_string()),
    })
}
