# LoL AutoCine v5.7.5 - Native Audio Helper Compile Fix

## 対応内容

v5.7.4 の C++ Build Tools 自動導入後に発生した native process-loopback helper の MSVC コンパイルエラーを修正しました。

### 修正1: Windows min/max マクロ衝突

MSVC/Windows SDK の `min` / `max` マクロが `std::min` / `std::max` と衝突し、`C2589` が発生していました。

`NOMINMAX` を `windows.h` より前に定義して、標準ライブラリの `std::min` / `std::max` をそのまま使用できるようにしました。

### 修正2: WAVEFORMATEXTENSIBLE のメンバー名

Windows SDK 10.0.26100.0 では有効ビット数のメンバー名が `wValidBitsPerSample` です。

誤っていた `wValidBits` を `wValidBitsPerSample` に修正しました。

## 想定される結果

`BUILD_AUDIO_HELPER.bat` 実行時に、今回報告された以下のエラーが解消されることを想定しています。

- C2589: `std::min` / `std::max`
- C2039: `WAVEFORMATEXTENSIBLE::Samples.wValidBits`

`_wfopen` の C4996 は警告であり、ビルド失敗の原因ではありません。

## 注意

この修正版は、Windows + MSVC の実環境でのコンパイル結果をこの実行環境から直接確認したものではありません。ユーザー環境の Visual Studio Build Tools 18 / Windows SDK 10.0.26100.0 に合わせてソースを修正しています。
