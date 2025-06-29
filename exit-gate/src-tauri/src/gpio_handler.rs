use serde::{Deserialize, Serialize};
use std::process::Command;
use std::time::Duration;
use tauri::command;
use log::{info, error, warn};

#[derive(Debug, Serialize, Deserialize)]
pub struct GpioConfig {
    pub pin: u8,
    pub active_high: bool, // true for active high, false for active low
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GpioResponse {
    pub success: bool,
    pub message: String,
}

// GPIO control using sysfs interface (works on Raspberry Pi)
fn set_gpio_pin(pin: u8, value: bool) -> Result<(), String> {
    // Export GPIO pin if not already exported
    let export_result = Command::new("sh")
        .arg("-c")
        .arg(&format!("echo {} > /sys/class/gpio/export", pin))
        .output();

    // Set pin direction to output
    let direction_result = Command::new("sh")
        .arg("-c")
        .arg(&format!("echo out > /sys/class/gpio/gpio{}/direction", pin))
        .output();

    if let Err(e) = direction_result {
        warn!("Failed to set GPIO {} direction: {}", pin, e);
    }

    // Set pin value
    let value_str = if value { "1" } else { "0" };
    let value_result = Command::new("sh")
        .arg("-c")
        .arg(&format!("echo {} > /sys/class/gpio/gpio{}/value", value_str, pin))
        .output();

    match value_result {
        Ok(output) => {
            if output.status.success() {
                info!("GPIO pin {} set to {}", pin, value);
                Ok(())
            } else {
                let error_msg = String::from_utf8_lossy(&output.stderr);
                Err(format!("Failed to set GPIO pin {}: {}", pin, error_msg))
            }
        }
        Err(e) => Err(format!("Command execution failed for GPIO pin {}: {}", pin, e)),
    }
}

#[command]
pub async fn gpio_open_gate(config: GpioConfig) -> Result<GpioResponse, String> {
    info!("Opening gate using GPIO pin {}", config.pin);
    
    let pin_value = if config.active_high { true } else { false };
    
    match set_gpio_pin(config.pin, pin_value) {
        Ok(_) => {
            // Auto-close after delay (configurable)
            tokio::spawn(async move {
                tokio::time::sleep(Duration::from_secs(5)).await;
                let close_value = if config.active_high { false } else { true };
                if let Err(e) = set_gpio_pin(config.pin, close_value) {
                    error!("Failed to auto-close gate: {}", e);
                }
            });
            
            Ok(GpioResponse {
                success: true,
                message: format!("Gate opened using GPIO pin {}", config.pin),
            })
        }
        Err(e) => Err(e),
    }
}

#[command]
pub async fn gpio_close_gate(config: GpioConfig) -> Result<GpioResponse, String> {
    info!("Closing gate using GPIO pin {}", config.pin);
    
    let pin_value = if config.active_high { false } else { true };
    
    match set_gpio_pin(config.pin, pin_value) {
        Ok(_) => Ok(GpioResponse {
            success: true,
            message: format!("Gate closed using GPIO pin {}", config.pin),
        }),
        Err(e) => Err(e),
    }
}

#[command]
pub async fn gpio_test_pin(config: GpioConfig) -> Result<GpioResponse, String> {
    info!("Testing GPIO pin {}", config.pin);
    
    // Test sequence: on -> off -> on -> off
    for i in 0..2 {
        let pin_value = if config.active_high { true } else { false };
        set_gpio_pin(config.pin, pin_value)?;
        tokio::time::sleep(Duration::from_millis(500)).await;
        
        let pin_value = if config.active_high { false } else { true };
        set_gpio_pin(config.pin, pin_value)?;
        tokio::time::sleep(Duration::from_millis(500)).await;
    }
    
    Ok(GpioResponse {
        success: true,
        message: format!("GPIO pin {} test completed", config.pin),
    })
}

#[command]
pub async fn check_gpio_availability() -> Result<GpioResponse, String> {
    // Check if GPIO sysfs interface is available
    let check_result = Command::new("ls")
        .arg("/sys/class/gpio")
        .output();

    match check_result {
        Ok(output) => {
            if output.status.success() {
                Ok(GpioResponse {
                    success: true,
                    message: "GPIO interface available".to_string(),
                })
            } else {
                Err("GPIO interface not available".to_string())
            }
        }
        Err(_) => Err("Failed to check GPIO availability".to_string()),
    }
}

// Alternative using rppal library (requires adding rppal dependency)
// Uncomment this section if you want to use rppal instead of sysfs

/*
use rppal::gpio::{Gpio, OutputPin, Level};
use std::sync::Mutex;
use once_cell::sync::Lazy;

static GPIO_PINS: Lazy<Mutex<std::collections::HashMap<u8, OutputPin>>> = 
    Lazy::new(|| Mutex::new(std::collections::HashMap::new()));

#[command]
pub async fn rppal_open_gate(config: GpioConfig) -> Result<GpioResponse, String> {
    let gpio = Gpio::new().map_err(|e| format!("Failed to initialize GPIO: {}", e))?;
    let mut pins = GPIO_PINS.lock().unwrap();
    
    let pin = match pins.get_mut(&config.pin) {
        Some(pin) => pin,
        None => {
            let new_pin = gpio.get(config.pin)
                .map_err(|e| format!("Failed to get GPIO pin {}: {}", config.pin, e))?
                .into_output();
            pins.insert(config.pin, new_pin);
            pins.get_mut(&config.pin).unwrap()
        }
    };
    
    let level = if config.active_high { Level::High } else { Level::Low };
    pin.set_level(level);
    
    // Auto-close after delay
    let config_clone = config.clone();
    tokio::spawn(async move {
        tokio::time::sleep(Duration::from_secs(5)).await;
        let close_level = if config_clone.active_high { Level::Low } else { Level::High };
        if let Ok(mut pins) = GPIO_PINS.lock() {
            if let Some(pin) = pins.get_mut(&config_clone.pin) {
                pin.set_level(close_level);
            }
        }
    });
    
    Ok(GpioResponse {
        success: true,
        message: format!("Gate opened using GPIO pin {} (rppal)", config.pin),
    })
}
*/
