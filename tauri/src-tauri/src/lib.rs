#[allow(non_snake_case)]

mod command;
mod alpr;
// Modul websocket_handler dan cctv_handler telah dihapus atau digabungkan ke camera_handler


// use printpdf::{Mm, PdfDocument};
use serde::{Deserialize, Serialize};
// use std::fs;
// use std::io::BufWriter;
// use home::home_dir;
use log::info;
use rodio::{OutputStream, Sink, Decoder};
use std::io::BufReader;
use std::fs::File;
use tauri::Manager; // Untuk app_handle
use std::path::PathBuf;

#[derive(Serialize, Deserialize)]
#[allow(non_snake_case)]
struct GateConfig {
    gateId: String,
}

// Global state for serial connection
// static SERIAL_CONNECTION: Lazy<Mutex<Option<Box<dyn SerialPort>>>> = Lazy::new(|| Mutex::new(None));

#[derive(Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct TransaksiParkir {
    petugas: String,
    id_pintu_keluar: String,
    plat_nomor: String,
    jns_kendaraan: String,
    waktu_masuk: String,
    waktu_keluar: String,
    lama_parkir: String,
    biaya_parkir: String,
}

#[tauri::command]
#[allow(non_snake_case)]
async fn play_audio(filePath: String) -> Result<(), String> {
    // Check if file extension is audio
    let valid_extensions = ["mp3", "wav", "ogg", "flac"];
    let extension = std::path::Path::new(&filePath)
        .extension()
        .and_then(|ext| ext.to_str())
        .ok_or("Invalid file extension")?
        .to_lowercase();

    if !valid_extensions.contains(&extension.as_str()) {
        return Err("Not a supported audio file format".to_string());
    }

    // Get a output stream handle to the default physical sound device
    let (_stream, stream_handle) = OutputStream::try_default()
        .map_err(|e| e.to_string())?;

    // Create a new sink
    let sink = Sink::try_new(&stream_handle)
        .map_err(|e| e.to_string())?;

    // Load and decode the audio file
    let file = File::open(filePath)
        .map_err(|e| e.to_string())?;
    let reader = BufReader::new(file);
    let source = Decoder::new(reader)
        .map_err(|e| e.to_string())?;

    // Play the audio
    sink.append(source);
    sink.sleep_until_end();

    Ok(())
}

#[tauri::command]
async fn get_active_gate_id(app_handle: tauri::AppHandle) -> Result<String, String> {
    let resource_path: PathBuf = app_handle
        .path()
        .resolve("resources/gate.json", tauri::path::BaseDirectory::Resource)
        .map_err(|e| e.to_string())?;

    if !resource_path.exists() {
        return Err("gate.json not found in resources".to_string());
    }

    let file_content = std::fs::read_to_string(resource_path)
        .map_err(|e| format!("Failed to read gate.json: {}", e))?;

    let config: GateConfig = serde_json::from_str(&file_content)
        .map_err(|e| format!("Failed to parse gate.json: {}", e))?;

    Ok(config.gateId)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info"))
        .format_timestamp_secs()
        .init();

    info!("Starting application...");

    let alpr_engine = alpr::AlprEngine::new();
    
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(alpr_engine)
        .invoke_handler(tauri::generate_handler![
            play_audio,
            command::serial_handler::create_serial_port,
            command::serial_handler::listen_to_serial,
            command::serial_handler::write_serial,
            command::serial_handler::close_serial,
            command::serial_handler::is_port_opened,
            command::camera_handler::capture_cctv_image,
            command::camera_handler::start_rtsp_live_stream,
            command::camera_handler::stop_rtsp_live_stream,
            command::alpr_handler::process_alpr_image,
            get_active_gate_id,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
