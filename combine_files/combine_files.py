# combine_files.py (Version 2.0)
import argparse
import glob
import os
import sys
import fnmatch

def combine_files(output_file, input_paths, exclude_patterns=None, use_absolute_paths=False, encoding='utf-8'):
    """
    将多个输入文件/目录中的文件合并到一个输出文件中，同时支持排除特定模式。
    Args:
        output_file (str): 合并后输出文件的路径。
        input_paths (list): 输入文件、目录或通配符模式的列表。
        exclude_patterns (list): 需要排除的文件或目录模式列表。
        use_absolute_paths (bool): 如果为True，则在标题中使用绝对路径。
        encoding (str): 读写文件时使用的编码。
    """
    if exclude_patterns is None:
        exclude_patterns = []

    # 步骤 1: 查找所有候选文件
    # 使用 set 来自动处理重复的文件路径
    candidate_files = set()
    for path in input_paths:
        # 如果路径是一个目录，则递归遍历
        if os.path.isdir(path):
            for dirpath, _, filenames in os.walk(path):
                for filename in filenames:
                    # 构建完整路径并添加到候选集合
                    full_path = os.path.join(dirpath, filename)
                    candidate_files.add(full_path)
        # 如果是文件或通配符模式，使用 glob
        else:
            # recursive=True 允许使用 '**' 通配符
            matched_files = glob.glob(path, recursive=True)
            if not matched_files:
                print(f"警告：模式 '{path}' 没有匹配到任何文件。")
            for f in matched_files:
                # glob可能返回目录，我们只关心文件
                if os.path.isfile(f):
                    candidate_files.add(f)

    # 步骤 2: 根据排除模式过滤文件
    if exclude_patterns:
        files_to_process = []
        for f in candidate_files:
            is_excluded = False
            for pattern in exclude_patterns:
                # fnmatch 用于路径与通配符模式的匹配
                if fnmatch.fnmatch(f, pattern):
                    is_excluded = True
                    break  # 一旦匹配到一个排除模式，就无需再检查
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
                    outfile.write('\n')

                header_path = os.path.abspath(filepath) if use_absolute_paths else filepath
                outfile.write(f"---\n{header_path}\n")

                try:
                    with open(filepath, 'r', encoding=encoding, errors='ignore') as infile:
                        # errors='ignore' 可以跳过无法解码的字符
                        while True:
                            chunk = infile.read(4096)
                            if not chunk:
                                break
                            outfile.write(chunk)
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
        description="一个用于合并多个文本文件并将文件名作为标题的 Python 脚本 (V2)。支持目录输入和文件排除。",
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
        nargs='*', # 接受零个或多个排除模式
        default=[],
        help='需要排除的文件或目录模式列表，支持通配符。\n'
             '例如: --exclude "**/build/*" "*.log" "*/.DS_Store"'
    )
    parser.add_argument(
        '--absolute',
        action='store_true',
        help='在文件头中使用绝对路径而不是相对路径。'
    )

    args = parser.parse_args()
    combine_files(args.output_file, args.input_paths, args.exclude, args.absolute)

if __name__ == "__main__":
    main()