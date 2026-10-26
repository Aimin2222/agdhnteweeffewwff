using System;
using System.IO;
using System.Text;
using System.Drawing;
using System.Windows.Forms;
using System.Threading.Tasks;
using System.Web.Script.Serialization;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

// Research-only local-content host. No AutoCine/LoL/backend integration.
public sealed class ReferenceDemo : Form {
 readonly WebView2 view = new WebView2();
 readonly JavaScriptSerializer json = new JavaScriptSerializer { MaxJsonLength = 2200000 };
 readonly string root,session,captures;
 readonly bool evidence=Array.IndexOf(Environment.GetCommandLineArgs(),"--evidence")>=0;
 Size restoreSize; Point restoreLocation; double restoreZoom=1; bool capturing=false;
 const string Host="autocine-ui-research-20261027.invalid";
 public ReferenceDemo(){
  root=Directory.GetParent(AppDomain.CurrentDomain.BaseDirectory.TrimEnd(Path.DirectorySeparatorChar)).FullName;
  bool qa=Path.GetFileNameWithoutExtension(Application.ExecutablePath).EndsWith("_QA")||evidence;
  session=Path.Combine(root,qa?"_session_qa":"_session");captures=Path.Combine(root,"screenshots");
  Directory.CreateDirectory(session);
  Text="AutoCine • R1 / R2 UI研究デモ — LoL未接続"+(qa?" [QA]":"");
  StartPosition=FormStartPosition.CenterScreen;ClientSize=new Size(1366,830);MinimumSize=new Size(1200,700);
  if(evidence){StartPosition=FormStartPosition.Manual;Location=new Point(-5000,0);ShowInTaskbar=false;}
  AutoScaleMode=AutoScaleMode.None;BackColor=Color.FromArgb(237,241,245);
  view.Dock=DockStyle.Fill;Controls.Add(view);
  Shown+=async (s,e)=>await Initialize();
 }
 async Task Initialize(){
  try {
   string version=CoreWebView2Environment.GetAvailableBrowserVersionString();
   var env=await CoreWebView2Environment.CreateAsync(null,Path.Combine(session,"webview2"));
   await view.EnsureCoreWebView2Async(env);
   view.CoreWebView2.SetVirtualHostNameToFolderMapping(Host,Path.Combine(root,"demo"),CoreWebView2HostResourceAccessKind.DenyCors);
   view.CoreWebView2.NavigationStarting+=(s,e)=>{Uri u; if(!Uri.TryCreate(e.Uri,UriKind.Absolute,out u)||u.Scheme!="https"||u.Host!=Host)e.Cancel=true;};
   view.CoreWebView2.NewWindowRequested+=(s,e)=>{e.Handled=true;};
   view.CoreWebView2.PermissionRequested+=(s,e)=>{e.State=CoreWebView2PermissionState.Deny;};
   view.CoreWebView2.WebMessageReceived+=async (s,e)=>await Message(e);
   view.CoreWebView2.ProcessFailed+=(s,e)=>File.WriteAllText(Path.Combine(session,"process-error.txt"),e.ProcessFailedKind.ToString());
   File.WriteAllText(Path.Combine(session,"host_environment.json"),json.Serialize(new {runtime=version,host="WinForms .NET Framework x64",sdk="1.0.3856.49",backend="NOT_CONNECTED",windowsSettingsChanged=false}),Encoding.UTF8);
   view.Source=new Uri("https://"+Host+"/index.html");
  }catch(Exception ex){File.WriteAllText(Path.Combine(session,"startup-error.txt"),ex.ToString(),Encoding.UTF8);MessageBox.Show(this,"研究デモを起動できません。WebView2 Runtime と .NET Framework 4.6.2以降を確認してください。\n自動インストールやWindows設定変更は行いません。\n\n"+ex.Message,"AutoCine UI研究",MessageBoxButtons.OK,MessageBoxIcon.Information);}
 }
 string Str(Dictionary<string,object>d,string k){return d.ContainsKey(k)?Convert.ToString(d[k]):"";}
 async Task Message(CoreWebView2WebMessageReceivedEventArgs e){
  if(!e.Source.StartsWith("https://"+Host+"/",StringComparison.Ordinal))return;
  try {
   if(e.WebMessageAsJson.Length>2100000)throw new Exception("Message too large");
   var d=json.Deserialize<Dictionary<string,object>>(e.WebMessageAsJson);string type=Str(d,"type");
   if(type=="demo-ready"){File.WriteAllText(Path.Combine(session,"demo-ready.json"),e.WebMessageAsJson,Encoding.UTF8);if(evidence){await Task.Delay(350);await view.ExecuteScriptAsync("automaticEvidence()");}}
   else if(type=="state-snapshot")File.WriteAllText(Path.Combine(session,"last-ui-state.json"),e.WebMessageAsJson,Encoding.UTF8);
   else if(type=="integration-report")File.WriteAllText(Path.Combine(session,"integration-tests.json"),e.WebMessageAsJson,Encoding.UTF8);
   else if(type=="test-report")File.WriteAllText(Path.Combine(session,"self-test.json"),e.WebMessageAsJson,Encoding.UTF8);
   else if(type=="save-json"){
    using(var save=new SaveFileDialog()){save.Title="研究デモのJSONを保存";save.Filter="研究JSON (*.json)|*.json";save.FileName=Path.GetFileName(Str(d,"name"));save.InitialDirectory=session;save.OverwritePrompt=true;if(save.ShowDialog(this)==DialogResult.OK)File.WriteAllText(save.FileName,Str(d,"content"),new UTF8Encoding(false));}
   }
   else if(type=="capture-begin"){
    if(capturing)throw new Exception("Capture already running");capturing=true;if(evidence)FormBorderStyle=FormBorderStyle.None;restoreSize=ClientSize;restoreLocation=Location;restoreZoom=view.ZoomFactor;Directory.CreateDirectory(captures);
   }
   else if(type=="capture-prepare"&&capturing){
    string size=Str(d,"size"),name=Str(d,"name");ValidateName(name);
    if(size!="1920x1080"&&size!="1366x768")throw new Exception("Unsupported capture size");
    var parts=size.Split('x');WindowState=FormWindowState.Normal;
    var rawDpr=Double.Parse(await view.ExecuteScriptAsync("window.devicePixelRatio"),System.Globalization.CultureInfo.InvariantCulture)/view.ZoomFactor;
    view.ZoomFactor=1/rawDpr;var targetSize=new Size(Int32.Parse(parts[0]),Int32.Parse(parts[1]));view.Dock=DockStyle.None;ClientSize=targetSize;view.Size=targetSize;
    await Task.Delay(150);
    view.CoreWebView2.PostWebMessageAsJson(json.Serialize(new {type="capture-size-ready",name=name}));
   }
   else if(type=="capture-now"&&capturing){
    string name=Str(d,"name");ValidateName(name);
    using(var stream=File.Create(Path.Combine(captures,name)))await view.CoreWebView2.CapturePreviewAsync(CoreWebView2CapturePreviewImageFormat.Png,stream);
    string metrics=await view.ExecuteScriptAsync("JSON.stringify({width:innerWidth,height:innerHeight,dpr:devicePixelRatio,preview:(()=>{const r=document.querySelector('.screen').getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}})(),bodyOverflow:document.documentElement.scrollWidth>innerWidth})");
    File.WriteAllText(Path.Combine(captures,name+".metrics.json"),metrics,Encoding.UTF8);
    view.CoreWebView2.PostWebMessageAsJson("{\"type\":\"capture-done\"}");
   }
   else if(type=="capture-end"&&capturing){view.Dock=DockStyle.Fill;ClientSize=restoreSize;Location=restoreLocation;view.ZoomFactor=restoreZoom;capturing=false;if(evidence){File.WriteAllText(Path.Combine(session,"evidence-complete.json"),"{\"completed\":true}",Encoding.UTF8);Application.Exit();}}
  }catch(Exception ex){File.WriteAllText(Path.Combine(session,"last-host-error.txt"),ex.ToString(),Encoding.UTF8);view.CoreWebView2.PostWebMessageAsJson(json.Serialize(new {type="host-error",message=ex.Message}));}
 }
 void ValidateName(string n){if(!Regex.IsMatch(n,@"^(LD|LN)_(main|easy|detail|camera|curve|color|material|export)_(light|dark)_(1920x1080|1366x768)\.png$"))throw new Exception("Invalid capture filename");}
 [STAThread]public static void Main(){Application.EnableVisualStyles();Application.SetCompatibleTextRenderingDefault(false);Application.Run(new ReferenceDemo());}
}
