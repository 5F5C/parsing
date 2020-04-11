import shutil
from os import path
import PyPDF2
from PyPDF2.utils import PyPdfError
from PIL import Image
import pytesseract
import os
from pymongo import MongoClient

# todo Извлечь JPG из PDF и сохранить в соответствующую папку

def get_file_type(filter):
    filters = {
        '/DCTDecode': 'jpg',
        '/FlateDecode': 'png',
        '/JPXDecode': 'jp2'
    }
    try:
        return filters.get(filter)
    except KeyError as e:
        return 'bmp'

def extract_pdf_image(pdf_path):
    try:
        pdf_file = PyPDF2.PdfFileReader(open(pdf_path, 'rb'), strict=False)
    except PyPdfError as e:
        print(e)
        return None
    except FileNotFoundError as e:
        print(e)
        return None

    result = []
    for page_num in range(0, pdf_file.getNumPages()):
        page = pdf_file.getPage(page_num)
        page_obj = page['/Resources']['/XObject'].getObject()

        try:
            if page_obj['/Im0'].get('/Subtype') == '/Image':
                size = (page_obj['/Im0']['/Width'], page_obj['/Im0']['/Height'])
                data = page_obj['/Im0']._data

                mode = 'RGB' if page_obj['/Im0']['/ColorSpace'] == '/DeviceRGB' else 'P'

            result_strict = {
                'page':page_num,
                'size':size,
                'data':data,
                'mode':mode,
                'file_type': get_file_type(page_obj['/Im0']['/Filter']),
            }

            result.append(result_strict)
        except KeyError as e:
            return None
    return result

def save_pdf_image(file_name, f_path, *pdf_strict):
    file_paths = []
    for itm in pdf_strict:
        name = f'{file_name}_#_{itm["page"]}.{itm["file_type"]}'
        file_path = path.join(image_folder_path, name)

        with open(file_path, 'wb') as image:
            image.write(itm['data'])
        file_paths.append(file_path)
    return file_paths

def extract_number(file_path):
    numbers = {}
    img_obj = Image.open(file_path)
    text = pytesseract.image_to_string(img_obj, 'rus')

    pattern = 'заводской (серийный) номер'
    for idx, line in enumerate(text.split('\n')):
        if line.lower().find(pattern) + 1:
            try:
                text_en = pytesseract.image_to_string(img_obj, 'eng')
                number = text_en.split('\n')[idx].split(' ')[-1]
                numbers.update({number: file_path})
            except pytesseract.pytesseract.TesseractError as e:
                print(e)
    return numbers


if __name__ == '__main__':
    client_mn = MongoClient('mongodb://db_server:27017')
    db_mn = client_mn['pdf_parse']
    pdf_file_path = 'data_for_pdf_parse'
    image_folder_path = 'images'
    for root, dirs, files in os.walk(pdf_file_path):
        for file in files:
            pdf_file_path = os.path.join(root, file)
            a = extract_pdf_image(pdf_file_path)
            if a:
                b = save_pdf_image(file, image_folder_path, *a)
                c = [extract_number(itm) for itm in b]
                if len(c) > 0:
                    print(c)
                    db_mn['filenames_serialNumbers'].insert_many(c)
                else:
                    print(f'cant find number: {pdf_file_path}')
                    db_mn['filename_cantFindNumber'].insert_one(pdf_file_path)