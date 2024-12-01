import pandas as pd
from postal.parser import parse_address
import re


df = pd.read_csv('./data/train/external_parties_train.csv')
# transaction_reference_id,party_role,party_info_unstructured,parsed_name,parsed_address_street_name,parsed_address_street_number,parsed_address_unit,parsed_address_postal_code,parsed_address_city,parsed_address_state,parsed_address_country,party_iban,party_phone,external_id
print(parse_address('123 Main St, Apt 4, Springfield, IL 62701, USA'))
# [('123', 'house_number'), ('main st', 'road'), ('apt 4', 'unit'), ('springfield', 'city'), ('il', 'state'), ('62701', 'postcode'), ('usa', 'country')]
#input("Press Enter to continue...")
def normalize_address(row):
    """
    Normalize an address by parsing and reformatting its components.
    
    Parameters:
    - row (pd.Series): The row containing address components.
    
    Returns:
    - str: The normalized address.
    """
    address = row['party_info_unstructured'][len(row['parsed_name']):]
    parsed_address = parse_address(address)
    parsed_address_dict = {component[1]: component[0] for component in parsed_address}

    row['parsed_address_street_name'] = parsed_address_dict.get('road', '')
    row['parsed_address_street_number'] = parsed_address_dict.get('house_number', '')
    row['parsed_address_unit'] = parsed_address_dict.get('unit', '')
    row['parsed_address_postal_code'] = parsed_address_dict.get('postcode', '')
    row['parsed_address_city'] = parsed_address_dict.get('city', '')
    row['parsed_address_state'] = parsed_address_dict.get('state', '')
    row['parsed_address_country'] = parsed_address_dict.get('country', '')

    return row

df = df.apply(normalize_address, axis=1)

def normalize_phone(number):
    number = re.sub(r'[^0-9+]', '', str(number))
    if number.startswith('+'):
        #change + to 00
        number = '00' + number[1:]
    #remove the + leftovers
    number = re.sub(r'[^0-9]', '', number)
    return number

df['party_phone'] = df['party_phone'].apply(normalize_phone)

df.to_csv('./data/train/external_parties_train_corrected.csv', index=False)