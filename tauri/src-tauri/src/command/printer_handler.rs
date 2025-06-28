use serde::{Deserialize, Serialize};
use tauri::command;
use log::{info, error};
use std::path::PathBuf;

#[derive(Serialize)]
pub struct PrintResponse {
    success: bool,
    message: String,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TicketData {
    ticket_number: String,
    plat_nomor: String,
    jenis_kendaraan: String,
    waktu_masuk: String,
    tarif: i32,
    company_name: String,
    gate_location: String,
    operator_name: String,
    is_paid: bool,
    barcode_data: String,
}

#[derive(Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PrinterConfig {
    printer_name: String,
    connection_type: String, // "usb", "serial", "network", "windows_driver"
    port: Option<String>,    // COM port, IP address, atau USB device path
    baud_rate: Option<u32>,  // untuk serial
}

#[derive(Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PrinterDevice {
    name: String,
    connection_type: String,
    port: String,
    status: String, // "available", "busy", "offline"
}

#[command]
pub async fn print_thermal_ticket(ticket_data: TicketData, printer_name: Option<String>) -> Result<PrintResponse, String> {
    // Debug: Log barcode data yang diterima
    info!("print_thermal_ticket received barcode_data: '{}'", ticket_data.barcode_data);
    info!("print_thermal_ticket received ticket_number: '{}'", ticket_data.ticket_number);
    
    let selected_printer = match printer_name {
        Some(name) => name,
        None => get_default_printer_name().await?
    };

    

    // Untuk EPSON TM-T82X, coba Windows driver dulu karena lebih reliable
    match print_with_driver(&ticket_data, &selected_printer).await {
        Ok(_) => Ok(PrintResponse {
            success: true,
            message: format!("Tiket berhasil dicetak ke EPSON printer: {}", selected_printer),
        }),
        Err(driver_error) => {
            info!("Driver printing failed, trying direct method: {}", driver_error);
            
            // Fallback ke direct printing
            match print_direct_to_printer(&ticket_data, &selected_printer).await {
                Ok(_) => Ok(PrintResponse {
                    success: true,
                    message: format!("Tiket berhasil dicetak langsung ke printer: {}", selected_printer),
                }),
                Err(direct_error) => {
                    error!("Both printing methods failed. Driver: {}, Direct: {}", driver_error, direct_error);
                    Err(format!("Gagal mencetak tiket. Driver: {}, Direct: {}", driver_error, direct_error))
                }
            }
        }
    }
}

// DIRECT PRINTING (NO DRIVER NEEDED)
async fn print_direct_to_printer(ticket_data: &TicketData, printer_identifier: &str) -> Result<(), String> {
    let commands = generate_raw_commands(ticket_data);
    
    // Try different connection methods
    if let Ok(_) = send_via_usb(&commands, printer_identifier).await {
        info!("Printed via USB to: {}", printer_identifier);
        return Ok(());
    }
    
    if let Ok(_) = send_via_serial(&commands, printer_identifier).await {
        info!("Printed via Serial to: {}", printer_identifier);
        return Ok(());
    }
    
    if let Ok(_) = send_via_network(&commands, printer_identifier).await {
        info!("Printed via Network to: {}", printer_identifier);
        return Ok(());
    }
    
    Err(format!("Could not connect to printer {} via any direct method", printer_identifier))
}

