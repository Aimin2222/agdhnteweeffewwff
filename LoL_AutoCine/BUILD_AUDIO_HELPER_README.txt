LoL AutoCine - Native Audio Helper

This version fixes the previous helper-build flow.

1. You normally only need to run 00_AUDIO_TEST.bat.
2. If tools\bin\lol_audio_helper.exe is missing, it automatically runs BUILD_AUDIO_HELPER.bat.
3. The build result is written to diagnostics\native_audio_build.log.
4. The helper EXE is verified before the audio test starts.
5. If the build fails, the audio test is NOT started.

Requirements for building the native helper:
- Windows
- Visual Studio Build Tools / Visual Studio with Desktop development with C++
- Windows 10/11 SDK

The native helper captures audio using Windows Process Loopback for the target LoL process tree. It is intended to avoid mixing unrelated desktop application audio.
