# 代码小片段

### 目录
| 编号 | 描述 |
| ------| ------ |
| 1 |非递归方式获取所有指定类型文件 |
| 2 |获取打包成执行文件(exe)和脚本运行文件的路径 |
| 3 |编码转换 |
***

1. 非递归方式获取所有指定类型文件
```python
def get_files(path, suffixs:tuple):
    files = []

    with os.scandir(path) as it:
        for dir_or_file in it:
            sub_dirs = [dir_or_file]
            while len(sub_dirs) > 0:
                entry = sub_dirs.pop()
                try:
                    if entry.is_symlink():
                        print('skip symlink:' + entry.path)
                        continue
                    elif entry.is_file() and entry.name.endswith(suffixs):
                        files.append(entry.path)
                    elif entry.is_dir():
                        with os.scandir(entry.path) as sub_dir_it:
                            sub_dirs[0:0] = sub_dir_it
                except Exception as e:
                    print(str(e) + entry.path)
                    continue

    return files
```

2. python中获取打包成执行文件(exe)和脚本运行文件的路径
在写python程序中，有可能需要获取当前运行脚本的路径。打包成exe的脚本和直接运行地脚本在获取路径上稍微有点不同。
```python
import os
import sys

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)
```
***

3. 编码转换
```python
def copyfile(src, dst):
    try:
        shutil.copyfile(src, dst)
    except Exception as Err:
        print('覆盖文件失败' + str(Err))

def file_codec_trans(filename_in, filename_out, encode_in = 'gb2312', encode_out = 'utf-8'):
    with codecs.open(filename=filename_in, mode='r', encoding=encode_in) as fi:
        data = fi.read()
        with open(filename_out, mode='w', encoding=encode_out) as fo:
            fo.write(data)
            fo.close()
        copyfile(filename_out, filename_in)
        print(filename_out+'->'+filename_in)
```

