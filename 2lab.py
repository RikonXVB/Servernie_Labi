import json

class Airplane:
    def __init__(self, model, capacity, payload, range_of_flight, fuel_consumption):
        self.model = model  # Модель самолета
        self.capacity = capacity  # Вместимость пассажиров
        self.payload = payload  # Грузоподъемность
        self.range_of_flight = range_of_flight  # Дальность полета
        self.fuel_consumption = fuel_consumption  # Расход топлива (л/ч)

    def __str__(self):
        return f"{self.model}: Вместимость {self.capacity}, Грузоподъемность {self.payload}, Дальность {self.range_of_flight}, Расход {self.fuel_consumption}"

class PassengerPlane(Airplane):
    def __init__(self, model, capacity, payload, range_of_flight, fuel_consumption):
        super().__init__(model, capacity, payload, range_of_flight, fuel_consumption)

class CargoPlane(Airplane):
    def __init__(self, model, capacity, payload, range_of_flight, fuel_consumption):
        super().__init__(model, capacity, payload, range_of_flight, fuel_consumption)

class Airline:
    def __init__(self, name):
        self.name = name
        self.airplanes = []

    def add_airplane(self, airplane):
        self.airplanes.append(airplane)

    def total_capacity(self):
        return sum(plane.capacity for plane in self.airplanes)

    def total_payload(self):
        return sum(plane.payload for plane in self.airplanes)

    def sort_by_range(self):
        return sorted(self.airplanes, key=lambda plane: plane.range_of_flight, reverse=True)

    def find_planes_by_fuel_consumption(self, min_fuel, max_fuel):
        return [plane for plane in self.airplanes if min_fuel <= plane.fuel_consumption <= max_fuel]

    def load_from_file(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            for plane_data in data:
                plane_type = plane_data.pop('type')  
                if plane_type == 'PassengerPlane':
                    self.add_airplane(PassengerPlane(**plane_data))
                elif plane_type == 'CargoPlane':
                    self.add_airplane(CargoPlane(**plane_data))


    def save_to_file(self, filename):
        data = [{'model': plane.model, 'capacity': plane.capacity, 'payload': plane.payload,
                 'range_of_flight': plane.range_of_flight, 'fuel_consumption': plane.fuel_consumption,
                 'type': 'PassengerPlane' if isinstance(plane, PassengerPlane) else 'CargoPlane'}
                for plane in self.airplanes]
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

def main():
    # Создаем авиакомпанию
    airline = Airline("SkyFly")

    # Пример добавления самолетов вручную
    airline.add_airplane(PassengerPlane("Boeing 737", 150, 20000, 5000, 3000))
    airline.add_airplane(CargoPlane("Antonov An-124", 0, 150000, 4000, 8000))
    airline.add_airplane(PassengerPlane("Airbus A320", 180, 22000, 6000, 3200))

    # Загрузка самолетов из файла
    airline.load_from_file('airplanes.json')

    # Показ общей вместимости и грузоподъемности
    print(f"Общая вместимость: {airline.total_capacity()} пассажиров")
    print(f"Общая грузоподъемность: {airline.total_payload()} кг")

    # Сортировка самолетов по дальности полета
    print("\nСамолеты, отсортированные по дальности полета:")
    sorted_planes = airline.sort_by_range()
    for plane in sorted_planes:
        print(plane)

    # Поиск самолетов по расходу топлива
    min_fuel = 3000
    max_fuel = 5000
    print(f"\nСамолеты с расходом топлива от {min_fuel} до {max_fuel}:")
    planes_by_fuel = airline.find_planes_by_fuel_consumption(min_fuel, max_fuel)
    for plane in planes_by_fuel:
        print(plane)

    # Сохранение данных в файл
    airline.save_to_file('airplanes_output.json')

if __name__ == "__main__":
    main()
