<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This project is a Tauri + Quasar (Vue 3 + TypeScript) application for an exit gate system. It must:
- Accept input from a USB barcode scanner (as keyboard input)
- On scan, check local PouchDB for a matching transaction (same schema as entry gate)
- If found, send a serial command to open the gate (via Tauri backend, serialport)
- Update the transaction status in the database
- Be optimized for Raspberry Pi deployment
- Use the same transaction schema and logic as the entry gate system
- get settings from database to configure the serial port and other parameters
- capture image from webcam and cctv camera, then upload to the server with the transaction data update


When generating code, prefer modular, maintainable, and testable patterns. Use Quasar UI components for the frontend. Use Tauri commands for serial communication. Use PouchDB for local database operations.

gunakan template ini
https://github.com/taiyuuki/tauri-quasar

selalu gunakan pnpm