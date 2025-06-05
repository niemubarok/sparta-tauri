use log::info;
use tauri::{AppHandle, State};
use tauri::Emitter;
use crate::alpr::{AlprEngine, AlprResult};

#[tauri::command]
pub async fn process_alpr_image(
    app_handle: AppHandle,
    state: State<'_, AlprEngine>,
    base64_image: String,
    camera_id: String,
) -> Result<AlprResult, String> {
    info!("Processing ALPR image for camera: {}", camera_id);
    
    let result = state.process_image(&base64_image, &camera_id).await;
    
    // Emit detected plates to frontend
    if result.success && !result.detected_plates.is_empty() {
        for plate in &result.detected_plates {
            let _ = app_handle.emit("plate-detected", plate);
            info!("Detected plate: {} from camera {}", plate.plate_number, plate.camera_id);
        }
    }
    
    Ok(result)
}