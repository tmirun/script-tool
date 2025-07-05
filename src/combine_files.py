#!/usr/bin/env python3
"""
将多个文件合并成一个单一的文本文件。

使用方法:
    python3 combine_files.py <输出文件> <包含路径1> <包含路径2> ... [--exclude <排除模式1> <排除模式2> ...] [--include-hidden]

参数:
    output_file:         合并后内容的输出文件名。
    include_patterns:    要包含的文件或目录的路径模式。支持通配符。
    --exclude, -e:       要排除的文件或目录的路径模式。支持通配符。
    --include-hidden:    如果指定，将包含隐藏文件和文件夹 (以"."开头)。

使用例子:
    # 将 my_project/ 目录下的所有非隐藏文件合并到 project_source.txt
    python3 combine_files.py project_source.txt my_project/

    # 将 my_project/ 目录下包括隐藏文件在的所有文件合并到 project_source.txt
    python3 combine_files.py project_source.txt my_project/ --include-hidden

    # 将 my_project/src/ 目录下的所有 .py 和 .json 文件合并到 src_code.txt
    python3 combine_files.py src_code.txt "my_project/src//*.py" "my_project/src//*.json"
"""

import argparse
import glob
import os
import sys
import fnmatch


def combine_files(output_file, input_paths, exclude_patterns=None, use_absolute_paths=False, encoding='utf-8',
                  include_hidden=False):
    """
    将多个输入文件/目录中的文件合并到一个输出文件中，同时支持排除特定模式和隐藏文件。
    Args:
        output_file (str): 合并后输出文件的路径。
        input_paths (list): 输入文件、目录或通配符模式的列表。
        exclude_patterns (list): 需要排除的文件或目录模式列表。
        use_absolute_paths (bool): 如果为True，则在标题中使用绝对路径。
        encoding (str): 读写文件时使用的编码。
        include_hidden (bool): 如果为True，则包含隐藏文件和目录。
    """
    if exclude_patterns is None:
        exclude_patterns = []

    # 步骤 1: 查找所有候选文件
    candidate_files = set()
    for path in input_paths:
        # 如果路径是一个目录，则递归遍历
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path, topdown=True):
                # 默认情况下，排除隐藏文件和文件夹
                if not include_hidden:
                    # 从 dirnames 列表中移除隐藏目录，以阻止 os.walk 进入这些目录
                    dirnames[:] = [d for d in dirnames if not d.startswith('.')]
                    # 从 filenames 列表中筛选掉隐藏文件
                    filenames = [f for f in filenames if not f.startswith('.')]

                for filename in filenames:
                    full_path = os.path.join(dirpath, filename)
                    candidate_files.add(full_path)
        # 如果是文件或通配符模式，使用 glob
        else:
            matched_files = glob.glob(path, recursive=True)
            if not matched_files and '*' not in path and '?' not in path:
                print(f"警告：路径 '{path}' 没有匹配到任何文件或目录。")

            for f_path in matched_files:
                if os.path.isfile(f_path):
                    # 如果不包含隐藏文件，检查路径的任何部分是否是隐藏的
                    if not include_hidden:
                        # 如果路径的任何部分以 '.' 开头，则跳过
                        if any(p.startswith('.') and p not in ('.', '..') for p in f_path.split(os.path.sep)):
                            continue
                    candidate_files.add(f_path)

    # 步骤 2: 根据排除模式过滤文件
    if exclude_patterns:
        files_to_process = []
        for f in candidate_files:
            is_excluded = False
            normalized_f = os.path.normpath(f)
            for pattern in exclude_patterns:
                normalized_pattern = os.path.normpath(pattern)
                # fnmatch 用于路径与通配符模式的匹配
                if fnmatch.fnmatch(os.path.basename(f), pattern) or fnmatch.fnmatch(f, pattern):
                    is_excluded = True
                    break  # 一旦匹配到一个排除模式，就无需再检查
                # 检查是否是目录排除
                if (pattern.endswith(os.path.sep) or pattern.endswith('/')) and \
                   normalized_f.startswith(normalized_pattern + os.path.sep):
                    is_excluded = True
                    break
            if not is_excluded:
                files_to_process.append(f)
    else:
        files_to_process = list(candidate_files)

    # 如果过滤后没有文件，则退出
    if not files_to_process:
        print("错误：经过滤后，没有找到任何要合并的文件。脚本已退出。")
        sys.exit(1)

    # 步骤 3: 排序并合并
    files_to_process.sort()

    print(f"找到 {len(candidate_files)} 个文件，排除 {len(candidate_files) - len(files_to_process)} 个后，")
    print(f"准备合并以下 {len(files_to_process)} 个文件到 '{output_file}':")
    for f in files_to_process:
        print(f"  - {f}")
    print("-" * 20)

    try:
        with open(output_file, 'w', encoding=encoding) as outfile:
            for index, filepath in enumerate(files_to_process):
                if index > 0:
                    outfile.write('\n\n')

                header_path = os.path.abspath(filepath) if use_absolute_paths else filepath
                outfile.write(f"--- {header_path} ---\n")

                try:
                    with open(filepath, 'r', encoding=encoding, errors='ignore') as infile:
                        # errors='ignore' 可以跳过无法解码的字符
                        content = infile.read()
                        outfile.write(content)
                except Exception as e:
                    error_message = f"\n错误：读取文件 '{filepath}' 时发生错误: {e}\n"
                    print(error_message)
                    outfile.write(error_message)

        print(f"\n✅ 成功！所有文件已合并到 '{output_file}'。")

    except IOError as e:
        print(f"错误：无法写入到输出文件 '{output_file}': {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="一个用于合并多个文本文件并将文件名作为标题的 Python 脚本。默认排除隐藏文件。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'output_file',
        help='合并后的输出文件名。'
    )
    parser.add_argument(
        'input_paths',
        nargs='+',
        help='一个或多个输入路径。可以是文件、目录或支持通配符的模式 (如 "src/**/*.py")。'
    )
    parser.add_argument(
        '--exclude',
        nargs='*',
        default=[],
        help='需要排除的文件或目录模式列表，支持通配符。\n'
             '例如: --exclude "**/build/*" "*.log" ".DS_Store"'
    )
    parser.add_argument(
        '--absolute',
        action='store_true',
        help='在文件头中使用绝对路径而不是相对路径。'
    )
    parser.add_argument(
        '--include-hidden',
        action='store_true',
        help='包含隐藏文件和文件夹 (即以 "." 开头的文件和文件夹)。'
    )

    args = parser.parse_args()
    combine_files(
        args.output_file,
        args.input_paths,
        args.exclude,
        args.absolute,
        include_hidden=args.include_hidden
    )


if __name__ == "__main__":
    main()