async fn send_via_usb(data: &[u8], device_identifier: &str) -> Result<(), String> {
    #[cfg(target_os = "windows")]
    {
        use std::fs;
        use std::io::Write;
        
        // Khusus untuk EPSON TM-T82X, coba Windows driver dulu
        if device_identifier.contains("TM-T82") || device_identifier.contains("EPSON") {
            if let Ok(_) = send_to_windows_printer(data, device_identifier).await {
                info!("Successfully sent via Windows driver to: {}", device_identifier);
                return Ok(());
            }
        }
        
        // Common USB printer paths on Windows
        let usb_paths = vec![
            "LPT1:",
            "LPT2:", 
            "LPT3:",
            "USB001",
            "USB002",
            "USB003",
        ];
        
        for path in usb_paths {
            if let Ok(mut file) = fs::OpenOptions::new()
                .write(true)
                .open(path) {
                
                if file.write_all(data).is_ok() {
                    info!("Successfully sent data via USB path: {}", path);
                    return Ok(());
                }
            }
        }
        
        // Try device path if provided
        if device_identifier.starts_with("USB") || device_identifier.contains("LPT") {
            if let Ok(mut file) = fs::OpenOptions::new()
                .write(true)
                .open(device_identifier) {
                
                if file.write_all(data).is_ok() {
                    info!("Successfully sent data via USB device: {}", device_identifier);
                    return Ok(());
                }
            }
        }
    }
    
    #[cfg(not(target_os = "windows"))]
    {
        use std::fs;
        use std::io::Write;
        
        // Common USB printer paths on Linux
        let usb_paths = vec![
            "/dev/usb/lp0",
            "/dev/usb/lp1",
            "/dev/lp0",
            "/dev/lp1",
        ];
        
        for path in usb_paths {
            if let Ok(mut file) = fs::OpenOptions::new()
                .write(true)
                .open(path) {
                
                if file.write_all(data).is_ok() {
                    info!("Successfully sent data via USB path: {}", path);
                    return Ok(());
                }
            }
        }
    }
    
    Err("No USB thermal printer found".to_string())
}

async fn send_via_serial(data: &[u8], port: &str) -> Result<(), String> {
    use std::time::Duration;
    use std::io::Write;
    
    // Default serial ports to try
    let mut ports_to_try = vec!["COM1", "COM2", "COM3", "COM4", "COM5"];
    
    // If specific port provided, try it first
    if port.starts_with("COM") || port.starts_with("/dev/tty") {
        ports_to_try.insert(0, port);
    }
    
    for port_name in ports_to_try {
        if let Ok(mut serial_port) = serialport::new(port_name, 9600)
            .timeout(Duration::from_millis(1000))
            .open() {
            
            if serial_port.write_all(data).is_ok() {
                info!("Successfully sent data via serial port: {}", port_name);
                return Ok(());
            }
        }
    }
    
    Err(format!("Could not send to serial port: {}", port))
}

async fn send_via_network(data: &[u8], address: &str) -> Result<(), String> {
    use std::net::{TcpStream, SocketAddr};
    use std::io::Write;
    use std::time::Duration;
    
    // Default network printer port
    let port = 9100;
    
    // Parse address
    let target_address = if address.contains(':') {
        address.to_string()
    } else if address.parse::<std::net::Ipv4Addr>().is_ok() {
        format!("{}:{}", address, port)
    } else {
        return Err("Invalid network address".to_string());
    };
    
    // Parse socket address with explicit error type
    let socket_addr: SocketAddr = target_address.parse()
        .map_err(|e: std::net::AddrParseError| e.to_string())?;
    
    // Try to connect
    match TcpStream::connect_timeout(&socket_addr, Duration::from_secs(3)) {
        Ok(mut stream) => {
            stream.write_all(data).map_err(|e| e.to_string())?;
            info!("Successfully sent data via network to: {}", target_address);
            Ok(())
        }
        Err(e) => Err(format!("Failed to connect to network printer {}: {}", target_address, e))
    }
}

// WINDOWS DRIVER METHOD (PRIMARY for EPSON)
async fn print_with_driver(ticket_data: &TicketData, printer_name: &str) -> Result<(), String> {
    let commands = generate_raw_commands(ticket_data);
    send_to_printer_driver(&commands, printer_name).await
}

