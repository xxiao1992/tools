from PyPDF2 import PdfFileReader, PdfFileWriter
import os


filenames = [x for x in os.listdir() if 'pdf' in x.lower() and 'To_print' not in x]
filenames = list(sorted(filenames))

files = []
outPdf = PdfFileWriter()
for filename in filenames:
    f = open(filename, 'rb')
    files.append(f)
    file = PdfFileReader(f, strict=False)
    outPdf.appendPagesFromReader(file)
    n_page = file.numPages
    if n_page % 2 == 1:
        outPdf.addBlankPage()

with open('To_print.pdf', 'wb') as outStream:
    outPdf.write(outStream)

for x in files:
    x.close()