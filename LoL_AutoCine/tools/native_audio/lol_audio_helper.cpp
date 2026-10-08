#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <mmdeviceapi.h>
#include <audioclient.h>
#include <audioclientactivationparams.h>
#include <propidl.h>
#include <wrl.h>
#include <wrl/implements.h>
#include <ks.h>
#include <ksmedia.h>
#include <avrt.h>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <string>
#include <thread>
#include <atomic>
#include <algorithm>
#include <cmath>

#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "mmdevapi.lib")
#pragma comment(lib, "avrt.lib")

using Microsoft::WRL::ComPtr;
using Microsoft::WRL::RuntimeClass;
using Microsoft::WRL::RuntimeClassFlags;
using Microsoft::WRL::ClassicCom;
using Microsoft::WRL::FtmBase;

#ifndef VIRTUAL_AUDIO_DEVICE_PROCESS_LOOPBACK
#define VIRTUAL_AUDIO_DEVICE_PROCESS_LOOPBACK L"VAD\\Process_Loopback"
#endif

static void print_hr(const char* where, HRESULT hr) {
    std::fprintf(stderr, "%s failed: 0x%08lX\n", where, (unsigned long)hr);
}

class ActivationHandler final : public RuntimeClass<RuntimeClassFlags<ClassicCom>, IActivateAudioInterfaceCompletionHandler, FtmBase> {
public:
    HRESULT STDMETHODCALLTYPE ActivateCompleted(IActivateAudioInterfaceAsyncOperation* operation) override {
        HRESULT hr = E_FAIL;
        if (operation) {
            IUnknown* raw = nullptr;
            HRESULT callHr = operation->GetActivateResult(&m_result, &raw);
            if (SUCCEEDED(callHr) && SUCCEEDED(m_result) && raw) {
                callHr = raw->QueryInterface(IID_PPV_ARGS(&m_client));
            }
            if (raw) raw->Release();
            hr = callHr;
        }
        m_hr = hr;
        SetEvent(m_event);
        return S_OK;
    }

    void set_event(HANDLE h) { m_event = h; }
    HRESULT result() const { return m_hr; }
    ComPtr<IAudioClient> client() const { return m_client; }

private:
    HANDLE m_event = nullptr;
    HRESULT m_hr = E_FAIL;
    ComPtr<IAudioClient> m_client;
    HRESULT m_result = E_FAIL;
};

#pragma pack(push, 1)
struct WavHeader {
    char riff[4]; uint32_t riffSize; char wave[4];
    char fmt[4]; uint32_t fmtSize;
    uint16_t audioFormat; uint16_t channels; uint32_t sampleRate;
    uint32_t byteRate; uint16_t blockAlign; uint16_t bitsPerSample;
    char data[4]; uint32_t dataSize;
};
#pragma pack(pop)

static bool write_wav_header(FILE* f, uint16_t ch, uint32_t rate, uint16_t bits, uint32_t dataSize) {
    WavHeader h{};
    std::memcpy(h.riff, "RIFF", 4); std::memcpy(h.wave, "WAVE", 4);
    std::memcpy(h.fmt, "fmt ", 4); std::memcpy(h.data, "data", 4);
    h.riffSize = 36 + dataSize; h.fmtSize = 16; h.audioFormat = 1;
    h.channels = ch; h.sampleRate = rate; h.bitsPerSample = bits;
    h.blockAlign = uint16_t(ch * bits / 8); h.byteRate = rate * h.blockAlign;
    h.dataSize = dataSize;
    return std::fwrite(&h, sizeof(h), 1, f) == 1;
}

static bool write_silence_pcm16(FILE* f, size_t samples) {
    static const int16_t zeros[4096] = {};
    while (samples) {
        size_t n = std::min(samples, size_t(4096));
        if (std::fwrite(zeros, sizeof(int16_t), n, f) != n) return false;
        samples -= n;
    }
    return true;
}

static int16_t float_to_pcm(float x) {
    x = std::max(-1.0f, std::min(1.0f, x));
    return (int16_t)std::lrintf(x * 32767.0f);
}

