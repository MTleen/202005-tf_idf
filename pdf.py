# -*- coding: utf-8 -*-
from subinterface import SubInterface
import tkinter as tk
from tkinter import filedialog, messagebox
from pdf_utils import *
import os


class Pdf(SubInterface):
    def __init__(self, title, mode):
        super(Pdf, self).__init__(title)
        self.mode = mode
        self.page_count = 0
        self.page_count_var = tk.Variable(self.frm_func,
                                          value='确定拆分范围（1-x）')
        self.page_from_var = tk.Variable(self.frm_func, value=1)
        self.page_to_var = tk.Variable(self.frm_func, value='max')
        self.password_var = tk.Variable(self.frm_func)
        self.watermark_var = tk.Variable(self.frm_func)

    def func_panel(self):
        modes = {
            'split': self.split_panel,
            'merge': self.merge_panel,
            'encrypt': self.encrypt_panel,
            'watermark': self.watermark_panel
        }
        modes[self.mode]()

    def split_panel(self):
        tk.Label(self.frm_func, textvariable=self.page_count_var) \
            .grid(row=0, column=2, columnspan=3, pady=10)
        tk.Entry(self.frm_func, textvariable=self.page_from_var, width=5) \
            .grid(row=1, column=2)
        tk.Label(self.frm_func, text='--').grid(row=1, column=3)
        tk.Entry(self.frm_func, textvariable=self.page_to_var, width=5) \
            .grid(row=1, column=4)

        tk.Button(self.frm_func,
                  text='开始拆分',
                  command=lambda: split_pdf(self.file_path,
                                            self.page_from_var.get(),
                                            self.page_to_var.get(),
                                            self.output_path_var.get())) \
            .grid(row=2, column=2, columnspan=3, pady=20)

    def merge_panel(self):
        self.text_panel.destroy()
        self.pdfs_panel.pack(padx=100)
        tk.Button(self.frm_exhibition, text='开始合并',
                  command=lambda: merge_pdf(self.file_path)).pack(pady=20)

    def encrypt_panel(self):
        tk.Label(self.frm_func, text='输入加密密码：').grid(row=0, column=0)
        tk.Entry(self.frm_func, textvariable=self.password_var,
                 show='*', width=15) \
            .grid(row=0, column=1)
        tk.Button(self.frm_func, text='开始加密',
                  command=lambda: password(self.file_path,
                                           self.output_path_var.get(),
                                           self.password_var.get())) \
            .grid(row=1, column=0, columnspan=2, pady=30)

    def watermark_panel(self):
        tk.Label(self.frm_func, text='输入水印：').grid(row=0, column=0)
        tk.Entry(self.frm_func, textvariable=self.password_var,
                 width=15) \
            .grid(row=0, column=1)
        tk.Button(self.frm_func, text='添加水印',
                  command=lambda: pdfwater(self.file_path,
                                           self.output_path_var.get(),
                                           self.watermark_var.get())) \
            .grid(row=1, column=0, columnspan=2, pady=30)

    def reveal_file(self):
        if self.mode != 'merge':
            self.file_path = self.file_path[0]
            if os.path.splitext(self.file_path)[-1] != '.pdf' or not os.path.exists(self.file_path):
                messagebox.showwarning(message='请选择正确的 pdf 文件。')
                return
            self.text_panel.delete('1.0', 'end')
            self.file_name_var.set(os.path.basename(self.file_path))
            self.page_count, pdf_content = read_pdf(self.file_path)
            self.page_count_var.set('确定拆分范围（1-{}）'.format(self.page_count))
            self.text_panel.insert('end', pdf_content)
        else:
            for p in self.file_path:
                self.pdfs_panel.insert(0, p)
