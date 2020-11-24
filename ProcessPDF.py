


import pdfminer
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams, LTTextBox, LTFigure, LTImage
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfpage import PDFPage
import os

class PDFProcessing:
    def __init__(self, file):
        self.file = file
        
    def extract_text(self, images_folder='./'):
        with open(self.file, 'rb') as f:
            parser = PDFParser(f)
            document = PDFDocument(parser)
            rsrcmgr = PDFResourceManager()
            laparams = LAParams()
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            pages = PDFPage.get_pages(f, check_extractable=False)
    
            pdf_text = []
            for i, page in enumerate(pages):
                interpreter.process_page(page)
                layout = device.get_result()
                page_text = self.parse_layout_objs(layout, images_folder='./')    
                pdf_text.append(page_text)
            
            with open('extracted_text.txt', 'w', encoding="utf-8") as f:
                f.write('\n'.join(pdf_text))
            return '\n'.join(pdf_text)

    def update_page_text_hash(self, h, lt_obj, pct=0.2):
        x0 = lt_obj.bbox[0]
        x1 = lt_obj.bbox[2]
        key_found = False
        for k, v in h.items():
            hash_x0 = k[0]
            if x0 >= (hash_x0 * (1.0-pct)) and (hash_x0 * (1.0+pct)) >= x0:
                hash_x1 = k[1]
                if x1 >= (hash_x1 * (1.0-pct)) and (hash_x1 * (1.0+pct)) >= x1:
                    key_found = True
                    v.append(lt_obj.get_text())
                    h[k] = v
        if not key_found:
            h[(x0,x1)] = [lt_obj.get_text()]
        return h
    
    def save_image(self, lt_obj, images_folder):
        result = None
        if lt_obj.stream:
            file_stream = lt_obj.stream.get_rawdata()
            with open(f'{images_folder}_{lt_obj.name}.jpg', 'wb') as f:
                result = f.write(file_stream)
        return result

    def parse_layout_objs(self, lt_objs, images_folder, text=[]):
        text = []
        page_text = {}
        for lt_obj in lt_objs:
            if isinstance(lt_obj, LTTextBox):
                page_text = self.update_page_text_hash(page_text, lt_obj)

            if isinstance(lt_obj, LTImage):
                saved_file = self.save_image(lt_obj, images_folder)
                if saved_file:
                    text.append(f'<img src ={os.path.join(images_folder, saved_file)} />')
                else:
                    print("Error saving an image")

            if isinstance(lt_obj, LTFigure):
                print("Figure")
                text.append(self.parse_layout_objs(lt_obj, images_folder, text))

        for k, v in sorted([(key, value)  for (key, value) in page_text.items()]):
            text.append('\n'.join(v))
                
        return '\n'.join(text)

file = r'./saved_pdf/Life/ABSLI-Accidental-Death-Benefit-Rider-Plus-Policy%20Contract.pdf'
p = PDFProcessing(file) 
text = p.extract_text()
print(len(text))

