import pandas as pd
import Levenshtein
import re
import unidecode

class Clients:
    def __init__(self, name, iban, phone, postal, street, street_number, city, state, country, external_id, transaction_reference_id):
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
        self.csv.append(transaction_reference_id)

    def add_csv(self, transaction_reference_id):
        self.csv.append(transaction_reference_id)

    def calculate_match_score(self, name, postal, street, street_number, city, state, country):
        score = 0
        # Weighted Name matching
        if self.name == name:
            score += 10
        if Levenshtein.distance(self.name, name) <= 2:
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
dico_ibans = {}
dico_phones = {}

df = pd.read_csv('data/train/external_parties_train.csv').iloc[1:]

def normalize_phone(number):
    number = re.sub(r'[^0-9+]', '', number)
    if number.startswith('+'):
        # Change + to 00
        number = '00' + number[1:]
    # Remove other non-numeric characters
    return re.sub(r'[^0-9]', '', number)

def find_same_clients(name, iban, phone, postal, street, street_number, city, state, country):
    # Vérifier par IBAN, seulement si IBAN est valide (non nul ou non vide)
    if iban and iban.strip() and iban in dico_ibans:
        return dico_ibans[iban]
    
    # Vérifier par numéro de téléphone, seulement si le numéro est valide
    if phone and phone in dico_phones:
        return dico_phones[phone]
    
    # Fallback à la correspondance avec score
    for client in clients:
        if client.calculate_match_score(name, postal, street, street_number, city, state, country) > 15:
            return client
    return None

def main():
    for i in range(len(df)):
        row = df.iloc[i]
        transaction_reference_id = row['transaction_reference_id']
        name = row['parsed_name']
        iban = row['party_iban']
        iban = iban.strip() if isinstance(iban, str) else None  # Supprimer les espaces et gérer les valeurs nulles
        phone = str(row['party_phone']).strip()  # S'assurer de supprimer les espaces blancs
        phone = normalize_phone(phone) if phone else None  # Normaliser si le téléphone existe
        postal = row['parsed_address_postal_code']
        street = str(row['parsed_address_street_name'])
        street_number = row['parsed_address_street_number']
        city = row['parsed_address_city']
        state = row['parsed_address_state']
        country = row['parsed_address_country']
        external_id = row['external_id']
        
        client = find_same_clients(name, iban, phone, postal, street, street_number, city, state, country)
        
        if client is None:
            new_client = Clients(name, iban, phone, postal, street, street_number, city, state, country, external_id, transaction_reference_id)
            clients.append(new_client)
            
            # Ajouter aux dictionnaires si les valeurs sont valides
            if iban and iban.strip():  # Ignorer les IBANs vides ou nuls
                dico_ibans[iban] = new_client
            if phone:  # Ignorer les numéros de téléphone vides ou nuls
                dico_phones[phone] = new_client
        else:
            client.add_csv(transaction_reference_id)

        if i % 1000 == 0:
            print(f'Processed {i+1}/{len(df)}')

    with open('clients_output.csv', 'w') as f:
        # Écrire l'en-tête
        f.write('transaction_reference_id,external_id\n')
        
        # Écrire les informations des clients
        for client in clients:
            for line in client.csv:
                f.write(f"{line},{client.external_id}\n")

if __name__ == '__main__':
    main()
