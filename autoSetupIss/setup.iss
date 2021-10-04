; 脚本用 Inno Setup 脚本向导 生成。
; 查阅文档获取创建 INNO SETUP 脚本文件的详细资料！


;note:将此脚本跟需要打包的文件放在同一级目录下

;"AAA_BBB"去掉"_BBB"在拼接PRODUCT_NAME
#define GetAppName(str fileName)   \
  Local[0] = GetFileDescription(fileName) , \
  Local[1] = "_",   \
  Local[2] = RPos(Local[1], Local[0]), \
  Local[3] = Delete(Local[0], Local[2], len(Local[0])), \
  Local[3] = Local[3] + GetStringFileInfo(fileName, PRODUCT_NAME),  \
  Local[3]
  
#define GetDirName(str fileName)   \
  Local[0] =  "C:\QuickHandler_"  + GetStringFileInfo(fileName, PRODUCT_NAME),  \
  Local[0]
  
;"AAA_BBB"去掉"AAA_"
#define GetCustomer(str fileName) \
  Local[0] = GetFileDescription(fileName) , \
  Local[1] = "_",   \
  Local[2] = RPos(Local[1], Local[0]), \
  Delete(Local[0], 0, Local[2]+1)

;"AJPS2019018,AJPS2019019",多个ID时将,替换为_
#define GetCustomerID(str fileName)  \
  Local[0] = GetFileProductVersion(AddBackslash(SourcePath) + "sscom.exe"), \
  StringChange(Local[0], ",", "_")
  
#define MyAppName "sscom.exe"
#define MyDirName GetDirName(AddBackslash(SourcePath) + "sscom.exe")
#define MyCustomer  GetCustomer(AddBackslash(SourcePath) + "sscom.exe")
#define MyCustomerID GetCustomerID(AddBackslash(SourcePath) + "sscom.exe")
#define MyAppVersion GetFileVersion(AddBackslash(SourcePath) + "sscom.exe")
#define MyAppPublisher "KO"
#define MyAppExeName "sscom.exe"

[Setup]
; 注意: AppId 的值是唯一识别这个程序的标志。
; 不要在其他程序中使用相同的 AppId 值。
; (在编译器中点击菜单“工具 -> 产生 GUID”可以产生一个新的 GUID)
AppId={#MyAppName}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
VersionInfoVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={#MyDirName}
DisableDirPage=yes
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=R:/
OutputBaseFilename={#MyAppName}_{#MyCustomer}_{#MyCustomerID}_setup_ver_{#MyAppVersion}
Compression=lzma
SolidCompression=yes

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimp.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: ".\testDir\*"; DestDir: "{app}\testDir\"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: ".\*.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\test"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\*.txt"; DestDir: "{app}"; Flags: ignoreversion
; 注意: 不要在任何共享的系统文件使用 "Flags: ignoreversion"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