static int16_t sample_to_pcm16(const BYTE* p, WORD bits, bool isFloat) {
    if (isFloat && bits == 32) {
        float x; std::memcpy(&x, p, sizeof(x)); return float_to_pcm(x);
    }
    if (bits == 16) { int16_t x; std::memcpy(&x, p, sizeof(x)); return x; }
    if (bits == 24) {
        int32_t x = (int32_t(p[0]) | (int32_t(p[1]) << 8) | (int32_t(p[2]) << 16));
        if (x & 0x00800000) x |= 0xFF000000;
        return (int16_t)(x >> 8);
    }
    if (bits == 32) {
        int32_t x; std::memcpy(&x, p, sizeof(x)); return (int16_t)(x >> 16);
    }
    return 0;
}

static bool capture(DWORD pid, const wchar_t* output, double seconds) {
    HANDLE activateDone = CreateEventW(nullptr, TRUE, FALSE, nullptr);
    if (!activateDone) { print_hr("CreateEvent", HRESULT_FROM_WIN32(GetLastError())); return false; }

    auto handler = Microsoft::WRL::Make<ActivationHandler>();
    if (!handler) { CloseHandle(activateDone); return false; }
    handler->set_event(activateDone);

    AUDIOCLIENT_ACTIVATION_PARAMS params{};
    params.ActivationType = AUDIOCLIENT_ACTIVATION_TYPE_PROCESS_LOOPBACK;
    params.ProcessLoopbackParams.TargetProcessId = pid;
    params.ProcessLoopbackParams.ProcessLoopbackMode = PROCESS_LOOPBACK_MODE_INCLUDE_TARGET_PROCESS_TREE;

    PROPVARIANT pv{};
    pv.vt = VT_BLOB;
    pv.blob.cbSize = sizeof(params);
    pv.blob.pBlobData = reinterpret_cast<BYTE*>(&params);

    ComPtr<IActivateAudioInterfaceAsyncOperation> op;
    HRESULT hr = ActivateAudioInterfaceAsync(
        VIRTUAL_AUDIO_DEVICE_PROCESS_LOOPBACK,
        __uuidof(IAudioClient),
        &pv,
        handler.Get(),
        &op);
    if (FAILED(hr)) { print_hr("ActivateAudioInterfaceAsync", hr); CloseHandle(activateDone); return false; }

    DWORD wait = WaitForSingleObject(activateDone, 10000);
    if (wait != WAIT_OBJECT_0) {
        std::fprintf(stderr, "Activation timeout\n"); CloseHandle(activateDone); return false;
    }
    hr = handler->result();
    if (FAILED(hr)) { print_hr("ActivateCompleted", hr); CloseHandle(activateDone); return false; }
    ComPtr<IAudioClient> client = handler->client();
    CloseHandle(activateDone);
    if (!client) { std::fprintf(stderr, "No IAudioClient returned\n"); return false; }

    // IMPORTANT:
    // VIRTUAL_AUDIO_DEVICE_PROCESS_LOOPBACK may return E_NOTIMPL from
    // IAudioClient::GetMixFormat on supported Windows versions. This is a
    // known behavior of Microsoft's ApplicationLoopback sample as well.
    // Use the capture format recommended by the Microsoft sample instead.
    WAVEFORMATEX captureFormat{};
    captureFormat.wFormatTag = WAVE_FORMAT_PCM;
    captureFormat.nChannels = 2;
    captureFormat.nSamplesPerSec = 44100;
    captureFormat.wBitsPerSample = 16;
    captureFormat.nBlockAlign = captureFormat.nChannels * captureFormat.wBitsPerSample / 8;
    captureFormat.nAvgBytesPerSec = captureFormat.nSamplesPerSec * captureFormat.nBlockAlign;
    captureFormat.cbSize = 0;

    const WORD channels = captureFormat.nChannels;
    const DWORD rate = captureFormat.nSamplesPerSec;
    const WORD bits = captureFormat.wBitsPerSample;
    const bool isFloat = false;

    // Ask WASAPI to convert the process-loopback stream to our fixed PCM16 format.
    REFERENCE_TIME bufferDuration = 10000000; // 1 second
    hr = client->Initialize(AUDCLNT_SHAREMODE_SHARED,
        AUDCLNT_STREAMFLAGS_LOOPBACK | AUDCLNT_STREAMFLAGS_EVENTCALLBACK | AUDCLNT_STREAMFLAGS_AUTOCONVERTPCM,
        bufferDuration, 0, &captureFormat, nullptr);
    if (FAILED(hr)) { print_hr("IAudioClient::Initialize", hr); return false; }

    // The capture client is obtained from the activated IAudioClient after Initialize.
    // Keep it alive for the entire capture loop; ComPtr releases it automatically.
    ComPtr<IAudioCaptureClient> captureClient;
    hr = client.As(&captureClient);
    if (FAILED(hr) || !captureClient) {
        print_hr("Query IAudioCaptureClient", FAILED(hr) ? hr : E_NOINTERFACE);
        return false;
    }

    HANDLE sampleEvent = CreateEventW(nullptr, FALSE, FALSE, nullptr);
    if (!sampleEvent) { return false; }
    hr = client->SetEventHandle(sampleEvent);
    if (FAILED(hr)) { print_hr("SetEventHandle", hr); CloseHandle(sampleEvent); return false; }

    FILE* f = nullptr;
    if (_wfopen_s(&f, output, L"wb") != 0) f = nullptr;
    if (!f) { std::fwprintf(stderr, L"Cannot open output: %ls\n", output); CloseHandle(sampleEvent); return false; }

    // Placeholder header; patched after capture.
    WavHeader placeholder{};
    std::memcpy(placeholder.riff, "RIFF", 4); std::memcpy(placeholder.wave, "WAVE", 4);
    std::memcpy(placeholder.fmt, "fmt ", 4); std::memcpy(placeholder.data, "data", 4);
    placeholder.fmtSize = 16; placeholder.audioFormat = 1; placeholder.channels = channels;
    placeholder.sampleRate = rate; placeholder.bitsPerSample = 16; placeholder.blockAlign = uint16_t(channels * 2);
    placeholder.byteRate = rate * placeholder.blockAlign;
    std::fwrite(&placeholder, sizeof(placeholder), 1, f);

    hr = client->Start();
    if (FAILED(hr)) { print_hr("IAudioClient::Start", hr); std::fclose(f); DeleteFileW(output); CloseHandle(sampleEvent); return false; }

    std::printf("START\n"); std::fflush(stdout);
    const ULONGLONG deadline = GetTickCount64() + (ULONGLONG)std::max(0.05, seconds) * 1000ULL;
    uint64_t dataBytes = 0;
    bool ok = true;
    bool stopRequested = false;
    HANDLE stdinHandle = GetStdHandle(STD_INPUT_HANDLE);

    HANDLE handles[1] = { sampleEvent };
    DWORD avrtTask = 0;
    HANDLE avrt = AvSetMmThreadCharacteristicsW(L"Pro Audio", &avrtTask);

    while (!stopRequested && GetTickCount64() < deadline) {
        if (stdinHandle != INVALID_HANDLE_VALUE && stdinHandle != nullptr) {
            DWORD avail = 0;
            if (PeekNamedPipe(stdinHandle, nullptr, 0, nullptr, &avail, nullptr) && avail > 0) {
                char cmd[64] = {}; DWORD got = 0;
                if (ReadFile(stdinHandle, cmd, sizeof(cmd) - 1, &got, nullptr) && got > 0) {
                    cmd[got] = 0;
                    if (strstr(cmd, "STOP") != nullptr) stopRequested = true;
                }
            }
        }
        DWORD w = WaitForMultipleObjects(1, handles, FALSE, 100);
        if (w == WAIT_FAILED) { ok = false; break; }

        UINT32 frames = 0;
        while (SUCCEEDED(captureClient->GetNextPacketSize(&frames)) && frames > 0) {
            BYTE* data = nullptr; DWORD flags = 0; UINT64 devPos = 0, qpc = 0; UINT32 n = 0;
            hr = captureClient->GetBuffer(&data, &n, &flags, &devPos, &qpc);
            if (FAILED(hr)) { print_hr("GetBuffer", hr); ok = false; break; }
            if (flags & AUDCLNT_BUFFERFLAGS_SILENT) {
                if (!write_silence_pcm16(f, size_t(n) * channels)) ok = false;
                dataBytes += uint64_t(n) * channels * 2;
            } else {
                size_t srcStride = captureFormat.nBlockAlign;
                for (UINT32 i = 0; i < n && ok; ++i) {
                    for (WORD c = 0; c < channels; ++c) {
                        const BYTE* sp = data + size_t(i) * srcStride + size_t(c) * (captureFormat.wBitsPerSample / 8);
                        int16_t s = sample_to_pcm16(sp, captureFormat.wBitsPerSample, isFloat);
                        if (std::fwrite(&s, sizeof(s), 1, f) != 1) ok = false;
                    }
                }
                dataBytes += uint64_t(n) * channels * 2;
            }
            captureClient->ReleaseBuffer(n);
            if (!ok) break;
        }
        if (!ok) break;
    }

    client->Stop();
    if (avrt) AvRevertMmThreadCharacteristics(avrt);

    // Drain one last time.
    for (;;) {
        UINT32 frames = 0;
        if (FAILED(captureClient->GetNextPacketSize(&frames)) || frames == 0) break;
        BYTE* data = nullptr; DWORD flags = 0; UINT64 devPos = 0, qpc = 0; UINT32 n = 0;
        if (FAILED(captureClient->GetBuffer(&data, &n, &flags, &devPos, &qpc))) { ok = false; break; }
        if (flags & AUDCLNT_BUFFERFLAGS_SILENT) {
            if (!write_silence_pcm16(f, size_t(n) * channels)) ok = false;
        } else {
            size_t srcStride = captureFormat.nBlockAlign;
            for (UINT32 i = 0; i < n && ok; ++i) for (WORD c = 0; c < channels; ++c) {
                const BYTE* sp = data + size_t(i) * srcStride + size_t(c) * (captureFormat.wBitsPerSample / 8);
                int16_t s = sample_to_pcm16(sp, captureFormat.wBitsPerSample, isFloat);
                if (std::fwrite(&s, sizeof(s), 1, f) != 1) ok = false;
            }
        }
        dataBytes += uint64_t(n) * channels * 2;
        captureClient->ReleaseBuffer(n);
        if (!ok) break;
    }

    if (dataBytes > 0xFFFFFFFFULL - 36) ok = false;
    if (ok) {
        std::fflush(f);
        std::fseek(f, 0, SEEK_SET);
        ok = write_wav_header(f, channels, rate, 16, (uint32_t)dataBytes);
    }
    std::fclose(f);
    CloseHandle(sampleEvent);
   

    if (!ok) { DeleteFileW(output); std::fprintf(stderr, "Capture failed\n"); return false; }
    std::printf("STOP\n"); std::fflush(stdout);
    return true;
}

int wmain(int argc, wchar_t** argv) {
    if (argc != 4) {
        std::fwprintf(stderr, L"Usage: lol_audio_helper.exe <pid> <output.wav> <seconds>\n");
        return 2;
    }
    DWORD pid = wcstoul(argv[1], nullptr, 10);
    double seconds = wcstod(argv[3], nullptr);
    if (!pid || seconds <= 0.0 || seconds > 3600.0) {
        std::fprintf(stderr, "Invalid arguments\n"); return 2;
    }
    HRESULT hr = CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    if (FAILED(hr)) { print_hr("CoInitializeEx", hr); return 3; }
    bool ok = capture(pid, argv[2], seconds);
    CoUninitialize();
    return ok ? 0 : 1;
}
