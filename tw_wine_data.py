#scraping wine data from total wine's site for Sacramento
##ISSUE: I am pulling about 1000 fewer records than I should be. Why is that?

import requests
import pyquery as pq 
import json

total_count = 7848
html_length = 1000
start_no = 1
remaining_count = total_count - start_no + 1
wine_list = []
counter = remaining_count

while remaining_count > 0:

	if remaining_count >= 1000:
		per_page = 1000
	else:
		per_page = remaining_count

	print('Downloading HTML...')
	print(remaining_count, start_no, per_page)

	url = 'http://www.totalwine.com/eng/categories/wine!viewPerPage/{per_page}!startRow/{start_no}'.format(per_page=per_page, start_no=start_no)
	cookies={'TOTALWINE_COOKIEPREFERREDLOCATION':'PICKUP|CA|17804'}

	r = requests.get(url, cookies=cookies)

	#parse html
	print('Parsing HTML...')
	parsed = pq.PyQuery(r.text)

	#grab all of the a tags with hrefs to whisky detail pages
	a_tags = parsed('.moreBtn')

	#grab hrefs from all the a tags
	links = [tag.attrib['href'] for tag in a_tags]

	print('Drilling into detail product pages')
			
	for link in links:
		print(counter)

		prod = requests.get(link)
		prod_parsed = pq.PyQuery(prod.text) #or prod.content?

		name = prod_parsed('#additionalDetails').find('h1').text() 
		long_desc = prod_parsed('#review-main-box').find('p').text()	
		color = prod_parsed('strong:contains("Type")').parent().siblings().text()
		varietal = prod_parsed('strong:contains("Varietal")').parent().siblings().text()
		location = prod_parsed('strong:contains("Country/State")').parent().siblings().text()

		item = {
			'name': name,
			'varietal': varietal,
			'location': location,
			'color': color,
			'description': long_desc
		}
		wine_list.append(item)
		counter -= 1

	#incrementing starting item number
	start_no += per_page
	remaining_count -= per_page

wine_list = json.dumps(wine_list)
