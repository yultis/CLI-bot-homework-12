from collections import UserDict
from datetime import datetime
import pickle


# The base class for storing field values
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

# Class representing the name field, inheriting from Field
class Name(Field):
    def __init__(self, value):
        super().__init__(value)

# Class representing the phone field, inheriting from Field
class Phone(Field):
    def __init__(self, value):
        # Validates and sets the phone number value
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must contain 10 digits.")
        super().__init__(value)

    # Allows changing the phone number value with validation
    def set_value(self, new_value):
        if len(new_value) != 10 or not new_value.isdigit():
            raise ValueError("Phone number must contain 10 digits.")
        self.value = new_value


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        super().__init__(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        try:
            datetime.strptime(new_value, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Incorrect date format, should be YYYY-MM-DD")
        self._value = new_value


# Class representing a record
class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    # Adds a phone number to the record
    def add_phone(self, phone):
        new_phone = Phone(phone)
        self.phones.append(new_phone)

    # Removes a phone number from the record
    def remove_phone(self, phone):
        for p in self.phones:
            if str(p) == phone:
                self.phones.remove(p)
                break

    # Edits an existing phone number in the record
    def edit_phone(self, old_phone, new_phone):
        phone_exists = False
        for p in self.phones:
            if str(p) == old_phone:
                p.set_value(new_phone)
                phone_exists = True
                break
        
        if not phone_exists:
            raise ValueError(f"Phone number '{old_phone}' does not exist in this record.")

    # Finds a phone number in the record
    def find_phone(self, phone_number):
        for p in self.phones:
            if str(p) == phone_number:
                return p  # Returns the phone number value
        return None  # Returns None if the phone is not found

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.now().date()
            birthday_date = datetime.strptime(self.birthday.value, "%Y-%m-%d").date()

            next_birthday_year = today.year
            if (today.month, today.day) > (birthday_date.month, birthday_date.day):
                next_birthday_year += 1

            birthday_date = birthday_date.replace(year=next_birthday_year)
            days_to_birthday = (birthday_date - today).days
            return days_to_birthday
        else:
            return None
    
    # String representation of the record
    def __str__(self):
        return f"Contact name: {self.name}, phones: {'; '.join(str(p) for p in self.phones)}"

# AddressBook class extending UserDict for managing records
class AddressBook(UserDict):
    # Adds a record to the address book
    def add_record(self, record):
        self.data[record.name.value] = record

    # Finds a record by name in the address book
    def find(self, name):
        return self.data.get(name)
    
    # Deletes a record by name from the address book
    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            print(f"The record '{name}' does not exist in the address book.")

    def __iter__(self, chunk_size=5):
        records = list(self.data.values())  # List of all records
        current = 0

        while current < len(records):
            yield records[current : current + chunk_size]  # Returns N records
            current += chunk_size

    # Save the data to a file using pickle serialization
    def save_to_file(self, file_name):
        with open(file_name, 'wb') as fh:
            pickle.dump(self.data, fh)

    # Load the data from a file using pickle deserialization
    def load_from_file(self, file_name):   
        with open(file_name, 'rb') as fh:
            self.data = pickle.load(fh)

    # Search for records based on a value in either the name or phone number
    def search(self, value):
        results = []
        for record in self.data.values():
        # Check if the value matches in the name (case-insensitive)
            if value.lower() in record.name.value.lower():
                results.append(record)
        # Check if the value matches in any phone number
            for phone in record.phones:
                if value in phone.value:
                    results.append(record)
                    break  # Break after finding a match in phones to avoid duplicates
        return results