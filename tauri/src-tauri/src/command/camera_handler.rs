use serde::{Deserialize, Serialize};
use base64::{Engine as _, engine::general_purpose::STANDARD as BASE64};
use chrono::Utc;
use std::process::Command;
use tempfile::NamedTempFile;
use reqwest;
use std::time::Duration;

// Import untuk live streaming
use tauri::{AppHandle, Runtime, Emitter};
use tokio::process::Command as TokioCommand;
use tokio::io::{AsyncBufReadExt, AsyncReadExt, BufReader};
use tokio::sync::mpsc;
use std::process::Stdio;
use std::sync::{Arc, Mutex};
use std::collections::HashMap;
use once_cell::sync::Lazy;

#[derive(Serialize)]
pub struct CctvResponse {
    is_success: bool,
    base64: Option<String>,
    time_stamp: String,
    message: Option<String>,
}

#[derive(Deserialize, Debug, Clone)]
#[serde(rename_all = "snake_case")]
pub enum CaptureMode {
    Rtsp,
    Snapshot,
}

fn get_ffmpeg_path() -> String {
    let ffmpeg_path_segment = if cfg!(windows) {
        "../../scripts/ffmpeg/ffmpeg.exe" // Adjusted path for Windows
    } else {
        "../../scripts/ffmpeg/ffmpeg" // Adjusted path for other OS
    };

    let exe_path = std::env::current_exe().expect("Failed to get executable path");
    let exe_dir = exe_path.parent().expect("Failed to get executable directory");
    
    let ffmpeg_full_path = exe_dir.join(ffmpeg_path_segment);

    ffmpeg_full_path.to_str().expect("Failed to convert path to string").to_string()
}

// Updated CaptureCctvImageArgs untuk mendukung mode snapshot dan RTSP
#[derive(Deserialize, Clone)]
#[serde(rename_all = "snake_case")]
pub struct CaptureCctvImageArgs {
    username: Option<String>,
    password: Option<String>,
    ip_address: String,
    rtsp_stream_path: Option<String>, // Optional untuk mode snapshot
    snapshot_url: Option<String>,     // URL snapshot kustom
    capture_mode: Option<CaptureMode>, // Mode capture (default: rtsp untuk backward compatibility)
    port: Option<u16>,               // Port kustom
    timeout_seconds: Option<u64>,    // Timeout kustom
}

#[cfg(windows)]
use std::os::windows::process::CommandExt;

