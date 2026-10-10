# Native LoL Process Loopback Helper

This helper captures audio rendered by the specified Windows process and its child-process tree using Windows Application Loopback / WASAPI.

The Python application launches it with:

    lol_audio_helper.exe <LoL PID> <output.wav> <seconds>

The helper prints `START` after the process-loopback audio client has been activated and prints `STOP` after the WAV is finalized.

It does not use desktop-wide loopback and does not mute other applications.

Requirements:
- Windows 10 build 20348 or later
- Windows SDK with `audioclientactivationparams.h`
- Microsoft C++ build tools

The implementation follows the public Windows process-loopback API documented by Microsoft and the architecture of Microsoft's Application Loopback sample.
