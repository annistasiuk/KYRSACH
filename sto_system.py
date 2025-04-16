import os
import datetime
from tabulate import tabulate
import uuid
import json
from pathlib import Path


class STOManagementSystem:
    def __init__(self, data_file="sto_data.json"):
        self.data_file = data_file
        self.data = {
            "vehicles": {},
            "repair_orders": {}
        }
        self.load_data()

    def load_data(self):
        if Path(self.data_file).exists():
            try:
                with open(self.data_file, "r", encoding="utf-8") as file:
                    self.data = json.load(file)
            except Exception as e:
                print(f"Помилка завантаження даних: {str(e)}")
                self.data = {"vehicles": {}, "repair_orders": {}}

    def save_data(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as file:
                json.dump(self.data, file, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Помилка збереження даних: {str(e)}")
            return False

    def register_vehicle(self, brand, model, year, reg_number, owner):
        try:
            for vehicle in self.data["vehicles"].values():
                if vehicle["reg_number"] == reg_number:
                    return False, "Помилка: транспортний засіб з таким реєстраційним номером вже існує."

            vehicle_id = str(uuid.uuid4())
            registration_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.data["vehicles"][vehicle_id] = {
                "id": vehicle_id,
                "brand": brand,
                "model": model,
                "year": year,
                "reg_number": reg_number,
                "owner": owner,
                "registration_date": registration_date
            }

            self.save_data()
            return True, "Транспортний засіб успішно зареєстровано."
        except Exception as e:
            return False, f"Помилка при реєстрації транспортного засобу: {str(e)}"

    def edit_vehicle(self, vehicle_id, brand=None, model=None, year=None, reg_number=None, owner=None):
        try:
            if vehicle_id not in self.data["vehicles"]:
                return False, "Транспортний засіб не знайдено."

            vehicle = self.data["vehicles"][vehicle_id]

            if brand:
                vehicle["brand"] = brand
            if model:
                vehicle["model"] = model
            if year:
                vehicle["year"] = year
            if owner:
                vehicle["owner"] = owner
            if reg_number:
                for v_id, v in self.data["vehicles"].items():
                    if v["reg_number"] == reg_number and v_id != vehicle_id:
                        return False, "Помилка: транспортний засіб з таким реєстраційним номером вже існує."
                vehicle["reg_number"] = reg_number

            self.save_data()
            return True, "Інформацію про транспортний засіб успішно оновлено."
        except Exception as e:
            return False, f"Помилка при редагуванні інформації: {str(e)}"

    def delete_vehicle(self, vehicle_id):
        try:
            if vehicle_id not in self.data["vehicles"]:
                return False, "Транспортний засіб не знайдено."

            for order in self.data["repair_orders"].values():
                if order["vehicle_id"] == vehicle_id:
                    return False, "Неможливо видалити: є активні заявки на ремонт для цього транспортного засобу."

            del self.data["vehicles"][vehicle_id]
            self.save_data()
            return True, "Транспортний засіб успішно видалено."
        except Exception as e:
            return False, f"Помилка при видаленні транспортного засобу: {str(e)}"

    def add_repair_order(self, vehicle_id, work_type, parts, resources, estimated_cost):
        try:
            if vehicle_id not in self.data["vehicles"]:
                return False, "Транспортний засіб не знайдено."

            order_id = str(uuid.uuid4())
            date_created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.data["repair_orders"][order_id] = {
                "id": order_id,
                "vehicle_id": vehicle_id,
                "date_created": date_created,
                "work_type": work_type,
                "parts": parts,
                "resources": resources,
                "estimated_cost": estimated_cost,
                "status": "Не оплачено"
            }

            self.save_data()
            return True, "Заявку на ремонт успішно додано."
        except Exception as e:
            return False, f"Помилка при додаванні заявки на ремонт: {str(e)}"

    def mark_order_paid(self, order_id):
        try:
            if order_id not in self.data["repair_orders"]:
                return False, "Заявку не знайдено."

            self.data["repair_orders"][order_id]["status"] = "Оплачено"
            self.save_data()
            return True, "Заявку успішно позначено як оплачену."
        except Exception as e:
            return False, f"Помилка при оновленні статусу заявки: {str(e)}"

    def generate_invoice(self, order_id):
        try:
            if order_id not in self.data["repair_orders"]:
                return False, "Заявку не знайдено."

            order = self.data["repair_orders"][order_id]
            vehicle = self.data["vehicles"][order["vehicle_id"]]

            invoice = f"""
==================================================
                РАХУНОК НА ОПЛАТУ
==================================================
Номер рахунку: {order_id[:8]}
Дата створення: {order["date_created"]}
--------------------------------------------------
Власник: {vehicle["owner"]}
Транспортний засіб: {vehicle["brand"]} {vehicle["model"]}
Реєстраційний номер: {vehicle["reg_number"]}
--------------------------------------------------
Тип робіт: {order["work_type"]}
Запчастини: {order["parts"] or "Не вказано"}
Ресурси: {order["resources"] or "Не вказано"}
--------------------------------------------------
Загальна вартість: {order["estimated_cost"]:.2f} грн.
Статус оплати: {order["status"]}
==================================================
            """

            return True, invoice
        except Exception as e:
            return False, f"Помилка при генерації рахунку: {str(e)}"

    def get_vehicles(self, filter_brand=None, filter_model=None, filter_payment=None):
        try:
            vehicles_list = []

            for vehicle_id, vehicle in self.data["vehicles"].items():
                vehicle_data = vehicle.copy()

                orders_count = 0
                unpaid_orders = 0
                total_cost = 0

                for order in self.data["repair_orders"].values():
                    if order["vehicle_id"] == vehicle_id:
                        orders_count += 1
                        total_cost += order["estimated_cost"]
                        if order["status"] == "Не оплачено":
                            unpaid_orders += 1

                vehicle_data["orders_count"] = orders_count
                vehicle_data["unpaid_orders"] = unpaid_orders
                vehicle_data["total_cost"] = total_cost

                vehicles_list.append(vehicle_data)

            filtered_vehicles = []
            for vehicle in vehicles_list:
                include = True

                if filter_brand and filter_brand.lower() not in vehicle["brand"].lower():
                    include = False

                if filter_model and filter_model.lower() not in vehicle["model"].lower():
                    include = False

                if filter_payment:
                    if filter_payment.lower() == "оплачено" and vehicle["unpaid_orders"] > 0:
                        include = False
                    elif filter_payment.lower() == "не оплачено" and vehicle["unpaid_orders"] == 0:
                        include = False

                if include:
                    filtered_vehicles.append(vehicle)

            return filtered_vehicles
        except Exception as e:
            print(f"Помилка при отриманні списку транспортних засобів: {str(e)}")
            return []

    def get_repair_orders(self, vehicle_id=None):
        try:
            orders_list = []

            for order_id, order in self.data["repair_orders"].items():
                if vehicle_id and order["vehicle_id"] != vehicle_id:
                    continue

                if order["vehicle_id"] in self.data["vehicles"]:
                    vehicle = self.data["vehicles"][order["vehicle_id"]]
                    order_data = order.copy()
                    order_data["brand"] = vehicle["brand"]
                    order_data["model"] = vehicle["model"]
                    order_data["reg_number"] = vehicle["reg_number"]
                    order_data["owner"] = vehicle["owner"]
                    orders_list.append(order_data)

            return orders_list
        except Exception as e:
            print(f"Помилка при отриманні списку заявок: {str(e)}")
            return []


def display_menu():
    menu = """
=============================================
    СИСТЕМА УПРАВЛІННЯ СТО
=============================================
1. Зареєструвати новий транспортний засіб
2. Редагувати інформацію про транспортний засіб
3. Видалити транспортний засіб
4. Додати заявку на ремонт
5. Позначити заявку як оплачену
6. Згенерувати рахунок
7. Переглянути список транспортних засобів
8. Переглянути заявки на ремонт
9. Вихід
=============================================
"""
    print(menu)


def main():
    system = STOManagementSystem()

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        display_menu()

        choice = input("Виберіть опцію (1-9): ")

        if choice == "1":
            print("\n=== Реєстрація нового транспортного засобу ===")
            brand = input("Марка: ")
            model = input("Модель: ")
            year = input("Рік випуску: ")
            reg_number = input("Реєстраційний номер: ")
            owner = input("Власник: ")

            try:
                year = int(year)
                success, message = system.register_vehicle(brand, model, year, reg_number, owner)
                print(message)
            except ValueError:
                print("Помилка: рік випуску має бути числом.")

        elif choice == "2":
            print("\n=== Редагування транспортного засобу ===")
            vehicles = system.get_vehicles()
            if not vehicles:
                print("Немає зареєстрованих транспортних засобів.")
                input("Натисніть Enter для продовження...")
                continue

            print(tabulate([[v['id'][:8], v['brand'], v['model'], v['reg_number'], v['owner']]
                            for v in vehicles],
                           headers=["ID", "Марка", "Модель", "Реєстр. номер", "Власник"]))

            vehicle_id = input("\nВведіть ID транспортного засобу для редагування: ")
            target_vehicle = next((v for v in vehicles if v['id'].startswith(vehicle_id)), None)

            if not target_vehicle:
                print("Транспортний засіб не знайдено.")
                input("Натисніть Enter для продовження...")
                continue

            print(f"\nРедагування {target_vehicle['brand']} {target_vehicle['model']} ({target_vehicle['reg_number']})")
            print("Залиште поле порожнім, якщо не хочете змінювати його.")

            new_brand = input(f"Марка [{target_vehicle['brand']}]: ") or None
            new_model = input(f"Модель [{target_vehicle['model']}]: ") or None
            new_year_str = input(f"Рік випуску [{target_vehicle['year']}]: ")
            new_year = int(new_year_str) if new_year_str else None
            new_reg = input(f"Реєстраційний номер [{target_vehicle['reg_number']}]: ") or None
            new_owner = input(f"Власник [{target_vehicle['owner']}]: ") or None

            success, message = system.edit_vehicle(
                target_vehicle['id'], new_brand, new_model, new_year, new_reg, new_owner
            )
            print(message)

        elif choice == "3":
            print("\n=== Видалення транспортного засобу ===")
            vehicles = system.get_vehicles()
            if not vehicles:
                print("Немає зареєстрованих транспортних засобів.")
                input("Натисніть Enter для продовження...")
                continue

            print(tabulate([[v['id'][:8], v['brand'], v['model'], v['reg_number'], v['owner']]
                            for v in vehicles],
                           headers=["ID", "Марка", "Модель", "Реєстр. номер", "Власник"]))

            vehicle_id = input("\nВведіть ID транспортного засобу для видалення: ")
            target_vehicle = next((v for v in vehicles if v['id'].startswith(vehicle_id)), None)

            if not target_vehicle:
                print("Транспортний засіб не знайдено.")
                input("Натисніть Enter для продовження...")
                continue

            confirm = input(
                f"Ви впевнені, що хочете видалити {target_vehicle['brand']} {target_vehicle['model']} ({target_vehicle['reg_number']})? (y/n): ")
            if confirm.lower() == 'y':
                success, message = system.delete_vehicle(target_vehicle['id'])
                print(message)

        elif choice == "4":
            print("\n=== Додавання заявки на ремонт ===")
            vehicles = system.get_vehicles()
            if not vehicles:
                print("Немає зареєстрованих транспортних засобів.")
                input("Натисніть Enter для продовження...")
                continue

            print(tabulate([[v['id'][:8], v['brand'], v['model'], v['reg_number'], v['owner']]
                            for v in vehicles],
                           headers=["ID", "Марка", "Модель", "Реєстр. номер", "Власник"]))

            vehicle_id = input("\nВведіть ID транспортного засобу для додавання заявки: ")
            target_vehicle = next((v for v in vehicles if v['id'].startswith(vehicle_id)), None)

            if not target_vehicle:
                print("Транспортний засіб не знайдено.")
                input("Натисніть Enter для продовження...")
                continue

            print(
                f"\nДодавання заявки для {target_vehicle['brand']} {target_vehicle['model']} ({target_vehicle['reg_number']})")
            work_type = input("Тип робіт: ")
            parts = input("Запчастини (розділяйте комою): ")
            resources = input("Ресурси (розділяйте комою): ")

            try:
                cost = float(input("Орієнтовна вартість: "))
                success, message = system.add_repair_order(target_vehicle['id'], work_type, parts, resources, cost)
                print(message)
            except ValueError:
                print("Помилка: вартість має бути числом.")

        elif choice == "5":
            print("\n=== Позначення заявки як оплаченої ===")
            orders = system.get_repair_orders()

            if not orders:
                print("Немає заявок на ремонт.")
                input("Натисніть Enter для продовження...")
                continue

            unpaid_orders = [o for o in orders if o['status'] == 'Не оплачено']

            if not unpaid_orders:
                print("Немає неоплачених заявок.")
                input("Натисніть Enter для продовження...")
                continue

            print(tabulate([[o['id'][:8], f"{o['brand']} {o['model']}", o['reg_number'], o['work_type'],
                             o['estimated_cost'], o['status']]
                            for o in unpaid_orders],
                           headers=["ID", "Транспорт", "Реєстр. номер", "Тип робіт", "Вартість", "Статус"]))

            order_id_input = input("\nВведіть перші 8 символів ID заявки для позначення як оплаченої: ").strip()
            matching_orders = [o for o in unpaid_orders if o['id'].startswith(order_id_input)]

            if not matching_orders:
                print("Заявку не знайдено або вона вже оплачена.")
                input("Натисніть Enter для продовження...")
                continue

            target_order = matching_orders[0]
            success, message = system.mark_order_paid(target_order['id'])
            print(message)

        elif choice == "6":
            print("\n=== Генерація рахунку ===")
            orders = system.get_repair_orders()
            if not orders:
                print("Немає заявок на ремонт.")
                input("Натисніть Enter для продовження...")
                continue

            print(tabulate([[o['id'][:8], f"{o['brand']} {o['model']}", o['reg_number'], o['work_type'],
                             o['estimated_cost'], o['status']]
                            for o in orders],
                           headers=["ID", "Транспорт", "Реєстр. номер", "Тип робіт", "Вартість", "Статус"]))

            order_id = input("\nВведіть ID заявки для генерації рахунку: ")
            target_order = next((o for o in orders if o['id'].startswith(order_id)), None)

            if not target_order:
                print("Заявку не знайдено.")
                input("Натисніть Enter для продовження...")
                continue

            success, invoice = system.generate_invoice(target_order['id'])
            if success:
                print(invoice)

                filename = f"invoice_{target_order['id'][:8]}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(invoice)
                print(f"Рахунок збережено у файл {filename}")
            else:
                print(invoice)

        elif choice == "7":
            print("\n=== Перегляд транспортних засобів ===")

            # Спочатку отримуємо всі транспортні засоби
            vehicles = system.get_vehicles()

            if not vehicles:
                print("Немає зареєстрованих транспортних засобів.")
                input("Натисніть Enter для продовження...")
                continue

            # Додаємо підменю для вибору дій
            while True:
                print("\n--- МЕНЮ ПЕРЕГЛЯДУ ТРАНСПОРТНИХ ЗАСОБІВ ---")
                print("1. Переглянути всі транспортні засоби")
                print("2. Фільтрувати транспортні засоби")
                print("3. Сортувати транспортні засоби")
                print("4. Повернутися до головного меню")

                view_choice = input("Виберіть опцію (1-4): ")

                if view_choice == "1":
                    # Показуємо всі транспортні засоби без фільтрів і сортування
                    print("\n--- СПИСОК ВСІХ ТРАНСПОРТНИХ ЗАСОБІВ ---")
                    print(tabulate([[v['id'][:8], v['brand'], v['model'], v['year'], v['reg_number'],
                                     v['owner'], v['orders_count'], v['unpaid_orders'], f"{v['total_cost']:.2f} грн"]
                                    for v in vehicles],
                                   headers=["ID", "Марка", "Модель", "Рік", "Реєстр. номер",
                                            "Власник", "Заявок", "Неоплачено", "Загальна вартість"]))

                elif view_choice == "2":
                    # Фільтрація
                    print("\n--- ФІЛЬТРАЦІЯ ТРАНСПОРТНИХ ЗАСОБІВ ---")
                    print("Залиште поля порожніми, якщо не бажаєте застосовувати фільтр")
                    filter_brand = input("Фільтр за маркою: ") or None
                    filter_model = input("Фільтр за моделлю: ") or None

                    payment_options = "\n1 - Показати тільки оплачені\n2 - Показати тільки неоплачені\n0 - Показати всі"
                    filter_payment_choice = input(f"Фільтр за статусом оплати {payment_options}: ")
                    filter_payment = None
                    if filter_payment_choice == "1":
                        filter_payment = "Оплачено"
                    elif filter_payment_choice == "2":
                        filter_payment = "Не оплачено"

                    filtered_vehicles = system.get_vehicles(filter_brand, filter_model, filter_payment)

                    if not filtered_vehicles:
                        print("Немає транспортних засобів, що відповідають критеріям фільтрації.")
                    else:
                        print("\n--- РЕЗУЛЬТАТИ ФІЛЬТРАЦІЇ ---")
                        print(tabulate([[v['id'][:8], v['brand'], v['model'], v['year'], v['reg_number'],
                                         v['owner'], v['orders_count'], v['unpaid_orders'],
                                         f"{v['total_cost']:.2f} грн"]
                                        for v in filtered_vehicles],
                                       headers=["ID", "Марка", "Модель", "Рік", "Реєстр. номер",
                                                "Власник", "Заявок", "Неоплачено", "Загальна вартість"]))

                elif view_choice == "3":
                    # Сортування
                    print("\n--- СОРТУВАННЯ ТРАНСПОРТНИХ ЗАСОБІВ ---")
                    sort_options = "\n1 - За роком випуску (новіші спочатку)\n2 - За власником (за алфавітом)"
                    sort_options += "\n3 - За вартістю робіт (більші спочатку)\n4 - За кількістю заявок (більше спочатку)"
                    sort_options += "\n5 - За неоплаченими заявками (більше спочатку)\n0 - Без сортування"

                    sort_choice = input(f"Виберіть тип сортування {sort_options}: ")
                    sorted_vehicles = vehicles.copy()

                    if sort_choice == "1":
                        sorted_vehicles.sort(key=lambda v: v["year"], reverse=True)
                        print("Застосовано сортування за роком випуску (новіші спочатку)")
                    elif sort_choice == "2":
                        sorted_vehicles.sort(key=lambda v: v["owner"].lower())
                        print("Застосовано сортування за власником (за алфавітом)")
                    elif sort_choice == "3":
                        sorted_vehicles.sort(key=lambda v: v["total_cost"], reverse=True)
                        print("Застосовано сортування за вартістю робіт (більші спочатку)")
                    elif sort_choice == "4":
                        sorted_vehicles.sort(key=lambda v: v["orders_count"], reverse=True)
                        print("Застосовано сортування за кількістю заявок (більше спочатку)")
                    elif sort_choice == "5":
                        sorted_vehicles.sort(key=lambda v: v["unpaid_orders"], reverse=True)
                        print("Застосовано сортування за неоплаченими заявками (більше спочатку)")
                    else:
                        print("Сортування не застосовано")

                    print("\n--- РЕЗУЛЬТАТИ СОРТУВАННЯ ---")
                    print(tabulate([[v['id'][:8], v['brand'], v['model'], v['year'], v['reg_number'],
                                     v['owner'], v['orders_count'], v['unpaid_orders'], f"{v['total_cost']:.2f} грн"]
                                    for v in sorted_vehicles],
                                   headers=["ID", "Марка", "Модель", "Рік", "Реєстр. номер",
                                            "Власник", "Заявок", "Неоплачено", "Загальна вартість"]))

                elif view_choice == "4":
                    # Повертаємося до головного меню
                    break

                else:
                    print("Невірний вибір. Спробуйте ще раз.")

                input("\nНатисніть Enter для продовження...")

        elif choice == "8":
            print("\n=== Перегляд заявок на ремонт ===")

            filter_vehicle = input("Фільтр за ID транспортного засобу (залиште порожнім для всіх): ") or None
            if filter_vehicle:
                vehicles = system.get_vehicles()
                target_vehicle = next((v for v in vehicles if v['id'].startswith(filter_vehicle)), None)
                if target_vehicle:
                    filter_vehicle = target_vehicle['id']
                else:
                    print("Транспортний засіб не знайдено.")
                    input("Натисніть Enter для продовження...")
                    continue

            orders = system.get_repair_orders(filter_vehicle)

            if not orders:
                print("Немає заявок на ремонт, що відповідають критеріям.")
            else:
                print(tabulate([[o['id'][:8], f"{o['brand']} {o['model']}", o['reg_number'], o['date_created'],
                                 o['work_type'], o['estimated_cost'], o['status']]
                                for o in orders],
                               headers=["ID", "Транспорт", "Реєстр. номер", "Дата", "Тип робіт", "Вартість", "Статус"]))

        elif choice == "9":
            print("Дякуємо за використання Системи управління СТО.")
            break

        else:
            print("Невірний вибір. Спробуйте ще раз.")

        input("\nНатисніть Enter для продовження...")


if __name__ == "__main__":
    main()