fn generate_raw_commands(ticket_data: &TicketData) -> Vec<u8> {
    let mut commands = Vec::new();
    
    // Initialize EPSON printer
    commands.extend_from_slice(&[0x1B, 0x40]); // ESC @ (Initialize)
    
    // Set character set for EPSON
    commands.extend_from_slice(&[0x1B, 0x74, 0x00]); // ESC t 0 (CP437)
    
    // Center align
    commands.extend_from_slice(&[0x1B, 0x61, 0x01]); // ESC a 1
    
    // Title only (tanpa company name)
    commands.extend_from_slice(&[0x1B, 0x45, 0x01]); // Bold ON
    commands.extend_from_slice("UHAMKA".as_bytes());
    commands.extend_from_slice(&[0x0A]); // LF
    commands.extend_from_slice(&[0x1B, 0x45, 0x00]); // Bold OFF
    
    // Set smaller font size
    commands.extend_from_slice(&[0x1B, 0x21, 0x01]); // ESC ! 1 (Smaller font)
    
    // Gate location
    commands.extend_from_slice(ticket_data.gate_location.as_bytes());
    commands.extend_from_slice(&[0x0A]); // LF
    
    // Reset font size
    commands.extend_from_slice(&[0x1B, 0x21, 0x00]); // ESC ! 0 (Normal font)
    commands.extend_from_slice(&[0x0A]); // Additional LF for spacing
    
    // Left align for details (tanpa margin)
    commands.extend_from_slice(&[0x1B, 0x61, 0x00]); // ESC a 0 (Left align)
    
    // Ticket details (tanpa status)
    let details = format!(
        "No. Tiket: {}\n\
         Plat Nomor: {}\n\
         Jenis: {}\n\
         Masuk: {}\n\
         Tarif: Rp {}\n\
         \n",
        ticket_data.ticket_number,
        ticket_data.plat_nomor,
        ticket_data.jenis_kendaraan,
        ticket_data.waktu_masuk,
        format_currency(ticket_data.tarif),
    );
    
    commands.extend_from_slice(details.as_bytes());
    
    // Center align for barcode
    commands.extend_from_slice(&[0x1B, 0x61, 0x01]); // ESC a 1
    
    // Add barcode (optimized for EPSON TM-T82X)
    add_epson_barcode(&mut commands, &ticket_data.barcode_data);
    // add_epson_barcode_debug(&mut commands, &ticket_data.barcode_data);
    
    // Spacing after barcode
    commands.extend_from_slice(&[0x0A]); // Single LF for less spacing
    
    // Footer
    commands.extend_from_slice(&[0x1B, 0x45, 0x01]); // Bold ON
    commands.extend_from_slice("SIMPAN TIKET INI".as_bytes());
    commands.extend_from_slice(&[0x0A]); // LF
    commands.extend_from_slice("UNTUK KELUAR PARKIR".as_bytes());
    commands.extend_from_slice(&[0x1B, 0x45, 0x00]); // Bold OFF
    commands.extend_from_slice(&[0x0A, 0x0A]); // LF LF
    
    // Operator info with smaller font - Left aligned
    commands.extend_from_slice(&[0x1B, 0x61, 0x00]); // ESC a 0
    commands.extend_from_slice(&[0x1B, 0x21, 0x01]); // ESC ! 1 (Smaller font)
    
    let operator_info = format!("Operator: {}", ticket_data.operator_name);
    commands.extend_from_slice(operator_info.as_bytes());
    commands.extend_from_slice(&[0x0A]); // Reduced spacing before cut
    
    // Cut paper (EPSON specific)
    commands.extend_from_slice(&[0x1D, 0x56, 0x41, 0x03]); // GS V A 3 (partial cut)
    
    commands
}

fn add_epson_barcode(commands: &mut Vec<u8>, data: &str) {
    // Debug: Log original dan validated barcode data
    info!("Original barcode data: '{}'", data);
    
    let barcode_data = validate_barcode_data(data);
    info!("Validated barcode data: '{}'", barcode_data);
    
    if barcode_data.is_empty() {
        // If barcode data is invalid, print as text
        commands.extend_from_slice("*** BARCODE DATA KOSONG ***".as_bytes());
        commands.extend_from_slice(&[0x0A]); // LF
        return;
    }
    
    // EPSON TM-T82X barcode settings - no HRI text
    commands.extend_from_slice(&[0x1D, 0x68, 0x50]); // GS h 80 (Set barcode height)
    commands.extend_from_slice(&[0x1D, 0x77, 0x02]); // GS w 2 (Set barcode width)
    commands.extend_from_slice(&[0x1D, 0x48, 0x00]); // GS H 0 (No HRI text)
    
    // Code39 barcode (most compatible with EPSON TM-T82X)
    commands.extend_from_slice(&[0x1D, 0x6B, 0x04]); // GS k 4 (Code39)
    commands.extend_from_slice(barcode_data.as_bytes()); // Data
    commands.extend_from_slice(&[0x00]); // NULL terminator for Code39
    
    commands.extend_from_slice(&[0x0A]); // LF after barcode
}