// Fungsi untuk capture via HTTP snapshot
async fn capture_via_snapshot(args: &CaptureCctvImageArgs) -> Result<CctvResponse, String> {
    println!("📸 Capturing via HTTP snapshot mode");
    println!("📸 Args received: snapshot_url={:?}, ip_address={}, port={:?}", 
             args.snapshot_url, args.ip_address, args.port);
    
    let snapshot_url = if let Some(url) = &args.snapshot_url {
        if !url.is_empty() {
            // Gunakan URL kustom dari settings jika tersedia dan tidak kosong
            println!("📸 Using custom snapshot URL from settings: {}", url);
            
            // Cek apakah URL sudah lengkap (mengandung http://) atau masih path relatif
            if url.starts_with("http://") || url.starts_with("https://") {
                // URL sudah lengkap, gunakan langsung
                url.clone()
            } else {
                // URL adalah path relatif, konstruksi URL lengkap dengan IP, port, dan credentials
                let port = args.port.unwrap_or(80);
                
                // Konstruksi URL dengan credentials jika tersedia
                let base_url = if let (Some(username), Some(password)) = (&args.username, &args.password) {
                    if !username.is_empty() && !password.is_empty() {
                        // Sertakan credentials dalam URL untuk kamera yang membutuhkannya
                        if port == 80 {
                            format!("http://{}:{}@{}", username, password, args.ip_address)
                        } else {
                            format!("http://{}:{}@{}:{}", username, password, args.ip_address, port)
                        }
                    } else {
                        // Tanpa credentials
                        if port == 80 {
                            format!("http://{}", args.ip_address)
                        } else {
                            format!("http://{}:{}", args.ip_address, port)
                        }
                    }
                } else {
                    // Tanpa credentials
                    if port == 80 {
                        format!("http://{}", args.ip_address)
                    } else {
                        format!("http://{}:{}", args.ip_address, port)
                    }
                };
                
                // Pastikan path dimulai dengan slash
                let path = if url.starts_with('/') {
                    url.clone()
                } else {
                    format!("/{}", url)
                };
                
                let full_url = format!("{}{}", base_url, path);
                println!("📸 Constructed full URL from custom path: {}", full_url.replace(&args.password.as_deref().unwrap_or(""), "***"));
                full_url
            }
        } else {
            // URL kosong, gunakan default path
            println!("📸 Custom snapshot URL is empty, using default paths");
            let port = args.port.unwrap_or(80);
            let base_url = if port == 80 {
                format!("http://{}", args.ip_address)
            } else {
                format!("http://{}:{}", args.ip_address, port)
            };
            
            // Path snapshot umum untuk berbagai merek CCTV
            let default_paths = vec![
                "/cgi-bin/snapshot.cgi",           // Hikvision, Dahua
                "/ISAPI/Streaming/channels/101/picture", // Hikvision modern
                "/tmpfs/auto.jpg",                 // Beberapa IP camera
                "/snapshot.jpg",                   // Generic
                "/cgi-bin/currentpic.cgi",        // Axis cameras
                "/jpeg/image.cgi",                 // Kamera lama
                "/snapshot/view0.jpg",             // Kamera modern
                "/image.jpg",
                "/Snapshot/1/RemoteImageCapture?ImageFormat=2" //glenz                      // Path sederhana
            ];
            
            // Gunakan path default pertama
            format!("{}{}", base_url, default_paths[0])
        }
    } else {
        // Tidak ada parameter snapshot_url sama sekali, konstruksi URL default
        println!("📸 No custom snapshot URL provided, constructing default URL");
        let port = args.port.unwrap_or(80);
        let base_url = if port == 80 {
            format!("http://{}", args.ip_address)
        } else {
            format!("http://{}:{}", args.ip_address, port)
        };
        
        // Path snapshot umum untuk berbagai merek CCTV
        let default_paths = vec![
            "/cgi-bin/snapshot.cgi",           // Hikvision, Dahua
            "/ISAPI/Streaming/channels/101/picture", // Hikvision modern
            "/tmpfs/auto.jpg",                 // Beberapa IP camera
            "/snapshot.jpg",                   // Generic
            "/cgi-bin/currentpic.cgi",        // Axis cameras
            "/jpeg/image.cgi",                 // Kamera lama
            "/snapshot/view0.jpg",             // Kamera modern
            "/image.jpg",
            "/Snapshot/1/RemoteImageCapture?ImageFormat=2" //glenz                      // Path sederhana
        ];
        
        // Gunakan path default pertama
        format!("{}{}", base_url, default_paths[0])
    };

    println!("🔗 Snapshot URL: {}", snapshot_url.replace(&args.password.as_deref().unwrap_or(""), "***"));

    let timeout = Duration::from_secs(args.timeout_seconds.unwrap_or(30)); // Increase timeout to 30 seconds
    let client = reqwest::Client::builder()
        .timeout(timeout)
        .danger_accept_invalid_certs(true) // Terima sertifikat self-signed
        .redirect(reqwest::redirect::Policy::limited(3)) // Allow redirects
        .build()
        .map_err(|e| format!("Failed to create HTTP client: {}", e))?;

    // Always use clean URL without embedded credentials and rely on basic auth headers
    let clean_url = if snapshot_url.contains("@") {
        // Remove credentials from URL - reqwest handles auth better via headers
        let url_parts: Vec<&str> = snapshot_url.split("@").collect();
        if url_parts.len() == 2 {
            let protocol_and_creds = url_parts[0];
            let host_and_path = url_parts[1];
            
            // Extract just the protocol part
            if let Some(protocol_pos) = protocol_and_creds.rfind("://") {
                let protocol = &protocol_and_creds[..protocol_pos + 3];
                let clean_url = format!("{}{}", protocol, host_and_path);
                println!("📸 Using clean URL without embedded credentials: {}", clean_url);
                clean_url
            } else {
                snapshot_url.clone()
            }
        } else {
            snapshot_url.clone()
        }
    } else {
        snapshot_url.clone()
    };

    let mut request = client.get(&clean_url);

    // Always add basic auth headers
    if let (Some(username), Some(password)) = (&args.username, &args.password) {
        if !username.is_empty() && !password.is_empty() {
            println!("📸 Adding basic auth headers for user: {}", username);
            request = request.basic_auth(username, Some(password));
        }
    }

    // Set header umum untuk kamera CCTV
    request = request
        .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        .header("Accept", "image/jpeg,image/png,image/*,*/*")
        .header("Connection", "close")
        .header("Cache-Control", "no-cache")
        .header("Pragma", "no-cache");

    println!("📸 Sending HTTP request to camera at: {}", clean_url);
    
    // Try a quick HEAD request first to test connectivity
    let test_request = client.head(&clean_url);
    let test_request = if let (Some(username), Some(password)) = (&args.username, &args.password) {
        if !username.is_empty() && !password.is_empty() {
            test_request.basic_auth(username, Some(password))
        } else {
            test_request
        }
    } else {
        test_request
    };
    
    match test_request.send().await {
        Ok(test_response) => {
            println!("📸 HEAD request test - Status: {}", test_response.status());
        }
        Err(e) => {
            println!("⚠️ HEAD request test failed: {}", e);
            // Continue with GET request anyway
        }
    }
    
    let response = request.send().await
        .map_err(|e| {
            println!("❌ HTTP request failed: {}", e);
            if e.is_timeout() {
                format!("Camera connection timeout ({}s) - check network connectivity", args.timeout_seconds.unwrap_or(30))
            } else if e.is_connect() {
                format!("Cannot connect to camera - check IP address and network")
            } else if e.is_request() {
                format!("Invalid request - check camera URL and settings")
            } else {
                format!("HTTP request failed: {}", e)
            }
        })?;

    println!("📸 Response received - Status: {} ({})", response.status(), response.status().as_u16());
    
    if !response.status().is_success() {
        let status_code = response.status().as_u16();
        let error_msg = match status_code {
            401 => "Authentication failed - check username and password".to_string(),
            403 => "Access forbidden - camera may not allow snapshot access".to_string(),
            404 => "Snapshot URL not found - check camera model and URL path".to_string(),
            408 => "Request timeout - camera took too long to respond".to_string(),
            500..=599 => "Camera internal error - camera may be busy or malfunctioning".to_string(),
            _ => format!("HTTP error: {} - {}", response.status(), response.status().canonical_reason().unwrap_or("Unknown error"))
        };
        
        println!("❌ HTTP error: {}", error_msg);
        return Ok(CctvResponse {
            is_success: false,
            base64: None,
            time_stamp: Utc::now().to_rfc3339(),
            message: Some(error_msg),
        });
    }

    println!("📸 Reading response body...");
    let image_data = response.bytes().await
        .map_err(|e| {
            println!("❌ Failed to read response body: {}", e);
            format!("Failed to read image data: {}", e)
        })?;

    if image_data.is_empty() {
        return Ok(CctvResponse {
            is_success: false,
            base64: None,
            time_stamp: Utc::now().to_rfc3339(),
            message: Some("Received empty image data".to_string()),
        });
    }

    // Validasi bahwa data yang diterima adalah gambar
    if image_data.len() < 100 || (!image_data.starts_with(&[0xFF, 0xD8]) && !image_data.starts_with(b"PNG")) {
        return Ok(CctvResponse {
            is_success: false,
            base64: None,
            time_stamp: Utc::now().to_rfc3339(),
            message: Some("Invalid image data received".to_string()),
        });
    }

    let base64_string = format!(
        "data:image/jpeg;base64,{}",
        BASE64.encode(&image_data)
    );

    println!("✅ Successfully captured snapshot image. Size: {} bytes", image_data.len());

    Ok(CctvResponse {
        is_success: true,
        base64: Some(base64_string),
        time_stamp: Utc::now().to_rfc3339(),
        message: Some("Berhasil mengambil gambar dari CCTV melalui snapshot".to_string()),
    })
}

