c# -*- coding: utf-8 -*-
"""
Extract Trismegistos numbers from files in ./Lists
Download the corresponding webpages and save in ./Pages
Extract data from pages and create dataframe

@author: Christian Casey
"""

from tqdm import tqdm
import re
import urllib
import os
import glob
import time
import pandas


#%% Download all lists, save them in './Lists/'
for iPage in tqdm(range(1,415)):
	
	strURL = 'https://www.trismegistos.org/tm/list_demotic.php?p=%d' % iPage
	strPage = urllib.request.urlopen(strURL).read().decode('utf-8')
	
	f = open('Lists/list_demotic.php?p=%d' % iPage, 'w')
	f.write(strPage)
	f.close()

#%% Loop through lists and extract TM Numbers
vTMNumbers = []
for i in tqdm(range(1,414)):
	f = open('Lists/list_demotic.php?p=%d' % i, 'r')
	strList = f.read()
	f.close()
	
	vTMNumbers.extend( re.findall(r'<td class="cell_text"><a href="../text/(\d+)">', strList) )
	

#%% Clean out 'Pages' directory (for debugging)
#vFiles = glob.glob('Pages/*')
#for strFilename in vFiles:
#    os.remove(strFilename)

#%% Download all text entry pages, save them to './Pages/'
	
for i in tqdm(range(len(vTMNumbers))):
	
	strTMNumber = vTMNumbers[i]
	
	strURL = 'https://www.trismegistos.org/text/%s' % strTMNumber
	strPage = urllib.request.urlopen(strURL).read().decode('utf-8')
	
	f = open('Pages/%s.html' % strTMNumber, 'w')
	f.write(strPage)
	f.close()
	
	print("\n%d" % i)
	
	time.sleep(6)	# Prevents overburdening TM server
	
#%% Delete foobarred page(s)
vFiles = [ '51399' ]
for strFilename in vFiles:
    os.remove('Pages/%s.html', strFilename)

#%% Load pages and extract data for each text
vFiles = glob.glob('Pages/*.html')
vFiles.sort()
vData = []


for strFilename in tqdm(vFiles):
	
	f = open(strFilename, 'r')
	strPage = f.read()
	f.close()
	
	vRow = []
	vRow.append( re.findall(r'Pages/(\d+)\.html', strFilename)[0] )
	
	# Find general period and date
	vFound = re.findall(r'<a href=.*?min_date.*?>(.*?)</a>[:\s]*(.*?)</span>', strPage)[0]
	
	# Split dates into start and end if they contain a dash
	strDate = vFound[1]
	iDash = strDate.find(' - ')
	if iDash < 0:
		vDates = [ strDate, '' ]
	else:
		vDates = [ strDate[:iDash], strDate[iDash+3:] ]
		
	
	vRow.append(vFound[0]), vRow.append(vFound[1]) # Add period and date string to data
		
	# Convert BC into negative, AD into positive
	# First deal with situations where BC is omitted, e.g. 'BC 5 - 3'  'BC 5 - BC 3'
	if vDates[0].find('BC ') >= 0 and vDates[1].find('AD ') < 0:
		vDates[1] = 'BC ' + vDates[1]
	
	vDates = [ str.replace('BC ', '-') for str in vDates ]
	vDates = [ str.replace('AD ', '') for str in vDates ]
	
	# Use the presence of a question mark to indicate uncertainty in the date
	vRow.append(strDate.find('?') >= 0)
		
	# Keep year only
	for i in range(2):
		# Full date format: Y M D
		vYear = re.findall(r'([\-\d]+)\s+[A-Za-z]+\s*\d*', vDates[i])
		if len(vYear) > 0:
			vDates[i] = vYear[0]
		else:
			# Deal with no year: '-Jul 15'
			if len(re.findall(r'([A-Za-z]+)', vDates[i])) > 0:
				vDates[i] = ''
			vYear = re.findall(r'([\-0-9]+)', vDates[i])
			if len(vYear) > 0:
				vDates[i] = vYear[0]
			else:
				vDates[i] = ''
				
		# Deal with edge case: '-'
		if vDates[i] == '-':
			vDates[i] = ''
		
		vRow.append(vDates[i])
		
	
	# Find provenance
	vFound = re.findall(r'<a href=.*?place.*?>(.*?)</a>', strPage)[0]
	vRow.append(vFound)
	
	# Fine language
	vFound = re.findall(r'<span class=\"semibold\">Language/script:</span>\s*([^<]*)<', strPage)[0]
	vRow.append(vFound)
	
	vData.append(vRow)
	
#%% Put data in dataframe and save
df = pandas.DataFrame(vData, columns=['TM Number', 'Period', 'Date String', 'Uncertain', 'Date (Start)', 'Date (End)', 'Provenance', 'Language'])
df.to_csv('Text Data.csv')


