fn validate_barcode_data(data: &str) -> String {
    // Debug: Log input data
    info!("validate_barcode_data input: '{}'", data);
    
    // For Code39: Only alphanumeric and some special characters
    let cleaned: String = data.chars()
        .filter(|c| c.is_ascii_alphanumeric() || *c == '-' || *c == '.' || *c == ' ')
        .collect();
    
    // Convert to uppercase for Code39
    let uppercase = cleaned.to_uppercase();
    
    // Debug: Log cleaned data
    info!("validate_barcode_data cleaned: '{}'", uppercase);
    
    // Extend limit for longer ticket numbers - Code39 can handle up to 43 characters on EPSON
    let result = if uppercase.len() > 30 {
        uppercase[..30].to_string()
    } else if uppercase.is_empty() {
        "NODATA".to_string() // Default value
    } else {
        uppercase
    };
    
    info!("validate_barcode_data result: '{}'", result);
    result
}


async fn send_to_printer_driver(data: &[u8], printer_name: &str) -> Result<(), String> {
    #[cfg(target_os = "windows")]
    {
        send_to_windows_printer(data, printer_name).await
    }
    
    #[cfg(not(target_os = "windows"))]
    {
        send_to_unix_printer(data, printer_name).await
    }
}

#[cfg(target_os = "windows")]
async fn send_to_windows_printer(data: &[u8], printer_name: &str) -> Result<(), String> {
    use std::ffi::CString;
    use std::ptr;
    use winapi::um::winspool::{
        OpenPrinterA, StartDocPrinterA, StartPagePrinter, 
        WritePrinter, EndPagePrinter, EndDocPrinter, ClosePrinter,
        DOC_INFO_1A
    };
    
    let printer_name_c = CString::new(printer_name).map_err(|e| e.to_string())?;
    let mut printer_handle = ptr::null_mut();
    
    unsafe {
        // Open printer
        if OpenPrinterA(
            printer_name_c.as_ptr() as *mut i8,
            &mut printer_handle, 
            ptr::null_mut()
        ) == 0 {
            return Err(format!("Failed to open EPSON printer: {}. Pastikan printer terinstall dan bisa diakses.", printer_name));
        }
        
        // Start document
        let doc_name = CString::new("Sparta Parking Ticket").map_err(|e| e.to_string())?;
        let datatype = CString::new("RAW").map_err(|e| e.to_string())?;
        let mut doc_info = DOC_INFO_1A {
            pDocName: doc_name.as_ptr() as *mut i8,
            pOutputFile: ptr::null_mut(),
            pDatatype: datatype.as_ptr() as *mut i8,
        };
        
        let job_id = StartDocPrinterA(printer_handle, 1, &mut doc_info as *mut _ as *mut _);
        if job_id == 0 {
            ClosePrinter(printer_handle);
            return Err("Failed to start document".to_string());
        }
        
        // Start page
        if StartPagePrinter(printer_handle) == 0 {
            EndDocPrinter(printer_handle);
            ClosePrinter(printer_handle);
            return Err("Failed to start page".to_string());
        }
        
        // Write data
        let mut bytes_written = 0;
        if WritePrinter(
            printer_handle,
            data.as_ptr() as *mut _,
            data.len() as u32,
            &mut bytes_written,
        ) == 0 {
            EndPagePrinter(printer_handle);
            EndDocPrinter(printer_handle);
            ClosePrinter(printer_handle);
            return Err("Failed to write to printer".to_string());
        }
        
        info!("Successfully wrote {} bytes to EPSON printer {}", bytes_written, printer_name);
        
        // Cleanup
        EndPagePrinter(printer_handle);
        EndDocPrinter(printer_handle);
        ClosePrinter(printer_handle);
    }
    
    Ok(())
}

