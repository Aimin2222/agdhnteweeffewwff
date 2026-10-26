# ソースから再ビルド
ReferenceDemo.csをWindows .NET Frameworkのcsc.exeでx64 winexeとしてcompile。System.Windows.Forms/System.Drawing/System.Web.Extensionsと同梱Core/WinForms DLLをreferenceへ指定し、ReferenceDemo.exe.manifestを埋め込む。SDK公式version1.0.3856.49、net462、x64 loaderを使用。通常UIを手動で開く場合はv1.exe。--evidenceは独立QA profile/合成fixture/自作captureのみを実行し終了する。
SDKの権利表記はlicenses/を保持。Runtime本体、参照ソフト、第三者UI素材は同梱していない。外部のshell/任意JSをUIから実行するbridgeは追加しない。
