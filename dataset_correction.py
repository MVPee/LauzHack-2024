import pandas as pd
from postal.parser import parse_address
import re

if __name__ == '__main__':
    df = pd.read_csv('./data/train/external_parties_train.csv')
# transaction_reference_id,party_role,party_info_unstructured,parsed_name,parsed_address_street_name,parsed_address_street_number,parsed_address_unit,parsed_address_postal_code,parsed_address_city,parsed_address_state,parsed_address_country,party_iban,party_phone,external_id
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



def normalize_phone(number):
    number = re.sub(r'[^0-9+]', '', str(number))
    if number.startswith('+'):
        #change + to 00
        number = '00' + number[1:]
    #remove the + leftovers
    number = re.sub(r'[^0-9]', '', number)
    return number


def normalize_data(row):
    """
    Normalize the data in a row.
    
    Parameters:
    - row (pd.Series): The row to normalize.
    
    Returns:
    - pd.Series: The normalized row.
    """
    row = normalize_address(row)
    row['party_phone'] = normalize_phone(row['party_phone'])
    
    return row

if __name__ == '__main__':
    df = df.apply(normalize_data, axis=1)

    df.to_csv('./data/train/external_parties_train_corrected.csv', index=False)