#[cfg(not(target_os = "windows"))]
async fn send_to_unix_printer(data: &[u8], printer_name: &str) -> Result<(), String> {
    use std::process::Command;
    use std::io::Write;
    
    let mut child = Command::new("lp")
        .arg("-d")
        .arg(printer_name)
        .arg("-o")
        .arg("raw")
        .stdin(std::process::Stdio::piped())
        .spawn()
        .map_err(|e| e.to_string())?;
        
    if let Some(mut stdin) = child.stdin.take() {
        stdin.write_all(data).map_err(|e| e.to_string())?;
    }
    
    let output = child.wait().map_err(|e| e.to_string())?;
    if !output.success() {
        return Err("Failed to print via lp command".to_string());
    }
    
    Ok(())
}

fn format_currency(amount: i32) -> String {
    let amount_str = amount.to_string();
    let mut result = String::new();
    let chars: Vec<char> = amount_str.chars().collect();
    
    for (i, ch) in chars.iter().enumerate() {
        if i > 0 && (chars.len() - i) % 3 == 0 {
            result.push('.');
        }
        result.push(*ch);
    }
    
    result
}

// DISCOVERY AND MANAGEMENT FUNCTIONS

#[command]
pub async fn discover_thermal_printers() -> Result<Vec<PrinterDevice>, String> {
    let mut devices = Vec::new();
    
    // Discover installed Windows drivers (priority untuk EPSON)
    #[cfg(target_os = "windows")]
    {
        devices.extend(discover_windows_printers().await);
    }
    
    // Discover USB devices
    devices.extend(discover_usb_printers().await);
    
    // Discover Serial devices
    devices.extend(discover_serial_printers().await);
    
    if devices.is_empty() {
        devices.push(PrinterDevice {
            name: "Manual Entry".to_string(),
            connection_type: "manual".to_string(),
            port: "manual".to_string(),
            status: "available".to_string(),
        });
    }
    
    Ok(devices)
}

async fn discover_usb_printers() -> Vec<PrinterDevice> {
    let mut devices = Vec::new();
    
    #[cfg(target_os = "windows")]
    {
        let usb_paths = vec!["LPT1:", "LPT2:", "LPT3:", "USB001", "USB002"];
        
        for path in usb_paths {
            if std::fs::OpenOptions::new().write(true).open(path).is_ok() {
                devices.push(PrinterDevice {
                    name: format!("USB Thermal Printer ({})", path),
                    connection_type: "usb".to_string(),
                    port: path.to_string(),
                    status: "available".to_string(),
                });
            }
        }
    }
    
    #[cfg(not(target_os = "windows"))]
    {
        let usb_paths = vec!["/dev/usb/lp0", "/dev/usb/lp1", "/dev/lp0", "/dev/lp1"];
        
        for path in usb_paths {
            if std::path::Path::new(path).exists() {
                devices.push(PrinterDevice {
                    name: format!("USB Thermal Printer ({})", path),
                    connection_type: "usb".to_string(),
                    port: path.to_string(),
                    status: "available".to_string(),
                });
            }
        }
    }
    
    devices
}

async fn discover_serial_printers() -> Vec<PrinterDevice> {
    let mut devices = Vec::new();
    
    if let Ok(ports) = serialport::available_ports() {
        for port in ports {
            devices.push(PrinterDevice {
                name: format!("Serial Thermal Printer ({})", port.port_name),
                connection_type: "serial".to_string(),
                port: port.port_name,
                status: "available".to_string(),
            });
        }
    }
    
    devices
}

