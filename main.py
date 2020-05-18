# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, messagebox
from pdf import Pdf
from ocr import OCR
from doc_kw import DocKw
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class Root(object):
    def __init__(self):
        self.root = tk.Tk()
        self.menubar = tk.Menu(self.root, tearoff=0)
        self.pdf_edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.ocr_menu = tk.Menu(self.menubar, tearoff=0)
        self.sim_menu = tk.Menu(self.menubar, tearoff=0)
        self.about_menu = tk.Menu(self.menubar, tearoff=0)

    def construct_gui(self):
        self.root.title('Program')
        self.set_win_size(770, 280)
        self.set_menu()
        self.set_func_matrix()
        self.root['menu'] = self.menubar

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
        self.root.geometry("%sx%s+%s+%s" % (win_width, win_height, x, y))
        self.root.resizable(0, 0)

    def set_menu(self):
        self.menubar.add_cascade(label='OCR', menu=self.ocr_menu)
        self.menubar.add_cascade(label='文档编辑', menu=self.pdf_edit_menu)
        self.menubar.add_cascade(label='文档相似度', menu=self.sim_menu)
        # self.menubar.add_cascade(label='关于', menu=self.about_menu)

        self.ocr_menu.add_command(label='图片文本识别', command=img_ocr)
        self.ocr_menu.add_separator()
        self.ocr_menu.add_command(label='Exit', command=self.root.destroy)

        self.pdf_edit_menu.add_command(label='PDF 文档拆分', command=pdf_split)
        self.pdf_edit_menu.add_command(label='PDF 文档合并', command=pdf_merge)
        self.pdf_edit_menu.add_command(label='PDF 文档加密', command=pdf_encrypt)
        self.pdf_edit_menu.add_command(label='PDF 文档加水印', command=pdf_watermark)
        self.pdf_edit_menu.add_separator()
        self.pdf_edit_menu.add_command(label='Exit', command=self.root.destroy)

        self.sim_menu.add_command(label='关键词提取', command=extract_kw)
        self.sim_menu.add_command(label='相似度提取', command=show_sim)
        self.sim_menu.add_separator()
        self.sim_menu.add_command(label='Exit', command=self.root.destroy)

        # self.about_menu.add_command(label='About me', command=lambda: self.root.destroy())

    def set_func_matrix(self):
        tk.Button(self.root, text='图片文字识别',
                  width=12, height=5, bg='red',
                  command=img_ocr).grid(row=0, column=0,
                                        padx=15, pady=15)
        tk.Button(self.root, text='PDF 文档拆分',
                  width=12, height=5, bg='orange',
                  command=pdf_split).grid(row=0, column=2,
                                          padx=5, pady=15)
        tk.Button(self.root, text='PDF 文档合并',
                  width=12, height=5, bg='yellow',
                  command=pdf_merge).grid(row=0, column=4,
                                          padx=5, pady=15)
        tk.Button(self.root, text='PDF 文档加密',
                  width=12, height=5, bg='green',
                  command=pdf_encrypt).grid(row=0, column=6,
                                            padx=5, pady=15)
        tk.Button(self.root, text='PDF 文档加水印',
                  width=12, height=5, bg='#00FFFF',
                  command=pdf_watermark).grid(row=1, column=1,
                                              padx=5, pady=15)
        tk.Button(self.root, text='关键词提取',
                  width=12, height=5, bg='#4C8AFA',
                  command=extract_kw).grid(row=1, column=3, padx=5,
                                           pady=15)
        tk.Button(self.root, text='相似度提取',
                  width=12, height=5, bg='#E3BAFA',
                  command=show_sim).grid(row=1, column=5, padx=5,
                                         pady=15)


def pdf_split():
    pdf = Pdf(title='PDF 文档分割', mode='split')
    pdf.construct_gui()


def pdf_merge():
    pdf = Pdf(title='PDF 文档合并', mode='merge')
    pdf.construct_gui()


def pdf_encrypt():
    pdf = Pdf(title='PDF 文档加密', mode='encrypt')
    pdf.construct_gui()


def pdf_watermark():
    pdf = Pdf(title='PDF 文档加水印', mode='watermark')
    pdf.construct_gui()


def img_ocr():
    ocr = OCR(title='图片文本识别')
    ocr.construct_gui()


def extract_kw():
    doc_kw = DocKw()
    doc_kw.construct_gui()


def show_sim():
    doc_kw = DocKw()
    doc_kw.construct_sim_gui()


def main():
    pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))  # 注册字体
    root = Root()
    root.construct_gui()


if __name__ == '__main__':
    main()
