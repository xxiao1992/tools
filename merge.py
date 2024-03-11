from PyPDF2 import PdfReader, PdfWriter
import os


filenames = [x for x in os.listdir() if 'pdf' in x.lower() and 'To_print' not in x]
filenames = list(sorted(filenames))

files = []
outPdf = PdfWriter()
for filename in filenames:
    f = open(filename, 'rb')
    files.append(f)
    file = PdfReader(f, strict=False)
    outPdf.append_pages_from_reader(file)
    n_page = len(file.pages)
    if n_page % 2 == 1:
        outPdf.add_blank_page()

with open('To_print.pdf', 'wb') as outStream:
    outPdf.write(outStream)

for x in files:
    x.close()
