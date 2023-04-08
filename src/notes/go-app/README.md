---
title: Golang 编译Win32 程序
date: 2023-04-08
timeLine: true
sidebar: false  
icon: c
category:  
    - 笔记      
tag:   
    - win32  
    - go  
    - UAC  
---    

因为工作中需要给某些`.dll` 文件设置所有者为`everyone`，需要请求`UAC` 权限，故做笔记备忘。  

## 项目初始化  
```bash  
mkdir app  
cd app  
go mod init app  
```  

## 管理资源文件  
请求`UAC` 时需要设置`app` 的资源文件属性。  
```bash  
go install github.com/akavel/rsrc     

# 编译资源文件，有些注意事项可以查找上面的仓库  
rsrc -manifest nac.manifest -o nac.syso  
go build
```  

### nac.mainfest  
```xml{6,9}
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="0.0.0.1"
    processorArchitecture="x86"
    name="app.exe"
    type="win32"
/>
<description>something about your app</description>
<trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
        <requestedPrivileges>
            <requestedExecutionLevel level="requireAdministrator" uiAccess="false"/>
        </requestedPrivileges>
    </security>
</trustInfo>
</assembly>
```  

## Go 代码   
主要是可以通过`cmd` 调用`icacls` 命令来修改`.dll` 的权限。  
```go  
userName = "everyone"
// 递归遍历文件夹
func walkDir(dir string) {
	files, err := ioutil.ReadDir(dir)
	if err != nil {
		println("目录不存在？")
		return
	}

	for _, file := range files {
		if file.IsDir() {
			walkDir(dir + "/" + file.Name())
		} else {
			absPath, err := filepath.Abs(dir + "/" + file.Name())
			if err != nil { fmt.Println(err) }

			ext := path.Ext(absPath)  // 获取文件扩展名

			if strings.ToLower(ext) == ".dll" {
                // cmd 执行`icacls` 修改文件权限
				cmd := exec.Command("icacls", absPath, "/grant", userName+":F")
				_, err := cmd.CombinedOutput()

				if err != nil {
					println("恐怕是用户名输错了")
					return
				}
				log.Println("成功修改：", absPath)
			}

		}
	}
}
```