// Fungsi untuk capture via RTSP (kode asli Anda yang sudah ada)
async fn capture_via_rtsp(args: &CaptureCctvImageArgs) -> Result<CctvResponse, String> {
    println!("📸 Capturing via RTSP mode");
    
    let rtsp_stream_path = args.rtsp_stream_path.as_ref()
        .ok_or("RTSP stream path is required for RTSP mode")?;
    
    if rtsp_stream_path.is_empty() {
        return Err("RTSP stream path cannot be empty".to_string());
    }

    // Helper function to clean path
    let clean_path = rtsp_stream_path.trim_matches('/');
    let port = args.port.unwrap_or(554);
    
    let rtsp_url = if let (Some(user), Some(pass)) = (args.username.as_deref(), args.password.as_deref()) {
        if !user.is_empty() && !pass.is_empty() {
            format!(
                "rtsp://{}:{}@{}:{}/{}",
                user, pass, args.ip_address, port, clean_path
            )
        } else {
            format!("rtsp://{}:{}/{}", args.ip_address, port, clean_path)
        }
    } else {
        format!("rtsp://{}:{}/{}", args.ip_address, port, clean_path)
    };

    println!("🔗 Constructed RTSP URL: {}", rtsp_url.replace(&args.password.as_deref().unwrap_or(""), "***"));

    let temp_file = NamedTempFile::new()
        .map_err(|e| format!("Failed to create temporary file: {}", e))?;
    let temp_path = temp_file.path().to_str()
        .ok_or("Failed to get temporary file path")?;

    let ffmpeg_path = get_ffmpeg_path();
    println!("🎬 Using FFmpeg at: {}", ffmpeg_path);

    let timeout_str = format!("{}", args.timeout_seconds.unwrap_or(10) * 1000000); // Convert to microseconds

    let mut command = Command::new(ffmpeg_path);
    command.args(&[
        "-rtsp_transport", "tcp",
        "-timeout", &timeout_str,
        "-i", &rtsp_url,
        "-frames:v", "1",
        "-f", "image2",
        "-y", 
        temp_path
    ]);
    
    #[cfg(windows)]
    command.creation_flags(0x08000000); // CREATE_NO_WINDOW
    
    let output = command.output()
        .map_err(|e| format!("Failed to execute FFmpeg: {}", e))?;

    if !output.status.success() {
        let error = String::from_utf8_lossy(&output.stderr);
        println!("❌ FFmpeg error: {}", error);
        return Ok(CctvResponse {
            is_success: false,
            base64: None,
            time_stamp: Utc::now().to_rfc3339(),
            message: Some(format!("FFmpeg error: {}", error)),
        });
    }

    let image_data = std::fs::read(temp_path)
        .map_err(|e| format!("Failed to read captured image: {}", e))?;

    let base64_string = format!(
        "data:image/jpeg;base64,{}",
        BASE64.encode(&image_data)
    );

    temp_file.close()
        .map_err(|e| format!("Failed to delete temporary file: {}", e))?;

    println!("✅ Successfully captured RTSP image. Size: {} bytes", image_data.len());

    Ok(CctvResponse {
        is_success: true,
        base64: Some(base64_string),
        time_stamp: Utc::now().to_rfc3339(),
        message: Some("Berhasil mengambil gambar dari CCTV melalui RTSP".to_string()),
    })
}

