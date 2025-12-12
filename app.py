# app.py
# Основное приложение турагентства
# Запуск: python app.py

import sqlite3
import os
from datetime import datetime

# Путь к базе
DB_PATH = 'data/tourism.db'

def get_connection():
    return sqlite3.connect(DB_PATH)


# ================== ОСНОВНОЕ МЕНЮ ==================


def main_menu():
    while True:
        print("\n" + "="*50)
        print("  🌍 ТУРАГЕНТСТВО — ОСНОВНОЕ МЕНЮ")
        print("="*50)
        print("1. Клиенты")
        print("2. Отели и номера")
        print("3. Готовые туры")
        print("4. Оформить заказ")
        print("5. Оплаты")
        print("6. Отчёты")
        print("0. Выход")
        
        choice = input("\n👉 Выберите раздел: ").strip()
        
        if choice == "1":
            clients_menu()
        elif choice == "2":
            hotels_menu()
        elif choice == "3":
            tour_packages_menu()
        elif choice == "4":
            bookings_menu()
        elif choice == "5":
            payments_menu()
        elif choice == "6":
            reports_menu()
        elif choice == "0":
            print("👋 До свидания Хорошего дня!")
            break
        else:
            print("❌ Неверный выбор. Попробуйте снова.")
# ================== МЕНЮ КЛИЕНТОВ ==================
def clients_menu():
    while True:
        print("\n" + "-"*40)
        print("  👥 УПРАВЛЕНИЕ КЛИЕНТАМИ")
        print("-"*40)
        print("1. Показать всех клиентов")
        print("2. Добавить клиента")
        print("3. Редактировать клиента")
        print("4. Удалить клиента")
        print("5. Показать документы клиента")
        print("6. Добавить документ клиенту")
        print("0. Назад")
        
        choice = input("\n👉 Выберите действие: ").strip()
        
        if choice == "1":
            show_clients()
        elif choice == "2":
            add_client()
        elif choice == "3":
            edit_client()
        elif choice == "4":
            deactivate_client()
        elif choice == "5":
            show_client_documents()  # ← Вызов функции
        elif choice == "6":
            add_document()  # ← Вызов функции
        elif choice == "0":
            break
        else:
            print("❌ Неверный выбор.")
