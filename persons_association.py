import pandas as pd
import re


#df = pd.read_csv('./data/train/external_parties_train.csv')
df = pd.read_csv('./data/test/external_parties_test_corrected.csv')
df = df.fillna('')
# transaction_reference_id,party_role,party_info_unstructured,parsed_name,parsed_address_street_name,parsed_address_street_number,parsed_address_unit,parsed_address_postal_code,parsed_address_city,parsed_address_state,parsed_address_country,party_iban,party_phone,external_id

class Person:
    id = 0
    total = 0
    def __init__(self):
        self.id = Person.id
        Person.id += 1
        Person.total += 1
        self.namesVectors = []
        self.addressesVectors = []
        self.IBANS = set()
        self.phones = set()
        self.transactions = set()

    def addData(self, row):
        #if row['parsed_name'] and row['parsed_name'] not in self.namesVectors:
        #    self.namesVectors.append(row['parsed_name'])
        #self.addressesVectors.append(str(row['parsed_address_street_name']) + ' ' + str(row['parsed_address_street_number']) + ' ' + str(row['parsed_address_unit']) + ' ' + str(row['parsed_address_postal_code']) + ' ' + str(row['parsed_address_city']) + ' ' + str(row['parsed_address_state']) + ' ' + str(row['parsed_address_country']))
        if row['party_iban'] and row['party_iban'] not in self.IBANS:
            self.IBANS.add(row['party_iban'])
        if row['party_phone'] and row['party_phone'] not in self.phones:
            self.phones.add(row['party_phone'])
        self.transactions.add(row['transaction_reference_id'])

    def __str__(self):
        return f"Person {self.id}: {self.namesVectors}, {self.addressesVectors}, {self.IBANS}, {self.phones}"
    
    def count(self):
        return len(self.transactions) + len(self.IBANS) + len(self.phones)


ibans = {}
phones = {}

num_rows = df.shape[0]
for index, row in df.iterrows():
    if index % 1000 == 0:
        print(f"{index}/{num_rows}", end='\r')
    phone_person = phones.get(row['party_phone'], None) if row['party_phone'] else None
    iban_person = ibans.get(row['party_iban'], None) if row['party_iban'] else None
    if phone_person and not iban_person:
        phone_person.addData(row)
        if row['party_iban']:
            ibans[row['party_iban']] = phone_person
    elif iban_person and not phone_person:
        iban_person.addData(row)
        if row['party_phone']:
            phones[row['party_phone']] = iban_person
    elif not phone_person and not iban_person:
        person = Person()
        person.addData(row)
        if row['party_iban']:
            ibans[row['party_iban']] = person
        if row['party_phone']:
            phones[row['party_phone']] = person
    else:
        if phone_person != iban_person:
            #phone_person.namesVectors += iban_person.namesVectors
            #phone_person.addressesVectors += iban_person.addressesVectors
            if phone_person.count() > iban_person.count():
                phone_person.IBANS.update(iban_person.IBANS)
                phone_person.phones.update(iban_person.phones)
                phone_person.transactions.update(iban_person.transactions)
                for iban in iban_person.IBANS:
                    ibans[iban] = phone_person
                for phone in iban_person.phones:
                    phones[phone] = phone_person
                Person.total -= 1
                del iban_person
            else:
                iban_person.IBANS.update(phone_person.IBANS)
                iban_person.phones.update(phone_person.phones)
                iban_person.transactions.update(phone_person.transactions)
                for iban in phone_person.IBANS:
                    ibans[iban] = iban_person
                for phone in phone_person.phones:
                    phones[phone] = iban_person
                Person.total -= 1
                del phone_person
            """ iban_person.addData(row)
            if row['party_phone']:
                phones[row['party_phone']] = iban_person
            if row['party_iban']:
                ibans[row['party_iban']] = iban_person """
        else:
            phone_person.addData(row)
            if row['party_iban']:
                ibans[row['party_iban']] = phone_person
            if row['party_phone']:
                phones[row['party_phone']] = phone_person
    
    


print("Unique persons:", Person.total)

""" print("Persons:")
for person in phones.values():
    print(person) """

# export persons to csv: transaction_reference_id,external_id

# get each different person in ibans or phones
persons = set()
for person in phones.values():
    persons.add(person)
for person in ibans.values():
    persons.add(person)

print("Persons:", len(persons))
print("Diff:", len(persons) - Person.total)

output = []
df_copy = df.copy()
for person in persons:
    if len(person.transactions) > 1:
        for transaction in person.transactions:
            output.append([transaction, person.id])
            #output = output.append({'transaction_reference_id': transaction, 'external_id': person.id}, ignore_index=True)
            #df_copy = df_copy[df_copy['transaction_reference_id'] != transaction]

output = pd.DataFrame(output, columns=['transaction_reference_id', 'external_id'])
output.to_csv('./outputs/persons_associations_corrected .csv', index=False)