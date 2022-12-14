# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python [conda env:root] *
#     language: python
#     name: conda-root-py
# ---

import os
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import PyPDF2
import pandas as pd

url = "https://investmentpolicy.unctad.org/international-investment-agreements/iia-mapping"
key = "treaty-files/"

soup = BeautifulSoup(requests.get(url).content, "html.parser")

all_links = []
for link in soup.find_all("a"):
    if key in link.get("href", ""):
        all_links.append("https://investmentpolicy.unctad.org" + link.get("href"))

bad_links = []
def get_bit_txt(link):
    pdf_bytes = requests.get(link).content
    p = BytesIO(pdf_bytes)
    try:
        read_pdf = PyPDF2.PdfFileReader(p, strict=False)
        count = read_pdf.numPages
        
        print(link)
        
        treaty_txt = ''
    
        for page_number in range(count):
            page = read_pdf.getPage(page_number)
            page_content = page.extractText()
            treaty_txt += '\n ' + page_content
        return treaty_txt
    
    except:
        bad_links.append(link)
        pass


all_bits = [get_bit_txt(l) for l in all_links]

len(all_links)

len(all_bits)

len(bad_links)

bad_links

# +
pdf_bytes = requests.get(all_links[50]).content

p = BytesIO(pdf_bytes)
p.seek(0, os.SEEK_END)
dir(pdf_bytes)
pdf_bytes
