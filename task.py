from collections import defaultdict, UserDict
from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    # реалізація класу
		pass


class Phone(Field):
    def __init__(self, value):
        if len(value) == 10 and value.isdigit():
            super().__init__(value)
        else:
            raise ValueError("Phone not valid")
        

class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))
        
    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p != phone]
    
    def edit_phone(self, old_phone, new_phone):
        for i, phone in enumerate(self.phones):
            if str(phone) == old_phone:
                self.phones[i].value = new_phone
                break 
        else:
            raise ValueError("Номер не знайдено")

    def find_phone(self, phone):
        for p in self.phones:
            if str(p) == phone:
                return p
        return None
    
    def add_birthday(self, birthday): 
        self.birthday = Birthday(birthday)

    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
    
    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def find_next_weekday(self, day,weekday: int):
        days_ahead = weekday - day.weekday()
        if days_ahead <= 0:
            days_ahead += 7
            next_weekday = day + timedelta(days = days_ahead)
            if next_weekday.weekday() in [5,6]:
                next_weekday = next_weekday + timedelta(days = (7 - next_weekday.weekday()))
            return next_weekday
        
    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        current_date = datetime.today().date()
        next_week = current_date + timedelta(weeks=1)
        for record in self.values():
            if record.birthday:
                next_birthday = record.birthday.date.replace(year=current_date.year)
                if current_date <= next_birthday <= next_week:
                    if next_birthday.weekday() in [5,6]:
                        next_birthday = self.find_next_weekday(next_birthday, 0)
                    upcoming_birthdays.append(f"{record.name.value}: {next_birthday.strftime("%d,%m,%Y")}")
                elif current_date > next_birthday:
                    next_birthday = record.birthday.date.replace(year=current_date.year + 1)
                    if current_date <= next_birthday <= next_week:
                        if next_birthday.weekday() in [5,6]:
                            next_birthday = self.find_next_weekday(next_birthday, 0)
                        upcoming_birthdays.append(f"{record.name.value}: {next_birthday.strftime("%d,%m,%Y")}")
        return upcoming_birthdays 
    

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено
    

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "Сheck the validity of the entered data"
        except IndexError:
            return "Enter user name"
    return inner

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
        name, old_phone, new_phone = args
        record = book.find(name)
        if record:
            record.edit_phone(old_phone, new_phone)
            return "Contact updated." 
        else:
            return "Перевірте вірність введених даних" 

@input_error
def show_phone(args,book: AddressBook):
        name = args[0]
        record = book.find(name)
        if record:
            if record.phones:
                return "; ".join([str(phone) for phone in record.phones])
        else: 
            return "Користувача з таким іменем не знайдено, перевірте вірність введених даних"
    
@input_error
def show_all(book: AddressBook):
    result = []
    if len(book) > 0:
        for record in book.values():
            result.append(f"{record.name.value}: {'; '.join([p.value for p in record.phones])}; Birthday: {record.birthday.value if record.birthday else "No birthday"}")
        return result
    else:
        return book or "Список контактів порожній"
        
    
@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday) 
        return "Birthday added."
    elif record is None:
        record = Record(name)
        record.add_birthday(birthday)
        book.add_record(record) 
        return "Birthday added."
    else:
        return "Перевірте вірність введених даних"

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return record.birthday
    else: 
        return "Перевірте вірність введених даних та повторіть спробу"

@input_error
def birthdays(args, book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return upcoming_birthdays
    else:
        return ["Немає користувачів, яких потрібно привітати на наступному тижні."]
    

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def main():
    book = load_data()
    # book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args,book))
        elif command == "all":
            contact_list = show_all(book)
            for contact in contact_list:
                print(contact)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args,book))
        elif command == "birthdays":  
            birthdays_list = birthdays(args,book)
            for birthday in birthdays_list:
                print(birthday)  
        else:
            print("Invalid command.")
    save_data(book)

if __name__ == "__main__":
    main()