// Command utama untuk capture image (mengganti yang lama)
#[tauri::command]
pub async fn capture_cctv_image(args: CaptureCctvImageArgs) -> Result<CctvResponse, String> {
    println!("📸 Capture CCTV Image called with mode: {:?}, ip: {}", 
             args.capture_mode.as_ref().unwrap_or(&CaptureMode::Rtsp), args.ip_address);
    
    // Validate inputs
    if args.ip_address.is_empty() {
        return Err("IP address cannot be empty".to_string());
    }

    let capture_mode = args.capture_mode.as_ref().unwrap_or(&CaptureMode::Rtsp);

    match capture_mode {
        CaptureMode::Snapshot => capture_via_snapshot(&args).await,
        CaptureMode::Rtsp => capture_via_rtsp(&args).await,
    }
}

// Command baru untuk auto-detect mode terbaik
#[tauri::command]
pub async fn capture_cctv_image_auto_detect(args: CaptureCctvImageArgs) -> Result<CctvResponse, String> {
    println!("📸 Auto-detect CCTV capture called for IP: {}", args.ip_address);
    println!("📸 Auto-detect args: snapshot_url={:?}, port={:?}", args.snapshot_url, args.port);
    
    if args.ip_address.is_empty() {
        return Err("IP address cannot be empty".to_string());
    }

    // Jika snapshot_url disediakan dan tidak kosong, gunakan langsung
    if let Some(ref url) = args.snapshot_url {
        if !url.is_empty() {
            println!("📸 Auto-detect: Using custom snapshot URL: {}", url);
            
            // Cek apakah URL sudah lengkap atau masih path relatif
            if url.starts_with("http://") || url.starts_with("https://") {
                // URL sudah lengkap, gunakan langsung
                return capture_via_snapshot(&args).await;
            } else {
                // URL adalah path relatif, konstruksi URL lengkap dengan credentials
                let port = args.port.unwrap_or(80);
                
                let base_url = if let (Some(username), Some(password)) = (&args.username, &args.password) {
                    if !username.is_empty() && !password.is_empty() {
                        // Sertakan credentials dalam URL
                        if port == 80 {
                            format!("http://{}:{}@{}", username, password, args.ip_address)
                        } else {
                            format!("http://{}:{}@{}:{}", username, password, args.ip_address, port)
                        }
                    } else {
                        if port == 80 {
                            format!("http://{}", args.ip_address)
                        } else {
                            format!("http://{}:{}", args.ip_address, port)
                        }
                    }
                } else {
                    if port == 80 {
                        format!("http://{}", args.ip_address)
                    } else {
                        format!("http://{}:{}", args.ip_address, port)
                    }
                };
                
                let path = if url.starts_with('/') {
                    url.clone()
                } else {
                    format!("/{}", url)
                };
                
                let full_url = format!("{}{}", base_url, path);
                println!("📸 Auto-detect: Constructed full URL from custom path: {}", full_url.replace(&args.password.as_deref().unwrap_or(""), "***"));
                
                // Buat args baru dengan URL lengkap untuk capture
                let mut custom_args = args.clone();
                custom_args.snapshot_url = Some(full_url);
                return capture_via_snapshot(&custom_args).await;
            }
        } else {
            println!("📸 Auto-detect: Custom snapshot URL is empty, trying default paths");
        }
    } else {
        println!("📸 Auto-detect: No custom snapshot URL provided, trying default paths");
    }

    // Coba berbagai URL snapshot untuk merek CCTV yang berbeda
    let port = args.port.unwrap_or(80);
    let base_url = if port == 80 {
        format!("http://{}", args.ip_address)
    } else {
        format!("http://{}:{}", args.ip_address, port)
    };

    let snapshot_paths = vec![
        "/cgi-bin/snapshot.cgi",           // Hikvision, Dahua
        "/ISAPI/Streaming/channels/101/picture", // Hikvision modern
        "/snapshot.cgi",                   // Beberapa kamera
        "/tmpfs/auto.jpg",                 // Beberapa IP camera
        "/snapshot.jpg",                   // Generic
        "/cgi-bin/currentpic.cgi",        // Axis cameras
        "/jpeg/image.cgi",                 // Kamera lama
        "/snapshot/view0.jpg",             // Kamera modern
        "/image.jpg",                      // Path sederhana
        "/jpg/image.jpg",                  // Path umum lainnya
        "/cgi-bin/api.cgi?cmd=Snap&channel=0&rs=wuuPhkmUOeI9WG7C", // Reolink style
    ];

    let mut last_error = String::new();

    for path in snapshot_paths {
        let snapshot_url = format!("{}{}", base_url, path);

        let mut test_args = args.clone();
        test_args.snapshot_url = Some(snapshot_url);
        test_args.timeout_seconds = Some(5); // Timeout lebih pendek untuk auto-detection

        match capture_via_snapshot(&test_args).await {
            Ok(response) if response.is_success => {
                println!("✅ Auto-detected working snapshot URL: {}", path);
                return Ok(response);
            }
            Ok(response) => {
                last_error = response.message.unwrap_or("Unknown error".to_string());
            }
            Err(e) => {
                last_error = e;
            }
        }
    }

    // Jika semua percobaan snapshot gagal, coba RTSP sebagai fallback
    if args.rtsp_stream_path.is_some() {
        println!("🔄 Snapshot auto-detection failed, trying RTSP fallback");
        return capture_via_rtsp(&args).await;
    }

    Ok(CctvResponse {
        is_success: false,
        base64: None,
        time_stamp: Utc::now().to_rfc3339(),
        message: Some(format!("Auto-detection failed. Last error: {}", last_error)),
    })
}

