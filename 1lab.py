class Train:
    def __init__(self, destination, train_number, departure_time, seats):
        self.destination = destination  # Пункт назначения
        self.train_number = train_number  # Номер поезда
        self.departure_time = departure_time  # Время отправления (в формате HH:MM)
        self.seats = seats  # Словарь с количеством мест: общие, купе, плацкарт, люкс

    def __str__(self):
        return f"Поезд {self.train_number} -> {self.destination} | Время отправления: {self.departure_time} | Места: {self.seats}"

# Создание массива объектов поездов
trains = [
    Train("Москва", 101, "08:00", {"общие": 50, "купе": 20, "плацкарт": 30, "люкс": 5}),
    Train("Санкт-Петербург", 102, "12:30", {"общие": 0, "купе": 15, "плацкарт": 25, "люкс": 2}),
    Train("Москва", 103, "15:45", {"общие": 10, "купе": 10, "плацкарт": 20, "люкс": 0}),
    Train("Воронеж", 104, "10:00", {"общие": 0, "купе": 8, "плацкарт": 30, "люкс": 0}),
    Train("Москва", 105, "18:15", {"общие": 5, "купе": 12, "плацкарт": 25, "люкс": 1}),
]

# a) Список поездов, следующих до заданного пункта назначения
def trains_to_destination(destination):
    result = [train for train in trains if train.destination == destination]
    return result

# b) Список поездов, следующих до заданного пункта назначения и отправляющихся после заданного часа
def trains_to_destination_after_time(destination, time):
    result = [train for train in trains if train.destination == destination and train.departure_time > time]
    return result

# c) Список поездов, следующих до заданного пункта назначения и имеющих общие места
def trains_with_common_seats(destination):
    result = [train for train in trains if train.destination == destination and train.seats["общие"] > 0]
    return result


destination_input = "Москва"
time_input = "12:00"

# Вывод списка поездов до заданного пункта назначения
print(f"Поезда до {destination_input}:")
for train in trains_to_destination(destination_input):
    print(train)

# Вывод списка поездов до заданного пункта назначения, отправляющихся после заданного времени
print(f"\nПоезда до {destination_input}, отправляющиеся после {time_input}:")
for train in trains_to_destination_after_time(destination_input, time_input):
    print(train)

# Вывод списка поездов до заданного пункта назначения, имеющих общие места
print(f"\nПоезда до {destination_input} с общими местами:")
for train in trains_with_common_seats(destination_input):
    print(train)
