import hashlib
import tkinter as tk
from tkinter import filedialog, ttk
import pyperclip
import threading

def calculate_md5_file(file_path, progress_callback=None):
    """计算文件的MD5值，并通过回调函数更新进度条"""
    md5 = hashlib.md5()
    try:
        file_size = 0
        with open(file_path, 'rb') as f:
            file_size = f.seek(0, 2)  # 获取文件大小
            f.seek(0, 0)  # 返回文件开头
            read_size = 0
            while True:
                data = f.read(65536)  # 每次读取64KB
                if not data:
                    break
                md5.update(data)
                read_size += len(data)
                if progress_callback:
                    progress_callback(read_size / file_size * 100)  # 更新进度条
        return md5.hexdigest()
    except FileNotFoundError:
        return "文件未找到！"
    except Exception as e:
        return f"发生错误：{e}"

def select_file():
    """选择文件并显示路径"""
    file_path = filedialog.askopenfilename()
    if file_path:
        file_path_var.set(file_path)

def calculate_md5_threaded():
    """在新线程中计算选中文件的MD5值"""
    file_path = file_path_var.get()
    if not file_path:
        result_var.set("请选择文件！")
        return

    progress_var.set(0)  # 重置进度条
    result_var.set("计算中，请稍候...")
    # 在新线程中执行计算
    threading.Thread(target=lambda: calculate_md5(file_path), daemon=True).start()

def calculate_md5(file_path):
    """计算MD5值并更新结果"""
    md5_value = calculate_md5_file(file_path, update_progress)
    root.after(0, lambda: md5_result_var.set(md5_value))
    root.after(0, lambda: result_var.set(""))

def update_progress(progress):
    """更新进度条的回调函数"""
    progress_var.set(progress)
    # 确保界面更新
    root.after(0, root.update)

def copy_md5():
    """复制MD5值到剪贴板"""
    md5_value = md5_result_var.get()
    if md5_value:
        pyperclip.copy(md5_value)
        result_var.set("MD5值已复制到剪贴板！")

def compare_two_files_threaded():
    """在新线程中对比两个文件的MD5值"""
    compare_result_var.set("对比中，请稍候...")
    # 在新线程中执行对比
    threading.Thread(target=compare_two_files, daemon=True).start()

def compare_two_files():
    """对比两个文件的MD5值"""
    file1_path = filedialog.askopenfilename(title="选择第一个文件")
    if not file1_path:
        root.after(0, lambda: compare_result_var.set("对比已取消"))
        return
    file2_path = filedialog.askopenfilename(title="选择第二个文件")
    if not file2_path:
        root.after(0, lambda: compare_result_var.set("对比已取消"))
        return

    md5_1 = calculate_md5_file(file1_path)
    md5_2 = calculate_md5_file(file2_path)

    if md5_1 == md5_2:
        result = "对比结果：一致，两个文件内容完全相同！"
    else:
        result = "对比结果：不一致，两个文件内容有差异！"
    root.after(0, lambda: compare_result_var.set(result))

def compare_file_with_input_threaded():
    """在新线程中对比文件的MD5值与输入的MD5值"""
    compare_result_var.set("对比中，请稍候...")
    # 在新线程中执行对比
    threading.Thread(target=compare_file_with_input, daemon=True).start()

def compare_file_with_input():
    """对比文件的MD5值与输入的MD5值"""
    file_path = filedialog.askopenfilename(title="选择文件")
    if not file_path:
        root.after(0, lambda: compare_result_var.set("对比已取消"))
        return
    input_md5 = compare_md5_var.get()

    if not input_md5:
        root.after(0, lambda: compare_result_var.set("请输入或粘贴要对比的MD5值！"))
        return

    if len(input_md5) != 32:
        root.after(0, lambda: compare_result_var.set("输入的MD5值格式不正确，请输入32位字符！"))
        return

    md5_file = calculate_md5_file(file_path)
    if md5_file == input_md5:
        result = "对比结果：一致，文件内容与输入的MD5值匹配！"
    else:
        result = "对比结果：不一致，文件内容与输入的MD5值不匹配！"
    root.after(0, lambda: compare_result_var.set(result))

def paste_md5():
    """从剪贴板粘贴MD5值到输入框"""
    try:
        input_md5 = pyperclip.paste()
        compare_md5_var.set(input_md5)
    except:
        compare_result_var.set("无法从剪贴板获取内容！")

# 创建主窗口
root = tk.Tk()
root.title("MD5计算器")

# 主框架
main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10)

# 计算MD5值区域
calculate_frame = tk.LabelFrame(main_frame, text="计算MD5值")
calculate_frame.pack(fill="both", expand=True, padx=5, pady=5)

tk.Label(calculate_frame, text="文件路径：").grid(row=0, column=0, padx=5, pady=5, sticky="e")
file_path_var = tk.StringVar()
tk.Entry(calculate_frame, textvariable=file_path_var, width=50).grid(row=0, column=1, padx=5, pady=5)
tk.Button(calculate_frame, text="选择文件", command=select_file).grid(row=0, column=2, padx=5, pady=5)

tk.Button(calculate_frame, text="计算MD5", command=calculate_md5_threaded).grid(row=1, column=0, columnspan=3, pady=10)

progress_var = tk.DoubleVar()
ttk.Progressbar(calculate_frame, variable=progress_var, maximum=100, length=400).grid(row=2, column=0, columnspan=3, padx=10, pady=5)

tk.Label(calculate_frame, text="文件MD5值：").grid(row=3, column=0, padx=5, pady=5, sticky="e")
md5_result_var = tk.StringVar()
tk.Entry(calculate_frame, textvariable=md5_result_var, width=50).grid(row=3, column=1, padx=5, pady=5)
tk.Button(calculate_frame, text="复制", command=copy_md5).grid(row=3, column=2, padx=5, pady=5)

result_var = tk.StringVar()
tk.Label(calculate_frame, textvariable=result_var, width=50).grid(row=4, column=0, columnspan=3, pady=10)

# 对比MD5值区域
compare_frame = tk.LabelFrame(main_frame, text="对比MD5值")
compare_frame.pack(fill="both", expand=True, padx=5, pady=5)

tk.Button(compare_frame, text="选择两个文件对比", command=compare_two_files_threaded).grid(row=0, column=0, padx=5, pady=5)
tk.Button(compare_frame, text="选择文件并与下方MD5值对比", command=compare_file_with_input_threaded).grid(row=0, column=1, padx=5, pady=5)

tk.Label(compare_frame, text="请在此处输入或粘贴要对比的MD5值：").grid(row=1, column=0, padx=5, pady=5, sticky="e")
compare_md5_var = tk.StringVar()
compare_entry = tk.Entry(compare_frame, textvariable=compare_md5_var, width=50)
compare_entry.grid(row=1, column=1, padx=5, pady=5)

# 添加一键粘贴按钮
tk.Button(compare_frame, text="一键粘贴", command=paste_md5).grid(row=2, column=1, padx=5, pady=5, sticky="w")

compare_result_var = tk.StringVar()
tk.Label(compare_frame, textvariable=compare_result_var, width=50, foreground="blue").grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()