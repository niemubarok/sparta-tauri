use serde::{Deserialize, Serialize};
use serialport::{SerialPort, SerialPortInfo};
use std::collections::HashMap;
use std::sync::Mutex;
use std::time::Duration;
use tauri::State;

mod gpio_handler;
mod command;

use command::camera_handler;

// Gate control state
type SerialPorts = Mutex<HashMap<String, Box<dyn SerialPort + Send>>>;

#[derive(Debug, Serialize, Deserialize)]
pub struct SerialConfig {
    port: String,
    baud_rate: u32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GateResponse {
    success: bool,
    message: String,
}

// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
async fn list_serial_ports() -> Result<Vec<String>, String> {
    match serialport::available_ports() {
        Ok(ports) => {
            let port_names: Vec<String> = ports.iter().map(|p| p.port_name.clone()).collect();
            Ok(port_names)
        }
        Err(e) => Err(format!("Failed to list serial ports: {}", e)),
    }
}

#[tauri::command]
async fn open_serial_port(
    config: SerialConfig,
    ports: State<'_, SerialPorts>,
) -> Result<GateResponse, String> {
    let mut ports_guard = ports.lock().unwrap();
    
    // Close existing connection if any
    ports_guard.remove(&config.port);
    
    match serialport::new(&config.port, config.baud_rate)
        .timeout(Duration::from_millis(1000))
        .open()
    {
        Ok(port) => {
            ports_guard.insert(config.port.clone(), port);
            Ok(GateResponse {
                success: true,
                message: format!("Serial port {} opened successfully", config.port),
            })
        }
        Err(e) => Err(format!("Failed to open serial port: {}", e)),
    }
}

#[tauri::command]
async fn open_gate(
    port_name: String,
    ports: State<'_, SerialPorts>,
) -> Result<GateResponse, String> {
    let mut ports_guard = ports.lock().unwrap();
    
    match ports_guard.get_mut(&port_name) {
        Some(port) => {
            let command = b"*OUT1ON#"; // Command to open gate
            match port.write_all(command) {
                Ok(_) => Ok(GateResponse {
                    success: true,
                    message: "Gate opened successfully".to_string(),
                }),
                Err(e) => Err(format!("Failed to send open command: {}", e)),
            }
        }
        None => Err(format!("Serial port {} not found. Please open the port first.", port_name)),
    }
}

#[tauri::command]
async fn close_gate(
    port_name: String,
    ports: State<'_, SerialPorts>,
) -> Result<GateResponse, String> {
    let mut ports_guard = ports.lock().unwrap();
    
    match ports_guard.get_mut(&port_name) {
        Some(port) => {
            let command = b"*OUT1OFF#"; // Command to close gate
            match port.write_all(command) {
                Ok(_) => Ok(GateResponse {
                    success: true,
                    message: "Gate closed successfully".to_string(),
                }),
                Err(e) => Err(format!("Failed to send close command: {}", e)),
            }
        }
        None => Err(format!("Serial port {} not found. Please open the port first.", port_name)),
    }
}

#[tauri::command]
async fn close_serial_port(
    port_name: String,
    ports: State<'_, SerialPorts>,
) -> Result<GateResponse, String> {
    let mut ports_guard = ports.lock().unwrap();
    
    match ports_guard.remove(&port_name) {
        Some(_) => Ok(GateResponse {
            success: true,
            message: format!("Serial port {} closed successfully", port_name),
        }),
        None => Err(format!("Serial port {} not found", port_name)),
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(SerialPorts::default())
        .invoke_handler(tauri::generate_handler![
            greet,
            list_serial_ports,
            open_serial_port,
            open_gate,
            close_gate,
            close_serial_port,
            gpio_handler::gpio_open_gate,
            gpio_handler::gpio_close_gate,
            gpio_handler::gpio_test_pin,
            gpio_handler::gpio_test_sensor,
            gpio_handler::gpio_test_led,
            gpio_handler::gpio_test_power,
            gpio_handler::gpio_test_busy,
            gpio_handler::gpio_test_live,
            gpio_handler::gpio_test_gate_trigger,
            gpio_handler::check_gpio_availability,
            camera_handler::capture_cctv_image
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
