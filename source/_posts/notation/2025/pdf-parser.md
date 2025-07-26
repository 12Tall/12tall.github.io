---
title: PDF 解析
date: 2025-07-25 15:48:00
tags:
    - pdf  
    - python  
    - ocr
    - table
---

这是一篇阅读笔记。从PDF 中提取数据（包含格式信息）可以用在很多很多地方，比如文档总结、翻译等。本文的整体思路结构比较清晰，可以在今后的代码中重点参考下。  
<!-- more -->  

## 代码流程图  

{% mermaid flowchart TD %}
 A[PDF 文件] --> |PDFMiner| B(提取页面（数组）)
 B --> |PDFMiner| C[[页面布局]]
 C --> D([LTTextContainer 文本容器]) --> |通过pdfminer 提取文本| G([通过LTTextLine/LTChar 逐行/逐字符分析样式]) 
 C --> E([LTFigure 图片]) --> |通过pdf2image 提取图片|H([通过pytesseract OCR 识别文本])
 C --> F([LTRect 二维矩形，一般为图形或图表]) --> |通过pdfplumber 提取表格❌|I([将表格内容转化为字符串])
 G --> J[[将解析后的内容形成字典对象]]
 H --> J
 I --> J
 J --> |整合数据| K[输出页面文本]
{% endmermaid %}  

需要的工具包：  
```bash
pip install PyPDF2  # 从路径读取PDF 文件  
pip install pdfmner.six  # 提取文本和格式，支持Python 3  
pip install pdfplumber  # 识别table 并提取信息（似乎有些表格无法识别）  
pip install pdf2image  # 裁剪pdf 并转化为PNG 图像   
pip install Pillow  # 图像处理     
pip install tesseract  # OCR 工具，但是需要提前安装二进制文件     
```

## 代码解析  

```python  
import pdfplumber
import pytesseract
from PIL import Image
from PyPDF2 import PdfReader,PageObject,PdfWriter
from pdf2image import convert_from_path
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
poppler_path=r'D:\utils\poppler-24.08.0\Library\bin'

pdf_file_path = 'DeepSeek_R1.pdf'

pdfFileObj = open(pdf_file_path, 'rb')
pdfReaded = PdfReader(pdfFileObj)


pdf_pages = extract_pages(pdf_file_path) # 读取文件
for page_num, page in enumerate(pdf_pages):  
    # 逐页处理  
    print(f"正在处理第{page_num+1} 页内容")

    pageObj = pdfReaded.pages[page_num]

    for element in page: 
        print(f"  处理元素<{type(element).__name__}>")  # 这里的element 不仅带有文本，还带有位置信息
        if isinstance(element, LTTextContainer):  # 处理文本内容
            print(f"    文本域<LTTextContainer>：BBox{element.bbox}")
            extract_text(element) 
        elif isinstance(element, LTFigure):  # OCR 识别图片
            print(f"    图片<LTFigure>：BBox{element.bbox}")
            crop_image(element, pageObj)
            convert_pdf_to_image()
            text = image_to_text()
            print("OCR 结果:::", text)
        elif isinstance(element, LTRect):
            print(f"    图形图表<LTRect>：BBox{element.bbox}")
            # 处理表格，但是验证代码似乎并不完善
        else:
            print(f"    其他元素类型：BBox{element.bbox}")
    if page_num >= 0:
        break # 只处理第一页用作演示
```

### 提取文本  
提取LTTextContainer 中的内容是，并不会查找表格中的文本内容，所以不用担心混乱出错：
```python
def extract_text(element: LTTextContainer):
    text = element.get_text()  # 所有文本

    # # 逐字处理文本，计算量大，视情况可以忽略格式信息
    # content = []
    # for line in element:
    #     line_content = []
    #     for charactor in line:
    #         if isinstance(charactor, LTChar):
    #             line_content.append({
    #                 "v":charactor.get_text(), # 值
    #                 "f":charactor.fontname,   # 字体
    #                 "s":charactor.size        # 大小
    #             })
    #     content.append(line_content)

    print("》》》")
    print(text)
    print("《《《\n\n")
```

### 识别图片  
```python
temp_file_name = "temp"  # 假定文件名，其实这里可以生成唯一文件名的

def crop_image(element:LTFigure, pageObj:PageObject):
    # 图片的边界信息，裁剪
    [l,t,r,b] = [element.x0, element.y0, element.x1, element.y1]
    pageObj.mediabox.lower_left = (l, b)
    pageObj.mediabox.upper_right = (r, t)
    # 保存裁剪后的图片
    cropped_pdf_writer = PdfWriter()
    cropped_pdf_writer.add_page(pageObj)
    # 保存到临时文件
    with open(f'{temp_file_name}.pdf', 'wb') as f:
        cropped_pdf_writer.write(f)

def convert_pdf_to_image(input_file=f'{temp_file_name}.pdf'):
    # pdf 转图片  
    images = convert_from_path(input_file,poppler_path=poppler_path)
    image = images[0]
    image.save(f"{temp_file_name}.png", "PNG")

def image_to_text(image_file = f"{temp_file_name}.png"):
    # OCR 识别文本
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)
    return text
```

### 提取表格  
提取表格的代码实际工作起来有些问题，最好还是通过其他工具来识别吧。或者干脆跳过图片和表格的处理：
```python
def extract_table( page_num, table_num):
    pdf = pdfplumber.open(pdf_file_path)
    table_page = pdf.pages[page_num]
    print(table_page)
    table = table_page.extract_tables()[page_num]

def table_converter(table):
    table_str = ""
    for row_num in range(len(table.extract())):  # 这里原先的方法已经不适用了
        row = table[row_num]
        clean_row = [item.replace('\n', '') if item is not None and '\n' in item else 'None' if item is None else item for item in row]
        table_str += f"|{'|'.join(clean_row)}|"+"\n"
        print(row)
    return table_str[:-1]
```

相比之下，通过[python-docx](https://github.com/python-openxml/python-docx)/[openpyxl](https://openpyxl.readthedocs.io/en/stable/)/[python-pptx](https://python-pptx.readthedocs.io/) 处理office 更简单一些。

## 原文  
1. [全面指南———用python提取PDF中各类文本内容的方法](https://www.luxiangdong.com/2023/10/05/extract/)