#[cfg(target_os = "windows")]
async fn discover_windows_printers() -> Vec<PrinterDevice> {
    match list_windows_printers().await {
        Ok(printers) => {
            printers.into_iter().map(|name| {
                let connection_type = if name.contains("TM-T82") || name.contains("EPSON") {
                    "epson_thermal".to_string()
                } else {
                    "windows_driver".to_string()
                };
                
                PrinterDevice {
                    name: name.clone(),
                    connection_type,
                    port: name,
                    status: "available".to_string(),
                }
            }).collect()
        }
        Err(_) => Vec::new()
    }
}

#[command]
pub async fn list_thermal_printers() -> Result<Vec<String>, String> {
    let devices = discover_thermal_printers().await?;
    Ok(devices.into_iter().map(|d| d.name).collect())
}

#[cfg(target_os = "windows")]
async fn list_windows_printers() -> Result<Vec<String>, String> {
    use winapi::um::winspool::{EnumPrintersA, PRINTER_INFO_2A, PRINTER_ENUM_LOCAL};
    use std::ptr;
    use std::ffi::CStr;
    
    unsafe {
        let mut needed = 0;
        let mut returned = 0;
        
        // Get buffer size
        EnumPrintersA(
            PRINTER_ENUM_LOCAL,
            ptr::null_mut(),
            2,
            ptr::null_mut(),
            0,
            &mut needed,
            &mut returned,
        );
        
        if needed == 0 {
            return Ok(vec!["EPSON TM-T82X".to_string()]);
        }
        
        let mut buffer: Vec<u8> = vec![0; needed as usize];
        
        if EnumPrintersA(
            PRINTER_ENUM_LOCAL,
            ptr::null_mut(),
            2,
            buffer.as_mut_ptr(),
            needed,
            &mut needed,
            &mut returned,
        ) == 0 {
            return Ok(vec!["EPSON TM-T82X".to_string()]);
        }
        
        let mut printers = Vec::new();
        let printer_info_array = buffer.as_ptr() as *const PRINTER_INFO_2A;
        
        for i in 0..returned {
            let printer_info = &*printer_info_array.offset(i as isize);
            if !printer_info.pPrinterName.is_null() {
                let name = CStr::from_ptr(printer_info.pPrinterName)
                    .to_string_lossy()
                    .to_string();
                printers.push(name);
            }
        }
        
        if printers.is_empty() {
            printers.push("EPSON TM-T82X".to_string());
        }
        
        Ok(printers)
    }
}

#[cfg(not(target_os = "windows"))]
async fn list_unix_printers() -> Result<Vec<String>, String> {
    use std::process::Command;
    
    let output = Command::new("lpstat")
        .arg("-p")
        .output()
        .map_err(|e| e.to_string())?;
        
    let output_str = String::from_utf8_lossy(&output.stdout);
    let mut printers: Vec<String> = output_str
        .lines()
        .filter_map(|line| {
            if line.starts_with("printer ") {
                line.split_whitespace().nth(1).map(|s| s.to_string())
            } else {
                None
            }
        })
        .collect();
        
    if printers.is_empty() {
        printers.push("Generic".to_string());
    }
        
    Ok(printers)
}

// CONFIGURATION MANAGEMENT

#[command]
pub async fn set_default_printer(printer_name: String) -> Result<PrintResponse, String> {
    match save_printer_config(&printer_name).await {
        Ok(_) => Ok(PrintResponse {
            success: true,
            message: format!("Printer default berhasil diset ke: {}", printer_name),
        }),
        Err(e) => Err(format!("Gagal menyimpan printer default: {}", e))
    }
}

#[command]
pub async fn get_default_printer() -> Result<String, String> {
    get_default_printer_name().await
}

async fn get_default_printer_name() -> Result<String, String> {
    match load_printer_config().await {
        Ok(config) => Ok(config.printer_name),
        Err(_) => {
            // Fallback: cari EPSON printer dulu
            let printers = list_thermal_printers().await?;
            for printer in &printers {
                if printer.contains("TM-T82") || printer.contains("EPSON") {
                    return Ok(printer.clone());
                }
            }
            // Jika tidak ada EPSON, ambil printer pertama
            if !printers.is_empty() {
                Ok(printers[0].clone())
            } else {
                Ok("Manual Entry".to_string())
            }
        }
    }
}

