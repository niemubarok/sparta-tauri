use serialport::SerialPort;
use std::sync::Mutex;
use once_cell::sync::Lazy;
use log::{info, error};
use std::time::Duration;

use tauri::command; // Tambahkan ini

// Global state for serial connection
static SERIAL_CONNECTION: Lazy<Mutex<Option<Box<dyn SerialPort>>>> = Lazy::new(|| Mutex::new(None));

#[command]
pub async fn create_serial_port(port_name: String) -> Result<(), String> {
    let port = serialport::new(&port_name, 9600)
        .timeout(Duration::from_millis(50))
        .data_bits(serialport::DataBits::Eight)
        .parity(serialport::Parity::None)
        .stop_bits(serialport::StopBits::One)
        .flow_control(serialport::FlowControl::None)
        .open()
        .map_err(|e| e.to_string())?;
    
    let mut connection = SERIAL_CONNECTION.lock().map_err(|e| e.to_string())?;
    *connection = Some(port);

    info!("Serial port {} opened successfully with 9600 baud rate", port_name);
    Ok(())
}

#[command]
pub async fn write_serial(data: String) -> Result<(), String> {
    let mut connection = SERIAL_CONNECTION.lock().map_err(|e| e.to_string())?;
    if let Some(port) = connection.as_mut() {
        port.write_all(data.as_bytes()).map_err(|e| e.to_string())?;
        println!("Data sent to serial port: {}", data);
        Ok(())
    } else {
        Err("Serial port not initialized".to_string())
    }
}

#[command]
pub async fn listen_to_serial(_port_name: String) -> Result<String, String> {
    let mut connection = SERIAL_CONNECTION.lock().map_err(|e| e.to_string())?;
    
    if connection.is_none() {
        error!("Serial port not initialized");
        return Err("Serial port not initialized".to_string());
    }
    
    if let Some(port) = connection.as_mut() {
        let mut buffer = [0u8; 1024];
        match port.read(&mut buffer) {
            Ok(bytes_read) if bytes_read > 0 => {
                match String::from_utf8(buffer[..bytes_read].to_vec()) {
                    Ok(received) => {
                        info!("Received data: {}", received);
                        Ok(received)
                    },
                    Err(_) => {
                        let hex = buffer[..bytes_read]
                            .iter()
                            .map(|b| format!("{:02X}", b))
                            .collect::<String>();
                        info!("Received hex data: {}", hex);
                        Ok(hex)
                    }
                }
            },
            Ok(0) => Ok("".to_string()),
            Ok(_) => Err("Invalid read size".to_string()),
            Err(ref e) if e.kind() == std::io::ErrorKind::TimedOut => Ok("".to_string()),
            Err(e) => {
                error!("Serial read error: {}", e);
                Err(e.to_string())
            }
        }
    } else {
        Err("Serial port not initialized".to_string())
    }
}

#[command]
pub async fn close_serial() -> Result<(), String> {
    let mut connection = SERIAL_CONNECTION.lock().map_err(|e| e.to_string())?;
    *connection = None;
    Ok(())
}

#[command]
pub async fn is_port_opened() -> bool {
    SERIAL_CONNECTION.lock()
        .map(|connection| connection.is_some())
        .unwrap_or(false)
}