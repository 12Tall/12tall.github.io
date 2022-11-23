---
title: Win32 SDK编程
date: 2022-08-03
timeLine: true
sidebar: false  
icon: c
category:  
    - 笔记      
tag:   
    - win32  
    - c/cpp  
    - 消息  
    - 窗口   
---  

## 窗口与消息机制   
首先以[鱼C论坛](https://fishc.com.cn/thread-47361-1-1.html)的模板代码为例，展示一下标准的Win32 程序的基本结构。  

### 创建Win32 窗口
```c++
#include<windows.h>
#include<string>

LRESULT CALLBACK WndProc(HWND, UINT, WPARAM, LPARAM);  // 声明函数  

// [API档案] WinMain https://fishc.com.cn/thread-73544-1-1.html
int WINAPI WinMain(
	HINSTANCE hInstance,      // 指定应用程序当前实例的句柄
							  // 因为PE 文件在内存中的首地址
	                          // 所以，同一个PE 文件，在内存中的句柄是相同的
	HINSTANCE hPrevInstance,  // 此应用程序前一个实例句柄，总是为NULL
							  // 检测另一个实例是否已经存在：采用CreateMutex 函数
	PSTR szCmdLine,           // 该应用程序的命令行参数
	int iCmdShow              // 控制窗口显示方式
) {
	static TCHAR szAppName[] = TEXT("MyWIndows");  // 定义类名  
	HWND hwnd;  // 窗口句柄  
	MSG msg;    // Windows 消息结构  
	WNDCLASS wndClass;  // 窗口类结构，用于向系统注册窗口类  

#pragma region 在窗口类结构中定义窗口基本属性
	wndClass.style = CS_HREDRAW | CS_VREDRAW;  // 窗口横向、纵向变化重绘
	wndClass.lpfnWndProc = WndProc;  // 窗口消息过程函数，也是回调函数
	wndClass.cbClsExtra = 0;
	wndClass.cbWndExtra = 0;
	wndClass.hInstance = hInstance;  // 窗口所属实例
	wndClass.hIcon = LoadIcon(NULL, IDI_APPLICATION);
	wndClass.hCursor = LoadCursor(NULL, IDC_ARROW);
	wndClass.hbrBackground = (HBRUSH)GetStockObject(WHITE_BRUSH);
	wndClass.lpszMenuName = NULL;
	wndClass.lpszClassName = szAppName;  // 窗口类类名
#pragma endregion

#pragma region 向系统注册窗口类  
	// RegisterClass https://fishc.com.cn/thread-70667-1-1.html
	// 如果需要设置窗口类的小图标，则需要使用RegisterClassEx
	// exe 注册的类在程序终止后会被注销；而dll 注册的则需要手动注销
    // UnregisterClass https://fishc.com.cn/thread-70759-1-1.html
	if (!RegisterClass(&wndClass)) {
		MessageBox(NULL,
			TEXT("注册窗口类失败，这个程序需要在Windows NT 下运行！"),
			szAppName,
			MB_ICONERROR);
		return 0;
	}
#pragma endregion	

#pragma region 利用已经注册的窗体类创建窗体  
	hwnd = CreateWindow(szAppName,  // 窗体类名
		std::to_wstring((DWORD)hInstance).c_str(),           // 窗口标题
		WS_OVERLAPPEDWINDOW,        // 窗口风格
		CW_USEDEFAULT,              // x
		CW_USEDEFAULT,              // y
		CW_USEDEFAULT,              // width
		CW_USEDEFAULT,              // height
		NULL,                       // 父窗口句柄
		NULL,                       // 窗口菜单句柄
		hInstance,                  // 程序实例句柄
		NULL);                      // 创建参数
#pragma endregion

	ShowWindow(hwnd, iCmdShow);     // 显示窗口  
	UpdateWindow(hwnd);             // 更新窗口

#pragma region 消息处理  
	while (GetMessage(&msg, NULL, 0, 0))
	{
		TranslateMessage(&msg);
		DispatchMessage(&msg);
	}
#pragma endregion

	return msg.wParam;  // 程序终止
}
LRESULT CALLBACK WndProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
	HDC hdc;
	PAINTSTRUCT ps;
	RECT rect;

	switch (uMsg){
	case WM_PAINT:
		hdc = BeginPaint(hwnd, &ps);
		GetClientRect(hwnd, &rect);
		DrawText(hdc, TEXT("大家好，这是我的第一个窗口程序！"), -1, &rect,
			DT_SINGLELINE | DT_CENTER | DT_VCENTER);
		EndPaint(hwnd, &ps);
		return 0;

	case WM_DESTROY:
		PostQuitMessage(0);
		return 0;
	}

	// call default window process
	return DefWindowProc(hwnd, uMsg, wParam, lParam);
}
```

### 窗口的生命周期  

![生命周期](./img/win32/window-lifcycle.svg)
### Windows 消息机制  

## Windows 中的安全机制  
在MinGW-GCC 中使用`OpenProcess` 函数不会报错，但是在Visual Studio 中却总也获取不到进程的句柄。搞了半天原来是Windows 安全机制的问题，这里简单做下笔记。  

### UAC
UAC(User Account Control, 用户账号控制)，是从Windows Vista以来引入的新技术。目的就是严格控制进程所获得的权限。  
- WinXP 时代：
  1. 标准用户具有AccessToken，只能访问和修改有限的资源；  
  2. 管理员组的用户具有FullAccessToken，可以获取任意资源的访问权限  
- Vista 以后：即便是管理员，也尽量只以标准用户的权限启动进程  
  1. 标准用户具有AccessToken 同XP；
  2. 以管理员登录，则会分配两个AccessToken：Standard和FullAccess。而默认情况下则以标准用户的权限创建进程。
并且需要注意的是，一个进程创建的子进程的权限一般不会更高。详情见阅：[《UAC 的前世今生》](https://xiangwangfeng.com/2010/10/20/UAC%E7%9A%84%E5%89%8D%E4%B8%96%E4%BB%8A%E7%94%9F/)

### UIPI  
UIPI(User Interface Privilege Isolation, 用户界面特权隔离)。用于在程序中过滤比自己MIC(Mandatory Integrity Control, 强制完整性控制) 等级低的进程发来的消息。  

MIC等级|说明    
---|---  
SECURITY_MANDATORY_UNTRUSTED_RID|不信任的MIC等级  
SECURITY_MANDATORY_LOW_RID|	低MIC等级，如IE  
SECURITY_MANDATORY_MEDIUM_RID|中MIC等级，默认为这个等级，如Explorer  
SECURITY_MANDATORY_HIGH_RID|高MIC等级，以管理员身份运行的程序  
SECURITY_MANDATORY_SYSTEM_RID|系统MIC等级，一般是服务应用程序  
SECURITY_MANDATORY_PROTECTED_PROCESS_RID|被保护进程的MIC等级  

详见[解决Win7系统下以管理员身份运行的程序接收不到拖放文件消息[WM_DROPFILES]问题的方法](https://blog.csdn.net/learner198461/article/details/42223835)  

### 进程权限提升  
要实现进程的权限提升，前提条件是此进程的权限仍然有可提升的空间，即不能以标准用户运行。而权限提升的过程主要与三个Windows 系统API 相关。  

以下代码引用自[进程提升权限](https://www.huaweicloud.com/articles/13251202.html)，这里仅重新排版。  
```c++
BOOL EnablePrivilege(LPCTSTR lpszPrivilegeName,BOOL bEnable){ 
	HANDLE hToken; 
	TOKEN_PRIVILEGES tp; 
	LUID luid; 
	
	if(!OpenProcessToken(GetCurrentProcess(),
	    TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY | TOKEN_READ,&hToken)) 
	  return FALSE; 

	if(!LookupPrivilegeValue(NULL, lpszPrivilegeName, &luid)) 
	  return TRUE;  // 这里应该return FALSE 吧

	tp.PrivilegeCount = 1; 
	tp.Privileges[0].Luid = luid; 
	tp.Privileges[0].Attributes = (bEnable) ? SE_PRIVILEGE_ENABLED : 0; 
	
	AdjustTokenPrivileges(hToken,FALSE,&tp,NULL,NULL,NULL);
	
	CloseHandle(hToken); 
	return (GetLastError() == ERROR_SUCCESS);
}
```

下图是具体的调用流程：  
![权限提升过程](./img/win32/enable-privilege.svg)

## 参考  
1. [WIN32-SDK-API 档案](https://fishc.com.cn/forum.php?mod=forumdisplay&fid=255&filter=typeid&typeid=420)