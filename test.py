import pandas as pd
import Levenshtein
import re

class Clients:
    def __init__(self, name, iban, phone, postal, street, street_number, city, state, country, external_id, csv_row):
        self.name = name
        self.iban = iban
        self.phone = phone
        self.postal = postal
        self.city = city
        self.state = state
        self.country = country
        self.street = street
        self.street_number = street_number
        self.external_id = external_id
        self.csv = []
        self.csv.append(csv_row)

    def add_csv(self, csv_row):
        self.csv.append(csv_row)

    def check_iban(self, iban):
        return self.iban == iban

    def check_phone(self, phone):
        return self.phone == phone

    def check_external_id(self, external_id):
        return self.external_id == external_id

    def calculate_match_score(self, name, postal, street, street_number, city, state, country):
        score = 0

        # Weighted Name matching
        if self.name == name:
            score += 10
        elif Levenshtein.distance(self.name, name) <= 2:
            score += 5

        
        if self.street_number == street_number:
            score += 5
        if Levenshtein.distance(self.street, street) <= 2:
            score += 8

        if self.postal == postal:
            score += 8
        if self.city == city:
            score += 5
        if self.state == state:
            score += 3
        if self.country == country:
            score += 2

        return score


    def __str__(self):
        return f'Name: {self.name}, IBAN: {self.iban}, phone: {self.phone}'

clients = []
df = pd.read_csv('data/train/external_parties_train.csv').iloc[1:]

def find_same_clients(name, iban, phone, postal, street, street_number, city, state, country, external_id):
    for client in clients:
        # if client.check_external_id(external_id):
        #     return client
        if client.check_iban(iban):
            return client
        if phone and client.check_phone(phone):
            return client
        if client.calculate_match_score(name, postal, street, street_number, city, state, country) > 12:
            return client
    return None

def normalize_phone(number):
    number = re.sub(r'[^0-9+]', '', number)
    if number.startswith('+'):
        #change + to 00
        number = '00' + number[1:]
    #remove the + leftovers
    number = re.sub(r'[^0-9]', '', number)
    return number

def main():
    for i in range(len(df)):
        row = df.iloc[i]
        name = row['parsed_name']
        iban = row['party_iban']
        phone = str(row['party_phone'])
        phone = normalize_phone(phone)
        postal = row['parsed_address_postal_code']
        street = str(row['parsed_address_street_name'])
        street_number = row['parsed_address_street_number']
        city = row['parsed_address_city']
        state = row['parsed_address_state']
        country = row['parsed_address_country']
        external_id = row['external_id']
        client = find_same_clients(name, iban, phone, postal, street, street_number, city, state, country, external_id)
        if client is None:
            new_client = Clients(name, iban, phone, postal, street, street_number, city, state, country, external_id, row.to_dict())
            clients.append(new_client)
        else:
            client.add_csv(row.to_dict())

    with open('clients_output.csv', 'w') as f:
        # Write the header row
        f.write('name,iban,phone,csv_count\n')
        
        # Write each client's information
        for client in clients:
            f.write(f'"{client.name}", "{client.iban}", "{client.phone}", "{len(client.csv)}"\n')
            for line in client.csv:
                f.write(f'\t{line}\n')
        f.write(f'\n\n{len(clients)}')

if __name__ == '__main__':
    main()
