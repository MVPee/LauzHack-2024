from metaphone import doublemetaphone
import Levenshtein
from nameparser import HumanName
from normalize import normalize_name

def compare_names(name1, name2):

	#if name1 || name 2 contains letter followed by dot, check if name1 || name2 contains the same beginning letter
	if len(name1) >= 2 and len(name2) >= 2:
		if name1[1] == '.' or name2[1] == '.' and name1[0] == name2[0]:
			return True

	# Get the metaphone of the names
	metaphone1 = doublemetaphone(name1)
	metaphone2 = doublemetaphone(name2)

	# Compare the metaphones
	if (metaphone1[0] and metaphone2[0] and (metaphone1[0] == metaphone2[0] or metaphone1[0] == metaphone2[1])) or \
	   (metaphone1[1] and metaphone2[1] and (metaphone1[1] == metaphone2[0] or metaphone1[1] == metaphone2[1])):
		return True

	# Compare the Levenshtein distance of the names
	if Levenshtein.distance(name1, name2) <= 2:
		return True

	return False

def test_name_match(name1, name2):
	# Parse the names to normalize them (remove titles, suffixes, etc.)
	name1 = normalize_name(name1)
	name2 = normalize_name(name2)

	parsed_name1 = HumanName(name1)
	parsed_name2 = HumanName(name2)

	#or don't use HumanName and detect titles, suffixes, etc. in the names
	#and remove them before comparing
	# def remove_titles_suffixes(name):
	# 	titles = ['mr', 'mrs', 'ms', 'dr', 'prof', 'miss', 'sir', 'madam', 'lady', 'lord']
	# 	suffixes = ['jr', 'sr', 'ii', 'iii', 'iv', 'v', 'phd', 'md', 'dds', 'esq']
	# 	others = ['corp', 'inc', 'ltd', 'llc', 'group', 'grp', 'co', 'company', 'associates', 'partners', 'plc', 'gmbh']
	# 	name_parts = name.lower().split()
	# 	name_parts = [part for part in name_parts if part not in titles and part not in suffixes and part not in others]
	# 	return ' '.join(name_parts)

	# name1 = remove_titles_suffixes(name1)
	# name2 = remove_titles_suffixes(name2)


	#compare first names of both then last names of both
	if compare_names(parsed_name1.first, parsed_name2.first) and compare_names(parsed_name1.last, parsed_name2.last):
		return True
	return False


if __name__ == "__main__":
	test_name_match("jcclure and sons grp.", "mcclure and and sons")
	# test_name_match("j. cmdonald", "dr. john mcdonald iii")
	# test_name_match("Smith", "Smythe")
	# test_name_match("Schmidt", "Smitt")