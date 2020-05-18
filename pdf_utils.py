# -*- coding: utf-8 -*-
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from PyPDF2.utils import PdfReadError
from tkinter import messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import os
import traceback
from aip import AipOcr
from PIL import Image


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
        pdf_input = PdfFileReader(fp_read_file)  # 将要分割的PDF内容格式化
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
        pdfReader = PdfFileReader(open(inFile, 'rb'))
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
        pdfReader = PdfFileReader(open(file_path, 'rb'))
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

        messagebox.showinfo(message='PDF 文件加密成功\n结果保存在：{}'.format(pdf_file_out))
    except Exception:
        traceback.print_exc()


def read_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as f:
            pdf_reader = PdfFileReader(f)
            page_count = pdf_reader.getNumPages()
            content = None
            for i in range(page_count):
                page = pdf_reader.getPage(i)
                page_text = page.extractText()
                content = page_text if content is None else content + page_text
        return page_count, content
    except PdfReadError:
        messagebox.showerror(message='{}文件已加密或损坏，请重新选择。'.format(pdf_path))
