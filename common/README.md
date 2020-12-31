# 代码小片段

### 目录
| 编号 | 描述 |
| ------| ------ |
| 1 |非递归方式获取所有指定类型文件 |

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

***

