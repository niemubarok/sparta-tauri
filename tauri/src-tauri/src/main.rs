// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    // Trae AI Note: A previous attempt to modify Tauri invoke_handlers failed.
    // The specific line to update was not found in the current file structure.
    // Searched for line:
    //         .invoke_handler(tauri::generate_handler![capture_cctv_image])
    // Intended to replace with (adding start_rtsp_live_stream, stop_rtsp_live_stream):
    //         .invoke_handler(tauri::generate_handler![capture_cctv_image, start_rtsp_live_stream, stop_rtsp_live_stream])
    // This automated modification could not be applied as the `tauri::Builder` pattern was not directly visible.
    sparta_lib::run()
}
