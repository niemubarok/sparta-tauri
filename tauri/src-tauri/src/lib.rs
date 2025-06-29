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
    use std::fs;
    
    // Try to get from resources first
    let resource_path: PathBuf = app_handle
        .path()
        .resolve("resources/gate.json", tauri::path::BaseDirectory::Resource)
        .map_err(|e| e.to_string())?;

    // If resources path exists, try to read it
    if resource_path.exists() {
        match std::fs::read_to_string(&resource_path) {
            Ok(file_content) => {
                match serde_json::from_str::<GateConfig>(&file_content) {
                    Ok(config) => return Ok(config.gateId),
                    Err(e) => {
                        eprintln!("Failed to parse gate.json from resources: {}", e);
                    }
                }
            },
            Err(e) => {
                eprintln!("Failed to read gate.json from resources: {}", e);
            }
        }
    }

    // Fallback: try app data directory
    let app_data_dir = app_handle
        .path()
        .app_data_dir()
        .map_err(|e| e.to_string())?;
        
    fs::create_dir_all(&app_data_dir)
        .map_err(|e| format!("Failed to create app data directory: {}", e))?;
        
    let app_data_path = app_data_dir.join("gate.json");
    
    if app_data_path.exists() {
        match std::fs::read_to_string(&app_data_path) {
            Ok(file_content) => {
                match serde_json::from_str::<GateConfig>(&file_content) {
                    Ok(config) => return Ok(config.gateId),
                    Err(e) => {
                        eprintln!("Failed to parse gate.json from app data: {}", e);
                    }
                }
            },
            Err(e) => {
                eprintln!("Failed to read gate.json from app data: {}", e);
            }
        }
    }
    
    // If file doesn't exist or is invalid, create a default one
    let default_gate_id = "gate_entry_1";
    let default_config = GateConfig {
        gateId: default_gate_id.to_string(),
    };
    
    let config_json = serde_json::to_string_pretty(&default_config)
        .map_err(|e| format!("Failed to serialize default config: {}", e))?;
    
    // Try to write to app data directory
    match std::fs::write(&app_data_path, &config_json) {
        Ok(_) => {
            println!("Created default gate.json at: {}", app_data_path.display());
        },
        Err(e) => {
            eprintln!("Failed to write default gate.json to app data: {}", e);
        }
    }
    
    // Also try to write to resources if possible (for development)
    if let Ok(resources_dir) = app_handle.path().resolve("resources", tauri::path::BaseDirectory::Resource) {
        if let Ok(_) = fs::create_dir_all(&resources_dir) {
            let _ = std::fs::write(&resource_path, &config_json);
        }
    }
    
    Ok(default_gate_id.to_string())
}

#[tauri::command]
async fn set_active_gate_id(app_handle: tauri::AppHandle, gate_id: String) -> Result<(), String> {
    use std::fs;
    
    let config = GateConfig {
        gateId: gate_id.clone(),
    };
    
    let config_json = serde_json::to_string_pretty(&config)
        .map_err(|e| format!("Failed to serialize config: {}", e))?;
    
    // Try to save to app data directory first
    let app_data_dir = app_handle
        .path()
        .app_data_dir()
        .map_err(|e| e.to_string())?;
        
    fs::create_dir_all(&app_data_dir)
        .map_err(|e| format!("Failed to create app data directory: {}", e))?;
        
    let app_data_path = app_data_dir.join("gate.json");
    
    std::fs::write(&app_data_path, &config_json)
        .map_err(|e| format!("Failed to write gate.json to app data: {}", e))?;
    
    // Also try to save to resources if possible
    if let Ok(resource_path) = app_handle.path().resolve("resources/gate.json", tauri::path::BaseDirectory::Resource) {
        if let Ok(resources_dir) = app_handle.path().resolve("resources", tauri::path::BaseDirectory::Resource) {
            let _ = fs::create_dir_all(&resources_dir);
            let _ = std::fs::write(&resource_path, &config_json);
        }
    }
    
    println!("Gate ID set to: {}", gate_id);
    Ok(())
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
            command::printer_handler::print_thermal_ticket,     // Tambahkan
            command::printer_handler::list_thermal_printers,    // Tambahkan
            command::printer_handler::test_print_barcode,
                command::printer_handler::set_default_printer,      // New
            command::printer_handler::get_default_printer,      // New
            command::printer_handler::get_printer_status,
            command::printer_handler::discover_thermal_printers,
            command::printer_handler::test_printer_connection,
            command::printer_handler::check_epson_printers,
            command::printer_handler::cancel_printer_operations,    // New
            command::printer_handler::reset_printer_operations,     // New
            command::printer_handler::get_printer_operation_status, // New

            
            get_active_gate_id,
            set_active_gate_id,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
