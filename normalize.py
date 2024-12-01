import re
import unidecode

def normalize_phone(number):
	number = re.sub(r'[^0-9+]', '', number)
	if number.startswith('+'):
		#change + to 00
		number = '00' + number[1:]
	#remove the + leftovers
	number = re.sub(r'[^0-9]', '', number)
	return number

def normalize_name(name):
	# convert accents to normal characters
	name = unidecode.unidecode(name)
	# Remove all non-alphabetic characters but keep spaces and dots
	name = re.sub(r'[^a-zA-Z\s.]', '', name)
	# Remove all double spaces and replace with single space
	name = re.sub(r'\s+', ' ', name)
	# Convert to lowercase
	name = name.lower()
	# Check if name contant duplicates substrings
	name_tokens = name.split()
	#remove duplicates from tokens
	name_tokens = list(dict.fromkeys(name_tokens))
	#convert back to name
	name = ' '.join(name_tokens)
	return name


def main():
	# Test the function
	assert(normalize_phone('0086+14566541548x37772') == normalize_phone('+ 86 +1456654-1548x377 72'))
	assert(normalize_name('josé') == normalize_name('Jose'))

if __name__ == '__main__':
	main()
