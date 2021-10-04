; �ű��� Inno Setup �ű��� ���ɡ�
; �����ĵ���ȡ���� INNO SETUP �ű��ļ�����ϸ���ϣ�


;note:���˽ű�����Ҫ������ļ�����ͬһ��Ŀ¼��

;"AAA_BBB"ȥ��"_BBB"��ƴ��PRODUCT_NAME
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
  
;"AAA_BBB"ȥ��"AAA_"
#define GetCustomer(str fileName) \
  Local[0] = GetFileDescription(fileName) , \
  Local[1] = "_",   \
  Local[2] = RPos(Local[1], Local[0]), \
  Delete(Local[0], 0, Local[2]+1)

;"AJPS2019018,AJPS2019019",���IDʱ��,�滻Ϊ_
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
; ע��: AppId ��ֵ��Ψһʶ���������ı�־��
; ��Ҫ������������ʹ����ͬ�� AppId ֵ��
; (�ڱ������е���˵������� -> ���� GUID�����Բ���һ���µ� GUID)
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
; ע��: ��Ҫ���κι����ϵͳ�ļ�ʹ�� "Flags: ignoreversion"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