def add_client():
    print("\n➕ ДОБАВЛЕНИЕ НОВОГО КЛИЕНТА")
    first_name = input("Имя: ").strip()
    last_name = input("Фамилия: ").strip()
    middle_name = input("Отчество (можно пусто): ").strip() or None
    phone = input("Телефон: ").strip()
    email = input("Email (можно пусто): ").strip() or None
    birth_year = input("Год рождения (можно пусто): ").strip()
    birth_year = int(birth_year) if birth_year.isdigit() else None

    if not first_name or not last_name or not phone:
        print("❌ Имя, фамилия и телефон обязательны.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO clients (first_name, last_name, middle_name, phone, email, birth_year)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, middle_name, phone, email, birth_year))
        conn.commit()
        print(f"✅ Клиент {first_name} {last_name} добавлен с ID: {cursor.lastrowid}")
    except sqlite3.IntegrityError:
        print("❌ Клиент с таким телефоном уже существует.")
    finally:
        conn.close()
def edit_client():
    try:
        client_id = int(input("\nВведите ID клиента для редактирования: "))
    except ValueError:
        print("❌ Неверный формат ID.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT first_name, last_name, middle_name, phone, email, birth_year, notes
        FROM clients WHERE id = ? AND is_active = 1
    ''', (client_id,))
    client = cursor.fetchone()
    if not client:
        print("❌ Клиент не найден.")
        conn.close()
        return

    print(f"\nРедактирование клиента: {client[0]} {client[1]}")
    print("Оставьте поле пустым, чтобы не менять.")

    first_name = input(f"Имя ({client[0]}): ").strip() or client[0]
    last_name = input(f"Фамилия ({client[1]}): ").strip() or client[1]
    middle_name = input(f"Отчество ({client[2]}): ").strip() or client[2]
    phone = input(f"Телефон ({client[3]}): ").strip() or client[3]
    email = input(f"Email ({client[4]}): ").strip() or client[4]
    email = email or None
    birth_year = input(f"Год рождения ({client[5]}): ").strip() or str(client[5])
    try:
        birth_year = int(birth_year)
    except ValueError:
        print("❌ Неверный год, оставлен прежним.")
        birth_year = client[5]
    notes = input(f"Заметки ({client[6]}): ").strip() or client[6]

    cursor.execute('''
        UPDATE clients SET
            first_name = ?, last_name = ?, middle_name = ?,
            phone = ?, email = ?, birth_year = ?, notes = ?
        WHERE id = ?
    ''', (first_name, last_name, middle_name, phone, email, birth_year, notes, client_id))
    conn.commit()
    print(f"✅ Клиент {first_name} {last_name} обновлён.")
    conn.close()

def show_clients():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, first_name, last_name, phone, email 
        FROM clients 
        WHERE is_active = 1 
        ORDER BY last_name, first_name
    ''')
    clients = cursor.fetchall()
    conn.close()

    if not clients:
        print("📭 Нет активных клиентов.")
        return

    print("\n📋 СПИСОК КЛИЕНТОВ:")
    for c in clients:
        email = c[4] if c[4] else "—"
        print(f"  ID: {c[0]} | {c[1]} {c[2]} | Тел: {c[3]} | Email: {email}")
def find_client_by_phone():
    phone = input("\n📞 Введите телефон клиента: ").strip()
    if not phone:
        print("❌ Телефон не может быть пустым.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, first_name, last_name, phone, email, birth_year
        FROM clients
        WHERE phone = ? AND is_active = 1
    ''', (phone,))
    client = cursor.fetchone()
    conn.close()

    if client:
        print(f"\n🔍 Найден клиент:")
        print(f"  ID: {client[0]}")
        print(f"  ФИО: {client[1]} {client[2]} {client[3]}")
        print(f"  Телефон: {client[3]}")
        print(f"  Email: {client[4]}")
        print(f"  Год рождения: {client[5]}")
    else:
        print("❌ Клиент не найден или удалён.")

def deactivate_client():
    try:
        client_id = int(input("\n❌ Введите ID клиента для скрытия: "))
    except ValueError:
        print("❌ Неверный формат ID.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT first_name, last_name FROM clients WHERE id = ? AND is_active = 1', (client_id,))
    client = cursor.fetchone()

    if not client:
        print("❌ Клиент не найден или уже скрыт.")
        conn.close()
        return

    confirm = input(f"Подтвердите скрытие {client[0]} {client[1]}? (да/нет): ").strip().lower()
    if confirm != 'да':
        print("Операция отменена.")
        conn.close()
        return

    cursor.execute('UPDATE clients SET is_active = 0 WHERE id = ?', (client_id,))
    conn.commit()
    print(f"✅ Клиент {client[0]} {client[1]} скрыт.")
    conn.close()

# ================== УПРАВЛЕНИЕ ДОКУМЕНТАМИ ==================
def documents_menu():
    while True:
        print("\n" + "-"*40)
        print("  📄 ДОКУМЕНТЫ КЛИЕНТОВ")
        print("-"*40)
        print("1. Добавить документ")
        print("2. Показать документы клиента")
        print("0. Назад")
        
        choice = input("\n👉 Выберите действие: ").strip()
        
        if choice == "1":
            add_document()
        elif choice == "2":
            show_client_documents()
        elif choice == "0":
            break
        else:
            print("❌ Неверный выбор.")

def add_document():
    try:
        client_id = int(input("\nВведите ID клиента: "))
    except ValueError:
        print("❌ Неверный формат ID.")
        return

    # Проверим, существует ли клиент
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, last_name FROM clients WHERE id = ? AND is_active = 1", (client_id,))
    client = cursor.fetchone()
    if not client:
        print("❌ Клиент не найден.")
        conn.close()
        return
    conn.close()

    print(f"Добавление документа для {client[0]} {client[1]}")

    doc_type = input("Тип документа (паспорт, виза, загранпаспорт и т.д.): ").strip()
    doc_number = input("Номер документа: ").strip()
    issue_date = input("Дата выдачи (ГГГГ-ММ-ДД): ").strip()
    expiry_date = input("Срок действия (ГГГГ-ММ-ДД, если есть): ").strip() or None
    issued_by = input("Кем выдан (для паспорта): ").strip() or None

    if not doc_type or not doc_number or not issue_date:
        print("❌ Тип, номер и дата выдачи обязательны.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO documents 
            (client_id, doc_type, doc_number, issue_date, expiry_date, issued_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (client_id, doc_type, doc_number, issue_date, expiry_date, issued_by))
        conn.commit()
        print(f"✅ Документ '{doc_type}' добавлен для {client[0]} {client[1]}")
    except sqlite3.IntegrityError as e:
        print(f"❌ Ошибка при добавлении: {e}")
    finally:
        conn.close()

def show_client_documents():
    try:
        client_id = int(input("\nВведите ID клиента: "))
    except ValueError:
        print("❌ Неверный формат ID.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, last_name FROM clients WHERE id = ? AND is_active = 1", (client_id,))
    client = cursor.fetchone()
    if not client:
        print("❌ Клиент не найден.")
        conn.close()
        return

    cursor.execute('''
        SELECT doc_type, doc_number, issue_date, expiry_date, issued_by
        FROM documents
        WHERE client_id = ? AND is_active = 1
        ORDER BY issue_date DESC
    ''', (client_id,))
    docs = cursor.fetchall()
    conn.close()

    if not docs:
        print(f"\n📄 У клиента {client[0]} {client[1]} нет документов.")
        return

    print(f"\n📋 ДОКУМЕНТЫ: {client[0]} {client[1]}")
    for doc in docs:
        expiry = doc[3] if doc[3] else "не ограничен"
        issued = f" | Кем выдан: {doc[4]}" if doc[4] else ""
        print(f"  • {doc[0]} №{doc[1]} | Выдан: {doc[2]} | Действует до: {expiry}{issued}")

# ================== МЕНЮ ОТЕЛЕЙ ==================
def hotels_menu():
    while True:
        print("\n" + "-"*40)
        print("  🏨 ОТЕЛИ И НОМЕРА")
        print("-"*40)
        print("1. Показать отели")
        print("2. Показать номера в отеле")
        print("0. Назад")
        
        choice = input("\n👉 Выберите действие: ").strip()
        
        if choice == "1":
            show_hotels()
        elif choice == "2":
            show_rooms_by_hotel()
        elif choice == "0":
            break
        else:
            print("❌ Неверный выбор.")

def show_hotels():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT h.id, h.name, c.name, h.stars, h.address
        FROM hotels h
        JOIN countries c ON h.country_id = c.id
        WHERE h.is_active = 1
        ORDER BY c.name, h.stars DESC
    ''')
    hotels = cursor.fetchall()
    conn.close()

    if not hotels:
        print("📭 Нет активных отелей.")
        return

    print("\n🏨 СПИСОК ОТЕЛЕЙ:")
    for h in hotels:
        print(f"  ID: {h[0]} | {h[1]} ({h[3]}★) | {h[2]} | Адрес: {h[4]}")

def show_rooms_by_hotel():
    try:
        hotel_id = int(input("\n🏨 Введите ID отеля: "))
    except ValueError:
        print("❌ Неверный формат ID.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT rt.id, rt.name, rt.max_guests, rt.price_per_night, rt.has_balcony, rt.has_kitchen
        FROM room_types rt
        WHERE rt.hotel_id = ? AND rt.is_active = 1
    ''', (hotel_id,))
    rooms = cursor.fetchall()
    conn.close()

    if not rooms:
        print("❌ В этом отеле нет активных номеров.")
        return

    print(f"\n🛏️ НОМЕРА в отеле (ID {hotel_id}):")
    for r in rooms:
        balcony = "есть" if r[4] else "нет"
        kitchen = "есть" if r[5] else "нет"
        print(f"  ID: {r[0]} | {r[1]} | До {r[2]} чел. | {r[3]} ₽/ночь | Балкон: {balcony} | Кухня: {kitchen}")
# ================== МЕНЮ ГОТОВЫХ ТУРОВ ==================
def tour_packages_menu():
    while True:
        print("\n" + "-"*40)
        print("  ✈️ ГОТОВЫЕ ТУРЫ")
        print("-"*40)
        print("1. Показать все пакеты")
        print("2. Показать свободные места")
        print("0. Назад")
        
        choice = input("\n👉 Выберите действие: ").strip()
        
        if choice == "1":
            show_tour_packages()
        elif choice == "2":
            show_available_slots()
        elif choice == "0":
            break
        else:
            print("❌ Неверный выбор.")

def show_tour_packages():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            tp.id,
            tp.name,
            c.name,
            h.name,
            tp.departure_date,
            tp.return_date,
            tp.nights,
            tp.base_price,
            tp.sold_slots,
            tp.max_slots
        FROM tour_packages tp
        JOIN countries c ON tp.country_id = c.id
        JOIN hotels h ON tp.hotel_id = h.id
        WHERE tp.is_active = 1
        ORDER BY tp.departure_date
    ''')
    packages = cursor.fetchall()
    conn.close()

    if not packages:
        print("📭 Нет активных пакетов туров.")
        return

    print("\n✈️ ДОСТУПНЫЕ ТУРЫ:")
    for p in packages:
        available = p[9] - p[8]  # max - sold
        print(f"  ID: {p[0]} | {p[1]} | {p[2]} → {p[3]}")
        print(f"    📅 {p[4]} – {p[5]} ({p[6]} ночей) | Цена: {p[7]} ₽ | Свободно: {available} из {p[9]}")
def show_available_slots():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT tp.id, tp.name, (tp.max_slots - tp.sold_slots) as available
        FROM tour_packages tp
        WHERE tp.is_active = 1 AND (tp.max_slots - tp.sold_slots) > 0
        ORDER BY available
    ''')
    slots = cursor.fetchall()
    conn.close()

    if not slots:
        print("❌ Нет свободных мест в пакетах.")
        return

    print("\n📊 СВОБОДНЫЕ МЕСТА:")
    for s in slots:
        print(f"  ТУР ID {s[0]}: {s[1]} → доступно {s[2]} мест")
# ================== МЕНЮ ЗАКАЗОВ ==================
def bookings_menu():
    while True:
        print("\n" + "-"*40)
        print("  📝 ОФОРМЛЕНИЕ ЗАКАЗА")
        print("-"*40)
        print("1. Оформить новый заказ")
        print("2. Показать все заказы")
        print("0. Назад")
        
        choice = input("\n👉 Выберите действие: ").strip()
        
        if choice == "1":
            create_booking()
        elif choice == "2":
            show_bookings()
        elif choice == "0":
            break
        else:
            print("❌ Неверный выбор.")
def create_booking():
    print("\n🆕 ОФОРМЛЕНИЕ НОВОГО ЗАКАЗА")

    # Выбор клиента
    phone = input("Введите телефон клиента: ").strip()
    client = find_client_by_phone_for_booking(phone)
    if not client:
        print("❌ Клиент не найден.")
        return

    # Выбор агента
    agent_code = input("Введите код агента (например, AGT-001): ").strip()
    agent = get_agent_by_code(agent_code)
    if not agent:
        print("❌ Агент не найден.")
        return

    # Выбор тура
    show_tour_packages()
    try:
        package_id = int(input("Введите ID тура (или 0 для индивидуального): "))
    except ValueError:
        print("❌ Неверный ввод.")
        return

    if package_id == 0:
        # Индивидуальный тур
        hotel_id = int(input("ID отеля: "))
        room_type_id = int(input("ID номера: "))
        departure_date = input("Дата вылета (ГГГГ-ММ-ДД): ")
        return_date = input("Дата возврата: ")
        nights = (datetime.strptime(return_date, "%Y-%m-%d") - datetime.strptime(departure_date, "%Y-%m-%d")).days
        total_cost = float(input("Общая стоимость: "))
    else:
        # Из пакета
        package = get_tour_package(package_id)
        if not package:
            print("❌ Пакет не найден.")
            return
        hotel_id = package[2]
        room_type_id = package[3]
        departure_date = package[4]
        return_date = package[5]
        nights = package[6]
        total_cost = package[7] * 2  # Пример: двое взрослых

    # Создание заказа
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bookings (
            client_id, agent_id, tour_package_id, hotel_id, room_type_id,
            departure_date, return_date, nights, total_cost, paid_amount, payment_status, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 'не оплачено', 'новый')
    ''', (client[0], agent[0], package_id or None, hotel_id, room_type_id, departure_date, return_date, nights, total_cost))
    booking_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print(f"✅ Заказ №{booking_id} оформлен для {client[1]} {client[2]}")
