from faker.providers import BaseProvider
from faker import Faker
import random
from random import randint
import simple_icd_10 as icd
import csv

def load_data(file):
    with open(file, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)  
    return data  


fake = Faker("en_US")

class HealthcareProvider(BaseProvider):
    professionals = load_data('data/professionals.csv')
    specialties = load_data('data/specialties.csv')
    procedures = load_data('data/procedures.csv')
    diagnosis_code = icd.get_all_codes()
    genders = load_data('data/genders.csv')
    proc_types = load_data('data/procedure_types.csv')
    service_types = load_data('data/service_types.csv')
    duration = load_data('data/duration.csv')
    frequency = load_data('data/frequency.csv')
    dme_equipments = load_data('data/dme_equipments.csv')
    
    def gender(self):
        return self.random_element(self.genders)[0]

    def member_id(self):
        return str(randint(100, 99999999999))

    def provider_id(self):
        return str(randint(1000, 9999999999))

    def healthcare_professional(self):
        return self.random_element(self.professionals)[0]

    def healthcare_specialty(self):
        return self.random_element(self.specialties)[0]

    def healthcare_procedure(self):
        pr = self.random_element(self.procedures)
        print(pr)
        procCode = pr[0]
        procDesc = pr[1]
        procedure = procDesc[:35] + " - " + procCode
        return procedure
    
    def healthcare_diagnosis(self):
        diagCode = self.random_element(self.diagnosis_code)
        diagDesc = icd.get_description(diagCode)[:35]
        diag = diagDesc + " - " + diagCode
        return diag

    def procedure_type(self):
        return self.random_element(self.proc_types)[0]

    def service_type(self):
        return self.random_element(self.service_types)[0]

    def hc_sessions(self):
        return str(randint(1, 25))

    def hc_duration(self):
        return self.random_element(self.duration)[0]

    def hc_frequency(self):
        return self.random_element(self.frequency)[0]
  
    def dme_equipment(self):
        dme = self.random_element(self.dme_equipments)
        hcpcs = dme[0]
        desc = dme[1][:25]
        equipment = hcpcs + " - " + desc
        return equipment   