async fn save_printer_config(printer_name: &str) -> Result<(), String> {
    use std::fs;
    
    let connection_type = if printer_name.contains("TM-T82") || printer_name.contains("EPSON") {
        "epson_thermal".to_string()
    } else {
        "auto".to_string()
    };
    
    let config = PrinterConfig {
        printer_name: printer_name.to_string(),
        connection_type,
        port: None,
        baud_rate: None,
    };
    
    let config_json = serde_json::to_string_pretty(&config)
        .map_err(|e| format!("Failed to serialize printer config: {}", e))?;
    
    let config_path = get_printer_config_path()?;
    
    if let Some(parent) = config_path.parent() {
        fs::create_dir_all(parent)
            .map_err(|e| format!("Failed to create config directory: {}", e))?;
    }
    
    fs::write(&config_path, config_json)
        .map_err(|e| format!("Failed to write printer config: {}", e))?;
    
    info!("EPSON printer config saved: {}", printer_name);
    Ok(())
}

async fn load_printer_config() -> Result<PrinterConfig, String> {
    use std::fs;
    
    let config_path = get_printer_config_path()?;
    
    if !config_path.exists() {
        return Err("Printer config file not found".to_string());
    }
    
    let config_content = fs::read_to_string(&config_path)
        .map_err(|e| format!("Failed to read printer config: {}", e))?;
    
    let config: PrinterConfig = serde_json::from_str(&config_content)
        .map_err(|e| format!("Failed to parse printer config: {}", e))?;
    
    Ok(config)
}

fn get_printer_config_path() -> Result<PathBuf, String> {
    use std::env;
    
    let app_data = env::var("APPDATA")
        .or_else(|_| env::var("HOME"))
        .map_err(|_| "Cannot find app data directory")?;
    
    let config_dir = PathBuf::from(app_data)
        .join("Sparta Parkir")
        .join("printer_config.json");
    
    Ok(config_dir)
}

// TEST FUNCTIONS

#[command]
pub async fn test_print_barcode(barcode_data: String, printer_name: Option<String>) -> Result<PrintResponse, String> {
    let test_ticket = TicketData {
        ticket_number: "TEST-12345".to_string(),
        plat_nomor: "B 1234 ABC".to_string(),
        jenis_kendaraan: "Motor".to_string(),
        waktu_masuk: chrono::Local::now().format("%d/%m/%Y %H:%M:%S").to_string(),
        tarif: 2000,
        company_name: "TEST PARKIR SPARTA".to_string(),
        gate_location: "PINTU MASUK - TEST".to_string(),
        operator_name: "TEST OPERATOR".to_string(),
        is_paid: false,
        barcode_data,
    };
    
    print_thermal_ticket(test_ticket, printer_name).await
}

#[command]
pub async fn test_printer_connection(printer_identifier: String) -> Result<PrintResponse, String> {
    let test_data = b"EPSON TM-T82X Test\nConnection OK\n\n\n";
    
    // Untuk EPSON, coba Windows driver dulu
    if printer_identifier.contains("TM-T82") || printer_identifier.contains("EPSON") {
        if let Ok(_) = send_to_windows_printer(test_data, &printer_identifier).await {
            return Ok(PrintResponse {
                success: true,
                message: format!("EPSON Windows driver connection to {} successful", printer_identifier),
            });
        }
    }
    
    if send_via_usb(test_data, &printer_identifier).await.is_ok() {
        return Ok(PrintResponse {
            success: true,
            message: format!("USB connection to {} successful", printer_identifier),
        });
    }
    
    if send_via_serial(test_data, &printer_identifier).await.is_ok() {
        return Ok(PrintResponse {
            success: true,
            message: format!("Serial connection to {} successful", printer_identifier),
        });
    }
    
    if send_via_network(test_data, &printer_identifier).await.is_ok() {
        return Ok(PrintResponse {
            success: true,
            message: format!("Network connection to {} successful", printer_identifier),
        });
    }
    
    Err(format!("Could not connect to printer: {}", printer_identifier))
}

