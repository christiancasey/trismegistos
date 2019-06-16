# -*- coding: utf-8 -*-
"""
Extract Trismegistos numbers from files in ./Lists
"""

from tqdm import tqdm
import re

vTMNumbers = []
for i in tqdm(range(1,414)):
    f = open('Lists/list_demotic.php?p=%d' % i, 'r')
    strList = f.read()
    f.close()
    
    vTMNumbersI = re.findall(r'<td class="cell_text"><a href="../text/(\d+)">', strList)
    vTMNumbers.extend(vTMNumbersI)
#<td class="cell_text"><a href="../text/(\d+)">