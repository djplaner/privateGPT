# Copyright (C) 2023 David Jones
# 
# This file is part of privateGPT.
# 
# privateGPT is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# privateGPT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with privateGPT.  If not, see <http://www.gnu.org/licenses/>.

""" 
import.py - Import a blog from a file

Inspired by https://deparkes.co.uk/2021/02/06/parse-wordpress-post-export-with-python/
"""

import feedparser
from pprint import pprint

import sys
import io
 
#-- define global variables

XML_IMPORT = "./djon.es/someassemblagerequired.WordPress.2023-06-02.xml"
OUTPUT_DIR = "../source_documents/"

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

def showFields(entry): 
	""" Dump out all the fields, type and content for the entry"""

	fields = [
			'title', 'title_detail', 'links', 'link', 'published', 
			'published_parsed', 'authors', 'author', 'author_detail', 
			'id', 'guidislink', 'summary', 'summary_detail', 
			'content', 'excerpt_encoded', 'wp_post_id', 
			'wp_post_date', 'wp_post_date_gmt', 'wp_post_modified', 
			'wp_post_modified_gmt', 'wp_comment_status', 
			'wp_ping_status', 'wp_post_name', 'wp_status', 
			'wp_post_parent', 'wp_menu_order', 'wp_post_type', 
			'wp_post_password', 'wp_is_sticky', 'tags']

	# Loop through each of the fields for entry and display
	# - the type and value of the field
	for field in fields:
		print(field, type(entry[field]), entry[field])

def showEntry(entry):
	""" Display misc information about the entry to stdout"""

	print(f"{entry['wp_status']} / {entry['wp_post_type']} Title: {entry['title']}: URL: {entry['link']}")
	pprint(entry['tags'])
	pprint(entry['content'])
	if (len(entry['content']) > 1):
		input("Press Enter to continue...")
	print()

def saveEntryFile(entry):
	"""Create a file for the entry 
	- place the file in OUTPUT_DIR/<fileName>.html
	- where <fileName> is the entry title escaped for filename no longer than 40 chars
	
	The file will be a HTML file 
	- using a standard HTML 5 template 
	- with the entry title as the title
	- entry title will also be a H1 at the start of the page - the title will also be a link to the entry URL
	- first paragraph will be a list of entry tags
	- followed by content
	"""

	##-- create the filename
	#-- remove any non-alphanumeric characters
	#-- replace spaces with hyphens
	fileName=entry['title'].replace(" ", "-").replace(".", "").replace(":", "").replace("?", "").replace("!", "").replace(";", "").replace(",", "").replace("(", "").replace(")", "").replace("'", "").replace('"', "").replace("/", "").replace("\\", "").replace("&", "").replace("=", "").replace("+", "").replace("*", "").replace("#", "").replace("%", "").replace("$", "").replace("@", "")
	#-- truncate to 40 chars
	fileName=f"{OUTPUT_DIR}{fileName[:40]}.html"

	#-- generate a list of tags
	tags = []
	for tag in entry['tags']:
		tags.append(tag['term'])



	#-- create the HTML string 
	html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{entry['title']}</title>
</head>
<body>
<h1><a href="{entry['link']}">{entry['title']}</a></h1>

<p>Tags: {', '.join(tags)}</p>

<p>{entry['content'][0]['value']}</p>

</body>
</html>
"""

	#-- write the HTML string to the file
	with open(fileName, "w", encoding="utf-8") as f:
		f.write(html)

def parse():
	"""Various tests/experiments with parsing a very specific Wordpress export file"""

	data = feedparser.parse("./djon.es/someassemblagerequired.WordPress.2023-06-02.xml")

	posts = []

	status = {}
	categories = {}

	for entry in data['entries']:
		# display the keys of the entry dict

		if entry['wp_status'] != 'publish':
			continue 

		saveEntryFile(entry)
		continue

		#showFields(entry)


		#-- keep a count of the status
		if entry['wp_status'] in status:
			status[entry['wp_status']] += 1
		else:
			status[entry['wp_status']] = 1

		for tag in entry['tags']:
			if tag['term'] in categories:
				categories[tag['term']] += 1
			else:
				categories[tag['term']] = 1

		#return None

	print("---- Status")
	pprint(status)
	print("---- Categories")
	pprint(categories)
	#-- show num of categories
	print(f"Number of categories: {len(categories)}")

	#-- show the top 10 categories
	print("---- Top 10 Categories")
	pprint(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:20])

if __name__  == "__main__":

	parse()
