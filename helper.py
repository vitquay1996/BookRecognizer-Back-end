import os
import sys

"""
Check if a string represents an integer
"""
def RepresentsInt(s):
	try:
		int(s)
		return True
	except ValueError:
		return False

"""
Retrieve isbn from book image
"""
def get_isbn_from_image(img_path):
	import selenium
	from selenium import webdriver
	from selenium.webdriver.common.keys import Keys
	from selenium.webdriver.chrome.options import Options
	from selenium.webdriver.support.ui import WebDriverWait

	chrome_options = Options()
	chrome_options.add_argument('--headless')

	driver = webdriver.Chrome(chrome_options=chrome_options)
	driver.get('https://images.google.com/')
	search_buttons = WebDriverWait(driver, 10).until(lambda x: x.find_elements_by_class_name('gsst_a'))
	print(search_buttons)
	search_image_button = search_buttons[0]
	search_image_button.click()
	file_upload = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_id('qbfile'))
	file_upload.send_keys(
		os.path.abspath(img_path)
		)
	# retrieve search results
	search_results = WebDriverWait(driver, 10).until(lambda x: x.find_elements_by_class_name('r'))
	print("There are {} search results!".format(len(search_results)))
	print("Printing search results:")
	search_len = len(search_results)
	for res in search_results:
		print(res.text)

	from difflib import SequenceMatcher
	best_name = '1'*200
	for j in range(2):
		for i in range(j, search_len, 2):
			if i < search_len and i+1 < search_len:
				print('Longest common substring:')
				a = search_results[i].text
				b = search_results[i+1].text
				s = SequenceMatcher(None, a, b)
				matched = s.find_longest_match(0, len(a), 0, len(b))
				common_substring = a[int(matched[0]) : int(matched[0]) + int(matched[2])]
				if len(common_substring) < len(best_name):
					best_name = common_substring
					break

	print('Best name: {}'.format(best_name))
	# revisit google and search this instead
	driver.get('https://www.google.com/xhtml')
	search_form = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_name('q'))
	search_form.send_keys(best_name + ' goodreads review')
	search_form.submit()
	search_results = WebDriverWait(driver, 10).until(lambda x: x.find_elements_by_class_name('r'))
	print("There are {} search results!".format(len(search_results)))
	print("Printing search results:")
	for res in search_results:
		print(res.text)
	# click goodread link
	gr = search_results[0]
	gr.click()
	# click show data button
	show_data_button = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_id('bookDataBoxShow'))
	driver.execute_script('document.getElementById(\'bookDataBoxShow\').click()')
	# find isbn
	isbns = WebDriverWait(driver, 10).until(lambda x: x.find_elements_by_class_name('infoBoxRowItem'))
	isbn_number = '-1'
	for isbn in isbns:
		elem_content = isbn.text
		cut_idx = elem_content.find(' ')
		if not cut_idx == -1:
			elem_content = elem_content[:cut_idx]
		if RepresentsInt(elem_content):
			isbn_number = elem_content
			break
	print('ISBN number: {}'.format(isbn_number))
	driver.quit()
	return isbn_number
