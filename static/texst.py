import os

# 定义目录和文件命名规则
directory = 'Icon'  # 替换为你的图片目录
base_name = 'icons8-report-'
extension = '.png'  # 替换为你的图片格式，如 .jpg, .jpeg 等

# 获取当前目录下所有文件
files = os.listdir(directory)

# 过滤出符合命名规则的文件
filtered_files = [f for f in files if f.endswith(extension)]

# 按字母顺序排序文件，以确保按顺序重命名
filtered_files.sort()

# 对每个文件进行重命名
for index, old_name in enumerate(filtered_files, start=1):
    new_name = f"{base_name}{index}{extension}"  # 构建新名称

    # 构建完整路径
    old_path = os.path.join(directory, old_name)
    new_path = os.path.join(directory, new_name)

    # 重命名文件（允许覆盖）
    try:
        os.rename(old_path, new_path)
        print(f"Renamed: {old_name} to {new_name}")
    except Exception as e:
        print(f"Error renaming {old_name} to {new_name}: {e}")