#[command]
pub async fn get_printer_status(printer_name: String) -> Result<String, String> {
    match test_printer_connection(printer_name.clone()).await {
        Ok(response) => Ok(response.message),
        Err(e) => Err(format!("Printer {} status: {}", printer_name, e))
    }
}

// EPSON specific functions
#[command]
pub async fn check_epson_printers() -> Result<Vec<String>, String> {
    let all_printers = list_thermal_printers().await?;
    let epson_printers: Vec<String> = all_printers
        .into_iter()
        .filter(|name| name.contains("TM-T82") || name.contains("EPSON"))
        .collect();
    
    if epson_printers.is_empty() {
        Ok(vec!["No EPSON TM-T82X printers found".to_string()])
    } else {
        Ok(epson_printers)
    }
}

fn add_epson_barcode_debug(commands: &mut Vec<u8>, data: &str) {
    let barcode_data = validate_barcode_data(data);
    
    // 1. Print data sebagai text dulu
    commands.extend_from_slice("=== DEBUG BARCODE ===".as_bytes());
    commands.extend_from_slice(&[0x0A]); // LF
    commands.extend_from_slice("Data: ".as_bytes());
    commands.extend_from_slice(barcode_data.as_bytes());
    commands.extend_from_slice(&[0x0A]); // LF
    commands.extend_from_slice("Length: ".as_bytes());
    commands.extend_from_slice(barcode_data.len().to_string().as_bytes());
    commands.extend_from_slice(&[0x0A]); // LF
    commands.extend_from_slice("====================".as_bytes());
    commands.extend_from_slice(&[0x0A, 0x0A]); // LF LF
    
    // 2. Coba multiple barcode formats
    
    // Format 1: Code39 (paling kompatibel)
    commands.extend_from_slice("Trying Code39:".as_bytes());
    commands.extend_from_slice(&[0x0A]); // LF
    commands.extend_from_slice(&[0x1D, 0x68, 0x50]); // Height
    commands.extend_from_slice(&[0x1D, 0x77, 0x02]); // Width
    commands.extend_from_slice(&[0x1D, 0x48, 0x02]); // HRI below
    commands.extend_from_slice(&[0x1D, 0x6B, 0x04]); // Code39
    commands.extend_from_slice(barcode_data.as_bytes());
    commands.extend_from_slice(&[0x00]); // NULL terminator
    commands.extend_from_slice(&[0x0A, 0x0A]); // LF LF
    
    // Format 2: Code128 
    commands.extend_from_slice("Trying Code128:".as_bytes());
    commands.extend_from_slice(&[0x0A]); // LF
    commands.extend_from_slice(&[0x1D, 0x68, 0x50]); // Height
    commands.extend_from_slice(&[0x1D, 0x77, 0x02]); // Width
    commands.extend_from_slice(&[0x1D, 0x48, 0x02]); // HRI below
    commands.extend_from_slice(&[0x1D, 0x6B, 0x49]); // Code128
    commands.push(barcode_data.len() as u8); // Length
    commands.extend_from_slice(barcode_data.as_bytes());
    commands.extend_from_slice(&[0x0A, 0x0A]); // LF LF
    
    // Format 3: Visual barcode sebagai text pattern
    commands.extend_from_slice("Visual Barcode:".as_bytes());
    commands.extend_from_slice(&[0x0A]); // LF
    // Create simple visual barcode pattern
    for ch in barcode_data.chars() {
        let code = ch as u8;
        for i in 0..8 {
            if (code >> i) & 1 == 1 {
                commands.extend_from_slice("|".as_bytes());
            } else {
                commands.extend_from_slice(" ".as_bytes());
            }
        }
    }
    commands.extend_from_slice(&[0x0A]); // LF
    commands.extend_from_slice(barcode_data.as_bytes()); // Data di bawah pattern
    commands.extend_from_slice(&[0x0A]); // LF
}