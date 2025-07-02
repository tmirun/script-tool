#!/bin/bash

# --- 配置 ---
# 设置你的项目脚本所在的顶层源目录。
# 脚本将会递归搜索这个目录下的所有 .py 文件。
SOURCE_DIR="." # <-- 修改成你自己的真实路径

# 设置安装目标目录
TARGET_DIR="/usr/local/bin/scripts"

# 设置链接创建目录
LINK_DIR="/usr/local/bin"
# --- 配置结束 ---


# set -e: 如果任何命令失败，脚本将立即退出
set -e

echo "开始安装脚本..."
echo "搜索目录: $SOURCE_DIR"

# 检查源目录是否存在
if [ ! -d "$SOURCE_DIR" ]; then
  echo "错误: 源目录 '$SOURCE_DIR' 不存在。"
  exit 1
fi

# 使用 sudo 创建目标目录 (如果不存在)
# -p 选项可以确保在目录已存在时不报错
echo "确保目标目录 '$TARGET_DIR' 已创建..."
sudo mkdir -p "$TARGET_DIR"

# 计数器
install_count=0

# 使用 find 命令查找所有 .py 文件，并通过管道传给 while 循环逐一处理
# IFS= read -r 是安全读取每一行（即使包含空格）的标准方法
find "$SOURCE_DIR" -type f -name "*.py" | while IFS= read -r script_path; do
  
  # 提取文件名，例如 "script_tool.py"
  filename=$(basename "$script_path")
  
  # 创建命令名 (去掉 .py 后缀)，例如 "script_tool"
  command_name="${filename%.py}"

  echo "---------------------"
  echo "正在处理: $script_path"

  # 1. 拷贝文件到目标目录
  echo "  -> 拷贝到 $TARGET_DIR"
  sudo cp "$script_path" "$TARGET_DIR/$filename"

  # 2. 赋予执行权限
  echo "  -> 赋予执行权限"
  sudo chmod +x "$TARGET_DIR/$filename"

  # 3. 创建或更新符号链接 (-f 表示如果链接已存在则强制覆盖)
  echo "  -> 创建命令链接: $LINK_DIR/$command_name"
  sudo ln -sf "$TARGET_DIR/$filename" "$LINK_DIR/$command_name"

  echo "  -> 完成: 现在可以使用 '$command_name' 命令"
  
  # 计数器加一
  install_count=$((install_count + 1))
done

echo "====================="
# 由于 while 循环在子 shell 中运行，常规方法无法修改父 shell 的 install_count
# 我们通过重新计算已安装的链接来获取最终数量
final_count=$(find "$TARGET_DIR" -type f -name "*.py" | wc -l | tr -d ' ')

if [ "$final_count" -eq 0 ]; then
  echo "未找到或安装任何脚本文件。"
else
  echo "共计 $final_count 个脚本已成功安装！"
fi