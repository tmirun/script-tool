# script-tool

## 简介

本项目包含一个自动化脚本安装工具，可将 `src` 目录下的所有 Python 脚本批量安装到系统可执行路径，方便全局调用。

## `install_scripts_to_bin.sh` 脚本安装工具使用方法

该工具会自动将 `src` 目录下的所有 `.py` 脚本复制到 `/usr/local/bin/scripts`，并在 `/usr/local/bin` 下创建同名命令链接（去除 `.py` 后缀），从而可以直接在终端使用这些脚本。

### 安装所有脚本到全局命令

```bash
bash install_scripts_to_bin.sh
```

> 需要 sudo 权限，执行过程中会自动处理权限和目录。

#### 示例

假设 `src` 目录下有 `hello.py`，安装后可直接在终端运行：

```bash
hello
```

---

## 环境管理

本项目推荐使用 Python 的 venv 虚拟环境进行依赖管理和开发。

### 创建虚拟环境

```bash
python3 -m venv venv
```

### 激活虚拟环境

- macOS/Linux:
  ```bash
  source venv/bin/activate
  ```
- Windows:
  ```bash
  venv\Scripts\activate
  ```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 冻结依赖

开发过程中如有新增依赖，请使用以下命令更新 `requirements.txt`：

```bash
pip freeze > requirements.txt
```

