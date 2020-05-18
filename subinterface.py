# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, messagebox


class SubInterface(object):
    def __init__(self, title):
        self.title = title
        self.root = tk.Toplevel()
        self.frm_exhibition = tk.Frame(self.root, bd=0, relief='sunken')
        self.frm_func = tk.Frame(self.root, bd=0, relief='sunken')
        self.file_path = None
        self.file_name_var = tk.Variable(self.frm_exhibition, value='文件预览')
        self.text_panel = tk.Text(self.frm_exhibition,
                                  width=35, height=20)
        self.img_panel = tk.Label(self.frm_exhibition,
                                  width=260, height=260,
                                  bd=1, relief='sunken')
        self.pdfs_panel = tk.Listbox(self.frm_exhibition,
                                     width=50, height=13)
        self.frm_output_path = tk.Frame(self.root)
        self.output_path_var = tk.Variable(self.root)

    def construct_gui(self):
        self.root.title(self.title)
        self.root.wm_attributes('-topmost', 1)
        self.set_win_size(650, 500)
        self.frm_exhibition.pack(side='left', padx=40, ipady=40)
        self.frm_func.pack(side='left', padx=40, ipady=40)
        self.frm_output_path.place(x=60, y=420)
        tk.Button(self.frm_exhibition,
                  text='选择文件',
                  command=lambda: self.select_file('input')).pack()
        tk.Label(self.frm_exhibition, textvariable=self.file_name_var, pady=10).pack()
        self.text_panel.pack()
        tk.Button(self.frm_output_path,
                  text='选择输出路径',
                  command=lambda: self.select_file('output')).pack(side='left', pady=10)
        tk.Entry(self.frm_output_path,
                 textvariable=self.output_path_var,
                 width=50).pack(side='right', padx=10)

        self.func_panel()

        self.root.mainloop()

    def set_win_size(self, wid, hei):
        # 设置窗口大小
        win_width = wid
        win_height = hei
        # 获取屏幕分辨率
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = int((screen_width - win_width) / 2)
        y = int((screen_height - win_height) / 2)
        # self.root.geometry("%sx%s+%s+%s" % (win_width, win_height, x, y))
        self.root.geometry("%sx%s" % (win_width, win_height))
        self.root.resizable(0, 0)

    def select_file(self, mode):
        if mode == 'input':
            path_ = filedialog.askopenfilenames()
            if path_ is None:
                messagebox.showinfo(message='请选择正确的文件。')
                return
            self.file_path = path_
            self.reveal_file()
        elif mode == 'output':
            path_ = filedialog.askdirectory()
            if path_ is None:
                messagebox.showinfo(message='请选择正确的文件夹。')
                return
            self.output_path_var.set(path_)

    def reveal_file(self):
        pass

    def func_panel(self):
        pass