def find_client_by_phone_for_booking(phone):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, first_name, last_name FROM clients WHERE phone = ? AND is_active = 1', (phone,))
    client = cursor.fetchone()
    conn.close()
    return client

def get_agent_by_code(code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM agents WHERE agent_code = ? AND is_active = 1', (code,))
    agent = cursor.fetchone()
    conn.close()
    return agent

def get_tour_package(package_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, hotel_id, room_type_id, departure_date, return_date, nights, base_price
        FROM tour_packages WHERE id = ? AND is_active = 1
    ''', (package_id,))
    package = cursor.fetchone()
    conn.close()
    return package

def show_bookings():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            b.id,
            c.first_name,
            c.last_name,
            h.name,
            b.departure_date,
            b.return_date,
            b.total_cost,
            b.paid_amount,
            b.payment_status,
            b.status
        FROM bookings b
        JOIN clients c ON b.client_id = c.id
        JOIN hotels h ON b.hotel_id = h.id
        ORDER BY b.created_at DESC
        LIMIT 10
    ''')
    bookings = cursor.fetchall()
    conn.close()

    if not bookings:
        print("📭 Нет заказов.")
        return

    print("\n📋 ПОСЛЕДНИЕ ЗАКАЗЫ (до 10):")
    for b in bookings:
        print(f"  №{b[0]} | {b[1]} {b[2]} | {b[3]}")
        print(f"    📅 {b[4]} – {b[5]} | {b[6]} ₽ | Оплачено: {b[7]} ₽ | {b[8]} | Статус: {b[9]}")

# ================== МЕНЮ ОПЛАТ ==================
def payments_menu():
    while True:
        print("\n" + "-"*40)
        print("  💳 УПРАВЛЕНИЕ ОПЛАТАМИ")
        print("-"*40)
        print("1. Внести оплату по заказу")
        print("2. Показать статус оплат")
        print("0. Назад")
        
        choice = input("\n👉 Выберите действие: ").strip()
        
        if choice == "1":
            make_payment()
        elif choice == "2":
            show_payment_status()
        elif choice == "0":
            break
        else:
            print("❌ Неверный выбор.")

def make_payment():
    try:
        booking_id = int(input("\nВведите ID заказа: "))
    except ValueError:
        print("❌ Неверный формат ID.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT total_cost, paid_amount, payment_status, client_id
        FROM bookings WHERE id = ?
    ''', (booking_id,))
    booking = cursor.fetchone()

    if not booking:
        print("❌ Заказ не найден.")
        conn.close()
        return

    total, paid, status, client_id = booking
    remaining = total - paid

    if remaining <= 0:
        print("✅ Оплата уже полностью внесена.")
        conn.close()
        return

    print(f"Общая стоимость: {total} ₽")
    print(f"Внесено: {paid} ₽")
    print(f"Осталось: {remaining} ₽")

    try:
        amount = float(input("Сумма к оплате: "))
    except ValueError:
        print("❌ Неверная сумма.")
        conn.close()
        return

    if amount <= 0 or amount > remaining:
        print(f"❌ Сумма должна быть от 1 до {remaining} ₽.")
        conn.close()
        return

    new_paid = paid + amount
    new_status = 'полностью' if new_paid >= total else 'частично'

    cursor.execute('''
        UPDATE bookings 
        SET paid_amount = ?, payment_status = ?
        WHERE id = ?
    ''', (new_paid, new_status, booking_id))
    conn.commit()

    # Лог оплаты (можно расширить)
    cursor.execute('''
        INSERT INTO payment_log (booking_id, amount, payment_date)
        VALUES (?, ?, ?)
    ''', (booking_id, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

    print(f"✅ Внесено {amount} ₽. Остаток: {total - new_paid} ₽.")
    conn.close()
def show_payment_status():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            b.id,
            c.first_name,
            c.last_name,
            b.total_cost,
            b.paid_amount,
            b.payment_status
        FROM bookings b
        JOIN clients c ON b.client_id = c.id
        WHERE b.status != 'отменён'
        ORDER BY b.created_at DESC
        LIMIT 10
    ''')
    payments = cursor.fetchall()
    conn.close()

    if not payments:
        print("📭 Нет заказов.")
        return

    print("\n📊 СТАТУС ОПЛАТ (последние 10):")
    for p in payments:
        remaining = p[3] - p[4]
        print(f"  Заказ {p[0]} | {p[1]} {p[2]} | {p[4]}/{p[3]} ₽ | {p[5]} | Осталось: {remaining} ₽")
# ================== МЕНЮ ОТЧЁТОВ ==================
def reports_menu():
    while True:
        print("\n" + "-"*40)
        print("  📊 ОТЧЁТЫ")
        print("-"*40)
        print("1. Продажи по агентам")
        print("2. Загруженность туров")
        print("0. Назад")
        
        choice = input("\n👉 Выберите отчёт: ").strip()
        
        if choice == "1":
            report_sales_by_agent()
        elif choice == "2":
            report_tour_load()
        elif choice == "0":
            break
        else:
            print("❌ Неверный выбор.")

def report_sales_by_agent():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            a.name,
            COUNT(b.id) as bookings_count,
            SUM(b.paid_amount) as total_paid
        FROM agents a
        LEFT JOIN bookings b ON a.id = b.agent_id
        WHERE a.is_active = 1
        GROUP BY a.id
        ORDER BY total_paid DESC
    ''')
    report = cursor.fetchall()
    conn.close()

    print("\n📈 ПРОДАЖИ ПО АГЕНТАМ:")
    for row in report:
        name, count, paid = row
        paid = paid or 0
        print(f"  {name} | Заказов: {count} | Собрано: {paid} ₽")

def report_tour_load():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            tp.name,
            tp.sold_slots,
            tp.max_slots,
            ROUND((tp.sold_slots * 100.0 / tp.max_slots), 1) as load_percent
        FROM tour_packages tp
        WHERE tp.is_active = 1 AND tp.max_slots > 0
        ORDER BY load_percent DESC
    ''')
    report = cursor.fetchall()
    conn.close()

    print("\n📊 ЗАГРУЖЕННОСТЬ ТУРОВ:")
    for row in report:
        name, sold, max_slots, percent = row
        print(f"  {name} | Продано: {sold}/{max_slots} | Загрузка: {percent}%")

if __name__ == "__main__":
    main_menu()
