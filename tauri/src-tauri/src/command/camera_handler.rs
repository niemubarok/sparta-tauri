use serde::{Deserialize, Serialize};
use base64::{Engine as _, engine::general_purpose::STANDARD as BASE64};
use chrono::Utc;
use std::process::Command;
use tempfile::NamedTempFile;

// No longer using CctvConfig or CameraInfo structs from here as config will be passed directly
// or managed by the frontend store.

#[derive(Serialize)]
pub struct CctvResponse {
    is_success: bool,
    base64: Option<String>,
    time_stamp: String,
    message: Option<String>,
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

// get_config_path and get_cctv_configs are removed as we no longer read from cctv_config.json

#[derive(Deserialize)] // Tambahkan Deserialize
#[serde(rename_all = "camelCase")]
pub struct CaptureCctvImageArgs {
    username: Option<String>,
    password: Option<String>,
    ip_address: String,
    rtsp_stream_path: String,
}

#[tauri::command]
pub async fn capture_cctv_image(args: CaptureCctvImageArgs) -> Result<CctvResponse, String> {
    // camera_id is removed as specific config is passed directly
    // 
    // Validate inputs
    if args.ip_address.is_empty() {
        return Err("IP address cannot be empty".to_string());
    }
    if args.rtsp_stream_path.is_empty() {
        return Err("RTSP stream path cannot be empty".to_string());
    }

    // Helper function to clean path
    let clean_path = args.rtsp_stream_path.trim_matches('/');
    
    let rtsp_url = if let (Some(user), Some(pass)) = (args.username.as_deref(), args.password.as_deref()) {
        if !user.is_empty() && !pass.is_empty() {
            format!(
                "rtsp://{}:{}@{}:554/{}",
                user, pass, args.ip_address, clean_path
            )
        } else {
            format!("rtsp://{}:554/{}", args.ip_address, clean_path)
        }
    } else {
        format!("rtsp://{}:554/{}", args.ip_address, clean_path)
    };

    let temp_file = NamedTempFile::new()
        .map_err(|e| format!("Failed to create temporary file: {}", e))?;
    let temp_path = temp_file.path().to_str()
        .ok_or("Failed to get temporary file path")?;

    let ffmpeg_path = get_ffmpeg_path();

    let output = Command::new(ffmpeg_path)
        .args(&[
            "-rtsp_transport", "tcp",
            "-i", &rtsp_url,
            "-frames:v", "1",
            "-f", "image2",
            "-y", 
            temp_path
        ])
        .output()
        .map_err(|e| format!("Failed to execute FFmpeg: {}", e))?;

    if !output.status.success() {
        let error = String::from_utf8_lossy(&output.stderr);
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

    Ok(CctvResponse {
        is_success: true,
        base64: Some(base64_string),
        time_stamp: Utc::now().to_rfc3339(),
        message: Some("Berhasil mengambil gambar dari CCTV".to_string()),
    })
}

use tauri::{AppHandle, Runtime, Emitter};
use tokio::process::Command as TokioCommand;
use tokio::io::{AsyncBufReadExt, AsyncReadExt, BufReader};
use tokio::sync::mpsc;
use std::process::Stdio;
use std::sync::{Arc, Mutex};
use std::collections::HashMap;
use once_cell::sync::Lazy;

// Define a struct to hold the child process and its shutdown sender
struct ActiveStream {
    process_child: tokio::process::Child,
    shutdown_tx: mpsc::Sender<()>, // Sender to signal the streaming task to stop
    cleanup_handle: tokio::task::JoinHandle<()>, // New field for cleanup task
}

// State to keep track of active FFmpeg processes and their shutdown senders
static ACTIVE_STREAMS: Lazy<Arc<Mutex<HashMap<String, ActiveStream>>>> = Lazy::new(|| Arc::new(Mutex::new(HashMap::new())));

#[derive(Deserialize, Serialize, Clone)]
#[serde(rename_all = "camelCase")]
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
        "-vf", "fps=5",  // Set framerate to 5
        "-q:v", "7",     // JPEG quality (2-31, lower is better)
        "-an",           // No audio
        "-f", "mjpeg",   // Force MJPEG output format
        "-fps_mode", "cfr",  // Constant frame rate
        "pipe:1"         // Output to stdout
    ]);
    cmd.kill_on_drop(true);  // Ensure process is killed when dropped
    cmd.stdout(Stdio::piped());
    cmd.stderr(Stdio::piped()); // Capture stderr for debugging

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
