# -*- coding: utf-8 -*-
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from PyPDF2.utils import PdfReadError
from tkinter import messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import os
import traceback
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal, LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO


def is_path_correct(file_path, output_dir):
    if file_path is None or output_dir == '':
        messagebox.showerror(message='请先选择正确的 PDF 文件或输出文件夹。')
        return False
    else:
        return True


def split_pdf(file_path, start_page, end_page, output_dir):
    try:
        if not is_path_correct(file_path, output_dir):
            return
        fp_read_file = open(file_path, 'rb')  # 打开要拆分的文件
        pdf_input = PdfFileReader(fp_read_file, strict=False)  # 将要分割的PDF内容格式化
        page_count = pdf_input.getNumPages()  # 获取PDF页数
        start_page = page_count if start_page == 'max' else int(start_page)
        end_page = page_count if end_page == 'max' else int(end_page)

        if start_page > end_page or start_page < 1 or end_page > page_count:
            messagebox.showerror(message='请输入正确的页码。')
            return
        start_page -= 1  # 该块处理存在问题
        pdf_output = PdfFileWriter()  # 实例一个 PDF文件编写器
        # pdf_file = "result.pdf"
        output_path = os.path.join(output_dir, 'result.pdf')

        for i in range(start_page, end_page):
            pdf_output.addPage(pdf_input.getPage(i))
        with open(output_path, 'wb') as sub_fp:
            pdf_output.write(sub_fp)

        fp_read_file.close()
        messagebox.showinfo(message='PDF 文件分割成功\n结果保存在：{}'.format(output_path))
    except FileNotFoundError:
        messagebox.showerror(message='请先选择正确的 PDF 文件。')
    except Exception:
        traceback.print_exc()


def merge_pdf(pdfs, output_dir):
    pdfFileWriter = PdfFileWriter()
    for inFile in pdfs:  # 依次循环打开要合并文件
        pdfReader = PdfFileReader(open(inFile, 'rb'), strict=False)
        numPages = pdfReader.getNumPages()
        for index in range(0, numPages):
            pageObj = pdfReader.getPage(index)
            pdfFileWriter.addPage(pageObj)
        # 最后,统一写入到输出文件中
        outFile = os.path.join(output_dir, 'merge_result.pdf')
        pdfFileWriter.write(open(outFile, 'wb'))
    messagebox.showinfo(message='PDF 文件合并成功\n结果保存在：{}'.format(outFile))


def password(file_path, output_dir, password):
    try:
        if not is_path_correct(file_path, output_dir):
            return
        pdfReader = PdfFileReader(open(file_path, 'rb'), strict=False)
        pdfWriter = PdfFileWriter()
        for pageNum in range(pdfReader.numPages):
            pdfWriter.addPage(pdfReader.getPage(pageNum))
        pdfWriter.encrypt(password)
        output_path = os.path.join(output_dir, 'encrypted.pdf')
        resultPdfFile = open(output_path, 'wb')
        pdfWriter.write(resultPdfFile)
        resultPdfFile.close()

        messagebox.showinfo(message='PDF 文件加密成功\n结果保存在：{}'.format(output_path))
    except Exception:
        traceback.print_exc()


def create_watermark(output_dir, content):
    """水印信息"""
    # 默认大小为21cm*29.7cm即A4大小
    file_name = os.path.join(output_dir, "mark.pdf")
    c = canvas.Canvas(file_name, pagesize=(30 * cm, 30 * cm))
    # 移动坐标原点(坐标系左下为(0,0))
    c.translate(10 * cm, 5 * cm)

    # 设置字体
    # c.setFont("Helvetica", 50)
    c.setFont("SimSun", 50)
    # 指定描边的颜色
    c.setStrokeColorRGB(0, 1, 0)
    # 指定填充颜色
    c.setFillColorRGB(0, 1, 0)
    # 旋转45度,坐标系被旋转
    c.rotate(30)
    # 指定填充颜色
    c.setFillColorRGB(0, 0, 0, 0.1)
    # 设置透明度,1为不透明
    # c.setFillAlpha(0.1)
    # 画几个文本,注意坐标系旋转的影响
    for i in range(5):
        for j in range(10):
            a = 10 * (i - 1)
            b = 5 * (j - 2)
            c.drawString(a * cm, b * cm, content)
            c.setFillAlpha(0.1)
    # 关闭并保存pdf文件
    c.save()
    return file_name


def pdfwater(file_path, output_dir, content):
    try:
        if not is_path_correct(file_path, output_dir):
            return
        pdf_file_mark = create_watermark(output_dir, content)
        pdf_file_out = os.path.join(output_dir, 'watermark_result.pdf')
        """把水印添加到pdf中"""
        pdf_output = PdfFileWriter()
        input_stream = open(file_path, 'rb')
        pdf_input = PdfFileReader(input_stream, strict=False)

        # 获取PDF文件的页数
        pageNum = pdf_input.getNumPages()

        # 读入水印pdf文件
        mark = open(pdf_file_mark, 'rb')
        pdf_watermark = PdfFileReader(mark, strict=False)
        # 给每一页打水印
        for i in range(pageNum):
            page = pdf_input.getPage(i)
            page.mergePage(pdf_watermark.getPage(0))
            page.compressContentStreams()  # 压缩内容
            pdf_output.addPage(page)
        result = open(pdf_file_out, 'wb')

        pdf_output.write(result)
        mark.close()
        os.remove(pdf_file_mark)
        input_stream.close()
        result.close()

        messagebox.showinfo(message='PDF 文件添加水印成功\n结果保存在：{}'.format(pdf_file_out))
    except Exception:
        traceback.print_exc()


def read_pdf(pdf_path):
    try:
        fp = open(pdf_path, 'rb')
        # 用文件对象来创建一个pdf文档分析器
        parser = PDFParser(fp)
        # 创建一个  PDF 文档
        doc = PDFDocument(parser=parser)
        # 连接分析器 与文档对象
        parser.set_document(doc)
        # 检测文档是否提供txt转换，不提供就忽略； 当然对于不提供txt转换的PDF 可以采用OCR 技术
        if not doc.is_extractable:
            messagebox.showerror(message='无法解析 PDF 文件 {}，请重新选择。'.format(pdf_path))
        # 创建PDf 资源管理器 来管理共享资源
        rsrcmgr = PDFResourceManager()
        # 创建一个PDF设备对象
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        # 处理文档对象中每一页的内容
        # doc.get_pages() 获取page列表
        # 循环遍历列表，每次处理一个page的内容
        # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等 想要获取文本就获得对象的text属性，
        page_count = 0
        content = ''
        for i, page in enumerate(PDFPage.create_pages(doc)):
            interpreter.process_page(page)
            layout = device.get_result()
            for x in layout:
                if isinstance(x, LTTextBoxHorizontal):
                    result = x.get_text()
                    content += result
                    print(result)
            page_count += 1
        # with open(pdf_path, 'rb') as f:
        #     pdf_reader = PdfFileReader(f, strict=False)
        #     page_count = pdf_reader.getNumPages()
        #     # page_count = len(pdf_reader.pages)
        #     content = None
        #     for i in range(page_count):
        #         page = pdf_reader.getPage(i)
        #         page_text = page.extractText()
        #         page_text = page_text
        #         content = page_text if content is None else content + page_text + '\n'
        return page_count, content
    except PdfReadError:
        messagebox.showerror(message='{}文件已加密或损坏，请重新选择。'.format(pdf_path))
        traceback.print_exc()
