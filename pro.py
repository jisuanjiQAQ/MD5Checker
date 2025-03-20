import hashlib
import tkinter as tk
from tkinter import filedialog, ttk
import pyperclip
import threading

def calculate_hash_file(file_path, algorithm, progress_callback=None):
    """计算文件的哈希值，并通过回调函数更新进度条"""
    try:
        hasher = hashlib.new(algorithm)
        file_size = 0
        with open(file_path, 'rb') as f:
            file_size = f.seek(0, 2)  # 获取文件大小
            f.seek(0, 0)  # 返回文件开头
            read_size = 0
            while True:
                data = f.read(65536)  # 每次读取64KB
                if not data:
                    break
                hasher.update(data)
                read_size += len(data)
                if progress_callback:
                    progress_callback(read_size / file_size * 100)  # 更新进度条
        return hasher.hexdigest()
    except FileNotFoundError:
        return "文件未找到！"
    except Exception as e:
        return f"发生错误：{e}"

def select_file():
    """选择文件并显示路径"""
    file_path = filedialog.askopenfilename()
    if file_path:
        file_path_var.set(file_path)

def calculate_hash_threaded():
    """在新线程中计算选中文件的哈希值"""
    file_path = file_path_var.get()
    if not file_path:
        result_var.set("请选择文件！")
        return

    selected_algorithm = algorithm_var.get()
    if not selected_algorithm:
        result_var.set("请选择哈希算法！")
        return

    progress_var.set(0)  # 重置进度条
    result_var.set("计算中，请稍候...")
    # 在新线程中执行计算
    threading.Thread(target=lambda: calculate_hash(file_path, selected_algorithm), daemon=True).start()

def calculate_hash(file_path, algorithm):
    """计算哈希值并更新结果"""
    hash_value = calculate_hash_file(file_path, algorithm, update_progress)
    root.after(0, lambda: hash_result_var.set(hash_value))
    root.after(0, lambda: result_var.set(""))

def update_progress(progress):
    """更新进度条的回调函数"""
    progress_var.set(progress)
    # 确保界面更新
    root.after(0, root.update)

def copy_hash():
    """复制哈希值到剪贴板"""
    hash_value = hash_result_var.get()
    if hash_value:
        pyperclip.copy(hash_value)
        result_var.set("哈希值已复制到剪贴板！")

def compare_two_files_threaded():
    """在新线程中对比两个文件的哈希值"""
    compare_result_var.set("对比中，请稍候...")
    # 在新线程中执行对比
    threading.Thread(target=compare_two_files, daemon=True).start()

def compare_two_files():
    """对比两个文件的哈希值"""
    file1_path = filedialog.askopenfilename(title="选择第一个文件")
    if not file1_path:
        root.after(0, lambda: compare_result_var.set("对比已取消"))
        return
    file2_path = filedialog.askopenfilename(title="选择第二个文件")
    if not file2_path:
        root.after(0, lambda: compare_result_var.set("对比已取消"))
        return

    selected_algorithm = algorithm_var.get()
    if not selected_algorithm:
        root.after(0, lambda: compare_result_var.set("请选择哈希算法！"))
        return

    hash_1 = calculate_hash_file(file1_path, selected_algorithm)
    hash_2 = calculate_hash_file(file2_path, selected_algorithm)

    if hash_1 == hash_2:
        result = "对比结果：一致，两个文件内容完全相同！"
    else:
        result = "对比结果：不一致，两个文件内容有差异！"
    root.after(0, lambda: compare_result_var.set(result))

def compare_file_with_input_threaded():
    """在新线程中对比文件的哈希值与输入的哈希值"""
    compare_result_var.set("对比中，请稍候...")
    # 在新线程中执行对比
    threading.Thread(target=compare_file_with_input, daemon=True).start()

