@echo off
echo Installing FFmpeg for Windows...

:: Create ffmpeg directory if it doesn't exist
if not exist "ffmpeg" mkdir ffmpeg

:: Download FFmpeg
powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg.zip'}"

:: Extract FFmpeg
powershell -Command "& {Expand-Archive -Path 'ffmpeg.zip' -DestinationPath 'ffmpeg' -Force}"

:: Move FFmpeg files to the correct location
move "ffmpeg\ffmpeg-master-latest-win64-gpl\bin\*" "ffmpeg\"

:: Clean up
rmdir /s /q "ffmpeg\ffmpeg-master-latest-win64-gpl"
del ffmpeg.zip

echo FFmpeg installation completed!
echo FFmpeg is now available in the ffmpeg directory 