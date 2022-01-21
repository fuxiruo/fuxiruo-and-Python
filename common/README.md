# 代码小片段

### 目录
| 编号 | 描述 |
| ------| ------ |
| 1 |非递归方式获取所有指定类型文件 |
| 2 |获取打包成执行文件(exe)和脚本运行文件的路径 |

***

1. 非递归方式获取所有指定类型文件
```
def get_ui_files(path):
    print(path)
    files = []

    with os.scandir(path) as it:
        for dir_or_file in it:
            sub_dirs = [dir_or_file]
            while len(sub_dirs) > 0:
                entry = sub_dirs.pop()
                try:
                    if entry.is_file()  and entry.name.endswith('.ui'):
                        print(entry.path)
                        files.append(entry.path)
                    elif entry.is_dir():
                        with os.scandir(entry.path) as sub_dir_it:
                            sub_dirs[0:0] = sub_dir_it
                except:
                    print(sys.exc_info()[1])
                    continue

    return files
```

2. python中获取打包成执行文件(exe)和脚本运行文件的路径
在写python程序中，有可能需要获取当前运行脚本的路径。打包成exe的脚本和直接运行地脚本在获取路径上稍微有点不同。
```
import os
import sys

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)
```
***