def compare_file_with_input():
    """对比文件的哈希值与输入的哈希值"""
    file_path = filedialog.askopenfilename(title="选择文件")
    if not file_path:
        root.after(0, lambda: compare_result_var.set("对比已取消"))
        return
    input_hash = compare_hash_var.get()

    if not input_hash:
        root.after(0, lambda: compare_result_var.set("请输入或粘贴要对比的哈希值！"))
        return

    selected_algorithm = algorithm_var.get()
    if not selected_algorithm:
        root.after(0, lambda: compare_result_var.set("请选择哈希算法！"))
        return

    hash_file = calculate_hash_file(file_path, selected_algorithm)
    if hash_file == input_hash:
        result = "对比结果：一致，文件内容与输入的哈希值匹配！"
    else:
        result = "对比结果：不一致，文件内容与输入的哈希值不匹配！"
    root.after(0, lambda: compare_result_var.set(result))

def paste_hash():
    """从剪贴板粘贴哈希值到输入框"""
    try:
        input_hash = pyperclip.paste()
        compare_hash_var.set(input_hash)
    except:
        compare_result_var.set("无法从剪贴板获取内容！")

# 创建主窗口
root = tk.Tk()
root.title("哈希计算器")

# 主框架
main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10)

# 支持的哈希算法
supported_algorithms = ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512']

# 计算哈希值区域
calculate_frame = tk.LabelFrame(main_frame, text="计算哈希值")
calculate_frame.pack(fill="both", expand=True, padx=5, pady=5)

tk.Label(calculate_frame, text="文件路径：").grid(row=0, column=0, padx=5, pady=5, sticky="e")
file_path_var = tk.StringVar()
tk.Entry(calculate_frame, textvariable=file_path_var, width=50).grid(row=0, column=1, padx=5, pady=5)
tk.Button(calculate_frame, text="选择文件", command=select_file).grid(row=0, column=2, padx=5, pady=5)

tk.Label(calculate_frame, text="选择哈希算法：").grid(row=1, column=0, padx=5, pady=5, sticky="e")
algorithm_var = tk.StringVar()
algorithm_menu = tk.OptionMenu(calculate_frame, algorithm_var, *supported_algorithms)
algorithm_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")
algorithm_var.set(supported_algorithms[0])  # 默认选择MD5

tk.Button(calculate_frame, text="计算哈希", command=calculate_hash_threaded).grid(row=2, column=0, columnspan=3, pady=10)

progress_var = tk.DoubleVar()
ttk.Progressbar(calculate_frame, variable=progress_var, maximum=100, length=400).grid(row=3, column=0, columnspan=3, padx=10, pady=5)

tk.Label(calculate_frame, text="文件哈希值：").grid(row=4, column=0, padx=5, pady=5, sticky="e")
hash_result_var = tk.StringVar()
tk.Entry(calculate_frame, textvariable=hash_result_var, width=50).grid(row=4, column=1, padx=5, pady=5)
tk.Button(calculate_frame, text="复制", command=copy_hash).grid(row=4, column=2, padx=5, pady=5)

result_var = tk.StringVar()
tk.Label(calculate_frame, textvariable=result_var, width=50).grid(row=5, column=0, columnspan=3, pady=10)

# 对比哈希值区域
compare_frame = tk.LabelFrame(main_frame, text="对比哈希值")
compare_frame.pack(fill="both", expand=True, padx=5, pady=5)

tk.Button(compare_frame, text="选择两个文件对比", command=compare_two_files_threaded).grid(row=0, column=0, padx=5, pady=5)
tk.Button(compare_frame, text="选择文件并与下方哈希值对比", command=compare_file_with_input_threaded).grid(row=0, column=1, padx=5, pady=5)

tk.Label(compare_frame, text="请在此处输入或粘贴要对比的哈希值：").grid(row=1, column=0, padx=5, pady=5, sticky="e")
compare_hash_var = tk.StringVar()
compare_entry = tk.Entry(compare_frame, textvariable=compare_hash_var, width=50)
compare_entry.grid(row=1, column=1, padx=5, pady=5)

# 添加一键粘贴按钮
tk.Button(compare_frame, text="一键粘贴", command=paste_hash).grid(row=2, column=1, padx=5, pady=5, sticky="w")

compare_result_var = tk.StringVar()
tk.Label(compare_frame, textvariable=compare_result_var, width=50, foreground="blue").grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()