// === BAGIAN LIVE STREAMING (KODE ASLI ANDA) ===

// Define a struct to hold the child process and its shutdown sender
struct ActiveStream {
    process_child: tokio::process::Child,
    shutdown_tx: mpsc::Sender<()>, // Sender to signal the streaming task to stop
    cleanup_handle: tokio::task::JoinHandle<()>, // New field for cleanup task
}

// State to keep track of active FFmpeg processes and their shutdown senders
static ACTIVE_STREAMS: Lazy<Arc<Mutex<HashMap<String, ActiveStream>>>> = Lazy::new(|| Arc::new(Mutex::new(HashMap::new())));

#[derive(Deserialize, Serialize, Clone)]
#[serde(rename_all = "snake_case")] // Change to snake_case to match the capture args
pub struct LiveStreamArgs {
    stream_id: String, // A unique ID for this stream, generated by frontend
    username: Option<String>,
    password: Option<String>,
    ip_address: String,
    rtsp_stream_path: String,
}

#[derive(Serialize)]
pub struct StreamResponse {
    is_success: bool,
    message: Option<String>,
}

#[tauri::command]
pub async fn start_rtsp_live_stream<R: Runtime>(
    app_handle: AppHandle<R>,
    args: LiveStreamArgs,
) -> Result<StreamResponse, String> {
    if args.ip_address.is_empty() {
        return Err("IP address cannot be empty".to_string());
    }
    if args.rtsp_stream_path.is_empty() {
        return Err("RTSP stream path cannot be empty".to_string());
    }

    let clean_path = args.rtsp_stream_path.trim_matches('/');
    let rtsp_url = match (args.username.as_deref(), args.password.as_deref()) {
        (Some(user), Some(pass)) if !user.is_empty() && !pass.is_empty() => {
            format!("rtsp://{}:{}@{}:554/{}", user, pass, args.ip_address, clean_path)
        },
        _ => format!("rtsp://{}:554/{}", args.ip_address, clean_path)
    };
    
    let ffmpeg_path = get_ffmpeg_path();

    let mut cmd = TokioCommand::new(ffmpeg_path);
    cmd.args([
        "-fflags", "nobuffer",
        "-flags", "low_delay",
        "-rtsp_transport", "tcp",
        "-i", &rtsp_url,
        "-c:v", "mjpeg",
        "-vf", "fps=5",
        "-q:v", "7",
        "-an",
        "-f", "mjpeg",
        "-fps_mode", "cfr",
        "pipe:1"
    ]);
    
    #[cfg(windows)]
    cmd.creation_flags(0x08000000); // CREATE_NO_WINDOW
    
    cmd.kill_on_drop(true);
    cmd.stdout(Stdio::piped());
    cmd.stderr(Stdio::piped());
    
    let mut child = match cmd.spawn() {
        Ok(c) => c,
        Err(e) => return Ok(StreamResponse { is_success: false, message: Some(format!("Failed to spawn FFmpeg: {}", e)) }),
    };

    let stdout = child.stdout.take().expect("FFmpeg stdout was not captured");
    let stderr = child.stderr.take().expect("FFmpeg stderr was not captured");

    let stream_id_for_insert = args.stream_id.clone(); // Clone for inserting into ACTIVE_STREAMS
    let stream_id_for_stderr_task = args.stream_id.clone(); // Clone for stderr task
    let stream_id_for_stdout_task = args.stream_id.clone(); // Clone for stdout task

    let app_handle_clone = app_handle.clone();

    let (shutdown_tx, mut shutdown_rx) = mpsc::channel::<()>(1);

    // Task to read stderr for debugging FFmpeg issues
    tokio::spawn(async move {
        let reader = BufReader::new(stderr);
        let mut lines = reader.lines();
        while let Ok(Some(line)) = lines.next_line().await {
            eprintln!("[FFmpeg stderr {}]: {}", stream_id_for_stderr_task, line);
        }
    });

    // Task to read stdout and emit frames
    tokio::spawn(async move {
        let mut reader = BufReader::new(stdout);
        let mut buffer = vec![0; 4096]; // Use a fixed-size buffer for reading chunks
        let mut frame_data = Vec::new();
        let mut last_frame_time = std::time::Instant::now();
        let timeout_duration = std::time::Duration::from_secs(5);

        loop {
            tokio::select! {
                _ = shutdown_rx.recv() => {
                    println!("Shutdown signal received for stream {}", stream_id_for_stdout_task);
                    break;
                }
                _ = tokio::time::sleep(timeout_duration) => {
                    if last_frame_time.elapsed() > timeout_duration {
                        // Emit connection status event to frontend
                        let _ = app_handle_clone.emit(&format!("cctv-connection-status::{}", stream_id_for_stdout_task), 
                            "connection_slow");
                    }
                }
                read_res = reader.read(&mut buffer) => {
                    match read_res {
                        Ok(0) => {
                            println!("FFmpeg stdout EOF for stream {}", stream_id_for_stdout_task);
                            let _ = app_handle_clone.emit(&format!("cctv-connection-status::{}", stream_id_for_stdout_task), 
                                "disconnected");
                            // Continue loop to allow reconnection
                            tokio::time::sleep(std::time::Duration::from_secs(1)).await;
                            continue;
                        },
                        Ok(n) => {
                            last_frame_time = std::time::Instant::now();
                            frame_data.extend_from_slice(&buffer[..n]);

                            // Process frames logic
                            while let Some(start_index) = frame_data.windows(2).position(|window| window == [0xFF, 0xD8]) {
                                if let Some(end_index) = frame_data[start_index + 2..].windows(2).position(|window| window == [0xFF, 0xD9]) {
                                    let actual_end_index = start_index + 2 + end_index + 2;
                                    
                                    if actual_end_index <= frame_data.len() {
                                        let complete_frame = frame_data[start_index..actual_end_index].to_vec();
                                        let base64_frame = BASE64.encode(&complete_frame);
                                        
                                        // Emit frame and connection status
                                        let _ = app_handle_clone.emit(&format!("cctv-live-frame::{}", stream_id_for_stdout_task), 
                                            base64_frame);
                                        let _ = app_handle_clone.emit(&format!("cctv-connection-status::{}", stream_id_for_stdout_task), 
                                            "connected");
                                            
                                        frame_data.drain(0..actual_end_index);
                                    } else {
                                        break;
                                    }
                                } else {
                                    break;
                                }
                            }

                            if frame_data.len() > 1_000_000 {
                                frame_data.clear();
                                eprintln!("Cleared oversized frame buffer for stream {}", stream_id_for_stdout_task);
                            }
                        }
                        Err(e) => {
                            eprintln!("Error reading FFmpeg stdout for stream {}: {}", stream_id_for_stdout_task, e);
                            let _ = app_handle_clone.emit(&format!("cctv-connection-status::{}", stream_id_for_stdout_task), 
                                "error");
                            tokio::time::sleep(std::time::Duration::from_secs(1)).await;
                            continue;
                        }
                    }
                }
            }
        }
    });

    let cleanup_handle = tokio::spawn(async move {
        let _ = tokio::signal::ctrl_c().await;
        // Cleanup code will be handled in stop_rtsp_live_stream
    });

    let mut streams = ACTIVE_STREAMS.lock().unwrap();
    streams.insert(stream_id_for_insert, ActiveStream { 
        process_child: child, 
        shutdown_tx,
        cleanup_handle,
    });

    Ok(StreamResponse { is_success: true, message: Some(format!("Live stream started for {}", args.stream_id)) })
}

