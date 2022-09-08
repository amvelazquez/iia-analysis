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

"""Scrapes UNCTAD website for all international investment agreemets."""

url = "https://investmentpolicy.unctad.org/international-investment-agreements/iia-mapping"
key = "treaty-files/"
soup = BeautifulSoup(requests.get(url).content, "html.parser")


def parse_iia_txt(link):
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
        #return None
        pass


# +
data = []
bad_links = []
table = soup.find('table', attrs={'class':'table ajax'})
table_body = table.find('tbody')


rows = table_body.find_all('tr')
total = len(rows)

for num, row in enumerate(rows):
    
    print(f"Now on treaty {num} out of {total}.")
    
    row_dict = {'link': None,
               'parties': None,
               'status': None,
               'language': None,
               'sign_date': None,
               'entry_force_date': None,
               'termination_date': None,
               'text': None}
    
    for link in row.find_all('a'):
        if key in link.get("href", ""):
            row_dict['link'] = ("https://investmentpolicy.unctad.org" + link.get("href"))
    
    row_dict['text'] = parse_iia_txt(row_dict['link'])
    row_dict['title'] = row.find_all("td", {'data-index' : "2"})[0].text
    row_dict['parties'] = row.find_all("td", {'data-index' : "5"})[0].text
    row_dict['status'] = row.find_all("td", {'data-index' : "4"})[0].text
    row_dict['sign_date'] = row.find_all("td", {'data-index' : "6"})[0].text
    row_dict['entry_force_date'] = row.find_all("td", {'data-index' : "7"})[0].text
    row_dict['termination_date'] = row.find_all("td", {'data-index' : "8"})[0].text
    row_dict['language'] = row.find_all("td", {'data-index' : "9"})[0].text

    data.append(row_dict)
# -

treaty_df = pd.DataFrame(data)

treaty_df

treaty_df.to_csv("raw_iia.csv",index=False)
