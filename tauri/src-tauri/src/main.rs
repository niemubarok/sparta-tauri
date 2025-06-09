// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

// use std::fs;
// use std::io;
// use std::path::{Path, PathBuf};

// // Fungsi untuk menyalin file dengan handling error yang lebih baik
// fn copy_file<P: AsRef<Path>, Q: AsRef<Path>>(from: P, to: Q) -> io::Result<()> {
//     let from = from.as_ref();
//     let to = to.as_ref();
    
//     // Periksa apakah file sumber ada
//     if !from.exists() {
//         return Err(io::Error::new(
//             io::ErrorKind::NotFound, 
//             format!("Source file not found: {:?}", from)
//         ));
//     }
    
//     // Pastikan folder tujuan ada
//     if let Some(parent) = to.parent() {
//         fs::create_dir_all(parent)?;
//     }
    
//     // Salin file
//     fs::copy(from, to)?;
//     Ok(())
// }

// // Fungsi untuk menyalin DLL Python ke folder executable
// fn copy_python_dlls(python_home: &Path, app_dir: &Path) -> Result<(), String> {
//     println!("Copying Python DLLs from {:?} to {:?}", python_home, app_dir);
    
//     // Daftar DLL yang perlu disalin
//     let dll_files = vec![
//         "python310.dll", 
//         "python3.dll",
//         "vcruntime140.dll",
//         "vcruntime140_1.dll",
//         "libffi-7.dll",
//         "libcrypto-1_1.dll",
//         "libssl-1_1.dll"
//     ];
    
//     for dll in dll_files {
//         let source = python_home.join(dll);
//         let dest = app_dir.join(dll);
        
//         // Hanya salin jika file sumber ada dan tujuan belum ada atau berbeda ukuran
//         if source.exists() && (!dest.exists() || 
//             fs::metadata(&source).map(|m| m.len()).unwrap_or(0) != 
//             fs::metadata(&dest).map(|m| m.len()).unwrap_or(0)) {
            
//             println!("Copying {:?} to {:?}", source, dest);
//             if let Err(e) = copy_file(&source, &dest) {
//                 println!("Warning: Failed to copy {}: {}", dll, e);
//             } else {
//                 println!("Successfully copied {}", dll);
//             }
//         }
//     }
    
//     Ok(())
// }

fn main() {
    // Lokasi executable aplikasi
    // let app_dir = std::env::current_exe()
    //     .unwrap()
    //     .parent()
    //     .unwrap()
    //     .to_path_buf();
        
    // // Lokasi Python embeddable
    // let python_home = app_dir.join("resources").join("python-embed");
    // let python_scripts = python_home.join("Scripts");
    
    // // Salin Python DLL ke folder executable
    // if let Err(e) = copy_python_dlls(&python_home, &app_dir) {
    //     eprintln!("Error copying Python DLLs: {}", e);
    // }
    
    // // Load DLL secara eksplisit dari folder aplikasi
    // #[cfg(target_os = "windows")]
    // unsafe {
    //     // Coba load python310.dll dari folder aplikasi
    //     let python_dll_path = app_dir.join("python310.dll").to_string_lossy().to_string();
    //     let handle = winapi::um::libloaderapi::LoadLibraryA(
    //         std::ffi::CString::new(python_dll_path).unwrap().as_ptr()
    //     );
    //     if handle.is_null() {
    //         eprintln!("Failed to load Python DLL from application folder");
    //     } else {
    //         println!("Successfully loaded Python DLL from application folder");
    //     }
    // }    // Atur environment variables untuk Python
    // unsafe {
    //     // Set PYTHONHOME
    //     std::env::set_var("PYTHONHOME", python_home.to_string_lossy().to_string());
        
    //     // Set PYTHONPATH dengan semua path yang diperlukan sesuai urutan _pth file
    //     let site_packages = python_home.join("Lib").join("site-packages");
    //     let python_lib = python_home.join("Lib");
    //     let python_zip = python_home.join("python310.zip");
    //     let python_dlls = python_home.join("DLLs");
        
    //     // Buat PYTHONPATH sesuai urutan di python310._pth, hanya tambahkan path yang ada
    //     let mut paths = Vec::new();
    //     paths.push(python_zip.to_string_lossy().to_string());
    //     paths.push(python_home.to_string_lossy().to_string());
        
    //     // Tambahkan folder aplikasi ke PYTHONPATH untuk menemukan DLL
    //     paths.push(app_dir.to_string_lossy().to_string());
        
    //     if python_dlls.exists() {
    //         paths.push(python_dlls.to_string_lossy().to_string());
    //     }
    //     if python_lib.exists() {
    //         paths.push(python_lib.to_string_lossy().to_string());
    //     }
    //     if site_packages.exists() {
    //         paths.push(site_packages.to_string_lossy().to_string());
    //     }
    //       let pythonpath = paths.join(";");
    //     std::env::set_var("PYTHONPATH", pythonpath);
        
    //     // Tambahkan Python, application dir, dan Scripts ke PATH
    //     let current_path = std::env::var("PATH").unwrap_or_default();
    //     let new_path = format!("{};{};{};{}", 
    //         app_dir.to_string_lossy(),
    //         python_home.to_string_lossy(),
    //         python_scripts.to_string_lossy(),
    //         current_path);
    //     std::env::set_var("PATH", new_path);
    // }
    
    // Jalankan aplikasi Tauri
    sparta_lib::run()
}