#[tauri::command]
pub async fn stop_rtsp_live_stream(stream_id: String) -> Result<StreamResponse, String> {
    let active_stream_details = {
        let mut streams = ACTIVE_STREAMS.lock().unwrap();
        streams.remove(&stream_id)
    };

    if let Some(mut active_stream) = active_stream_details {
        // Send shutdown signal with timeout
        let shutdown_timeout = tokio::time::timeout(
            std::time::Duration::from_secs(5),
            active_stream.shutdown_tx.send(())
        ).await;

        if let Err(_) = shutdown_timeout {
            eprintln!("Shutdown signal timeout for stream {}", stream_id);
        }

        // Graceful shutdown attempt with SIGTERM
        if let Err(e) = active_stream.process_child.start_kill() {
            eprintln!("Failed to send SIGTERM to FFmpeg process: {}", e);
        }

        // Wait for process to exit gracefully
        let exit_status = tokio::time::timeout(
            std::time::Duration::from_secs(3),
            active_stream.process_child.wait()
        ).await;

        match exit_status {
            Ok(Ok(_)) => {
                // Process exited cleanly
                active_stream.cleanup_handle.abort(); // Cancel cleanup task
                Ok(StreamResponse { 
                    is_success: true, 
                    message: Some(format!("Stream {} stopped cleanly.", stream_id)) 
                })
            },
            _ => {
                // Force kill if graceful shutdown failed
                if let Err(e) = active_stream.process_child.kill().await {
                    eprintln!("Failed to kill FFmpeg process: {}", e);
                }
                active_stream.cleanup_handle.abort();
                Ok(StreamResponse { 
                    is_success: true, 
                    message: Some(format!("Stream {} force stopped.", stream_id)) 
                })
            }
        }
    } else {
        Ok(StreamResponse { 
            is_success: false, 
            message: Some(format!("Stream {} not found.", stream_id)) 
        })
    }
}
