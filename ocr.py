# -*- coding: utf-8 -*-
from aip import AipOcr
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
from subinterface import SubInterface
import os


class OCR(SubInterface):
    def __init__(self, title):
        super(OCR, self).__init__(title)
        self.result_panel = tk.Text(self.frm_func, width=30, height=20)

    def func_panel(self):
        tk.Button(self.frm_func, text='开始识别',
                  command=self.baidu_ocr) \
            .pack()
        tk.Label(self.frm_func, text='结果输出').pack(pady=10)
        self.result_panel.pack()

    def reveal_file(self):
        if not os.path.splitext(self.file_path)[-1] in ['.png', '.jpg', '.gif', '.jpeg']:
            messagebox.showerror(message='请选择正确的图片。')
        print(self.file_path)
        img_open = Image.open(self.file_path)
        width, height = img_open.size
        if width < height:
            width = int(width / height * 260)
            height = 260
        else:
            height = int(height / width * 260)
            width = 260
        img_open = img_open.resize((width, height), Image.NEAREST)
        img = ImageTk.PhotoImage(img_open)
        self.img_panel.config(image=img)
        self.img_panel.image = img
        self.text_panel.destroy()
        self.img_panel.pack()

    def select_file(self, mode):
        path_ = filedialog.askopenfilename()
        if path_ is None:
            messagebox.showinfo(message='请选择正确的文件。')
            return
        if mode == 'input':
            self.file_path = path_
            self.reveal_file()
        elif mode == 'output':
            self.output_path_var.set(path_)

    def baidu_ocr(self):
        """
            picfile:    图片文件名
            outfile:    输出文件
            """
        picfile = self.file_path
        outfile = self.output_path_var.get()
        if picfile is None or outfile == '':
            messagebox.showerror(message='请先选择正确的图片文件或输出文件。')
            return
        filename = os.path.basename(picfile)

        APP_ID = '18873305'  # 刚才获取的 ID，下同
        API_KEY = 'Istc2YxnkUfOl2sAFCYxpcaR'
        SECRECT_KEY = '4DfXEAjpq79Gn89Yw0bCMvheGXZG6Z2F'
        client = AipOcr(APP_ID, API_KEY, SECRECT_KEY)
        # 图片切割
        img = Image.open(picfile)
        print(picfile)
        width, height = img.size
        while (width * height > 4000000):  # 该数值压缩后的图片大约 两百多k
            width = width // 2
            height = height // 2
        con_img = img.resize((width, height), Image.NEAREST)
        tmp_path = os.path.join(os.path.dirname(picfile), 'tmp.png')
        con_img.save(tmp_path)
        picfile = tmp_path
        """
        Image.NEAREST ：低质量
        Image.BILINEAR：双线性
        Image.BICUBIC ：三次样条插值
        Image.ANTIALIAS：高质量
        """
        # 二进制方式打开图片文件
        i = open(picfile, 'rb')
        # 进行图片的读取
        img = i.read()
        print("正在识别图片：\t" + filename)
        options = {}
        """ 如果有可选参数 
    
        options["detect_direction"] = "true"
        options["probability"] = "true"
        """
        # message = client.basicGeneral(img)  # 通用文字识别
        message = client.basicAccurate(img, options)  # 通用文字高精度识别
        # print("识别成功！")
        i.close()

        with open(outfile, 'a+') as fo:  # a+以附加的方式打开可读写文件，不存在则建立文件，存在则写入数据到文件尾
            fo.writelines("+" * 60 + '\n')
            fo.writelines("识别图片：\t" + filename + "\n" * 2)
            fo.writelines("文本内容：\n")
            self.result_panel.delete('1.0', 'end')
            # 输出文本内容
            for text in message.get('words_result'):
                fo.writelines(text.get('words') + '\n')
                self.result_panel.insert('end', text.get('words') + '\n')
                # print(text.get('words') )
                # fo.writelines(text.get('words') +' ' +str(text.get('probability'))+'\n')
            fo.writelines('\n' * 2)
        os.remove(tmp_path)
        messagebox.showinfo(message='OCR 内容保存成功\n保存路径：{}'.format(outfile))
        # print("文本导出成功！")
