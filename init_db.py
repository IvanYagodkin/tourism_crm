 # init_db.py
# Скрипт для создания базы данных турагентства
# Запускать один раз — при первом запуске системы

import sqlite3
import os

# Создаём папку data, если её нет
if not os.path.exists('data'):
    os.makedirs('data')

# Подключаемся к базе (файл создастся в data/tourism.db)
conn = sqlite3.connect('data/tourism.db')
cursor = conn.cursor()

print("✅ Подключено к базе: data/tourism.db")
# Таблица: countries — страны назначения
# Назначение: хранит список стран, куда продаём туры
cursor.execute('''
    CREATE TABLE IF NOT EXISTS countries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,           -- название страны: "Турция", "Египет"
        code TEXT,                           -- код страны: "TR", "EG"
        region TEXT,                         -- регион: "Азия", "Африка"
        visa_required INTEGER DEFAULT 0,     -- нужна ли виза: 1 = да, 0 = нет
        is_active INTEGER DEFAULT 1,         -- 1 = активна, 0 = скрыта
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
print("✅ Таблица 'countries' создана")

# Добавим примеры стран
countries = [
    ('Турция', 'TR', 'Азия', 0),
    ('Египет', 'EG', 'Африка', 0),
    ('Греция', 'GR', 'Европа', 0),
    ('Таиланд', 'TH', 'Азия', 1),
    ('Испания', 'ES', 'Европа', 0),
    ('ОАЭ', 'AE', 'Азия', 0)
]
cursor.executemany('''
    INSERT OR IGNORE INTO countries (name, code, region, visa_required) 
    VALUES (?, ?, ?, ?)
''', countries)
print("✅ Примеры стран добавлены")
# Таблица: clients — клиенты турагентства
# Назначение: хранит данные клиентов. Используется при оформлении заказов.
# Важно: не удалять физически — только помечать is_active = 0
cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,           -- имя
        last_name TEXT NOT NULL,            -- фамилия
        middle_name TEXT,                   -- отчество (может быть пустым)
        phone TEXT UNIQUE,                  -- телефон, уникальный
        email TEXT,                         -- email (необязательный)
        notes TEXT,       
        birth_year INTEGER,                 -- год рождения (для подбора туров)
        is_active INTEGER DEFAULT 1,        -- 1 = активен, 0 = скрыт
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
print("✅ Таблица 'clients' создана")
# Таблица: documents — документы клиентов
# Назначение: хранит паспорта, заграны, виды на жительство
# Важно: scan_path — путь к файлу (например, "scans/passport_5.pdf")
cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,         -- к какому клиенту относится
        doc_type TEXT NOT NULL,             -- тип: "паспорт", "загран", "свидетельство", "ВНЖ"
        doc_number TEXT NOT NULL,           -- номер документа
        issue_date DATE,                    -- дата выдачи
        expiry_date DATE,                   -- срок действия
        issued_by TEXT,                     -- кем выдан
        scan_path TEXT,                     -- путь к скану (опционально)
        is_active INTEGER DEFAULT 1,        -- 1 = действует, 0 = аннулирован
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
    )
''')
print("✅ Таблица 'documents' создана")
# Таблица: hotels — отели
# Назначение: хранит информацию об отелях. Используется при подборе туров
cursor.execute('''
    CREATE TABLE IF NOT EXISTS hotels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,                 -- название отеля
        country_id INTEGER NOT NULL,        -- привязка к стране
        address TEXT,                       -- адрес: город, улица
        stars INTEGER,                      -- количество звёзд: 2, 3, 4, 5
        has_pool INTEGER DEFAULT 0,         -- бассейн: 1 = да, 0 = нет
        has_wifi INTEGER DEFAULT 1,         -- Wi-Fi: 1 = да
        has_breakfast INTEGER DEFAULT 1,    -- завтрак включён
        description TEXT,                   -- описание
        is_active INTEGER DEFAULT 1,        -- 1 = работает, 0 = закрыт
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (country_id) REFERENCES countries (id)
    )
''')
print("✅ Таблица 'hotels' создана")

# Добавим примеры отелей
hotels = [
    ('Sunrise Resort', 1, 'Кемер, Турция', 5, 1, 1, 1, 'Пляжный отель с спа'),
    ('Nile View Hotel', 2, 'Хургада, Египет', 4, 1, 1, 1, 'Рядом с набережной'),
    ('Aegean Sea Hotel', 3, 'Родос, Греция', 4, 1, 1, 1, 'Вид на море'),
    ('Bangkok Palace', 4, 'Бангкок, Таиланд', 5, 1, 1, 1, 'Центр города, бассейн на крыше')
]
cursor.executemany('''
    INSERT OR IGNORE INTO hotels (name, country_id, address, stars, has_pool, has_wifi, has_breakfast, description) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', hotels)
print("✅ Примеры отелей добавлены")
# Таблица: room_types — типы номеров в отелях
# Назначение: стандарт, люкс, семейный и т.д.
cursor.execute('''
    CREATE TABLE IF NOT EXISTS room_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hotel_id INTEGER NOT NULL,          -- к какому отелю относится
        name TEXT NOT NULL,                 -- "Стандарт", "Люкс", "Семейный"
        max_guests INTEGER DEFAULT 2,       -- сколько человек помещается
        price_per_night REAL NOT NULL,      -- цена за ночь
        has_balcony INTEGER DEFAULT 0,      -- балкон: 1 = да
        has_kitchen INTEGER DEFAULT 0,      -- кухня: 1 = да
        is_active INTEGER DEFAULT 1,        -- 1 = доступен, 0 = снят с продажи
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (hotel_id) REFERENCES hotels (id)
    )
''')
print("✅ Таблица 'room_types' создана")

# Добавим примеры номеров
room_types = [
    (1, 'Стандарт', 2, 5000, 1, 0),
    (1, 'Люкс', 3, 12000, 1, 1),
    (2, 'Стандарт', 2, 4500, 1, 0),
    (2, 'Семейный', 4, 8000, 1, 0),
    (3, 'Стандарт', 2, 6000, 1, 0),
    (4, 'Люкс', 3, 15000, 1, 1)
]
cursor.executemany('''
    INSERT OR IGNORE INTO room_types (hotel_id, name, max_guests, price_per_night, has_balcony, has_kitchen) 
    VALUES (?, ?, ?, ?, ?, ?)
''', room_types)
print("✅ Примеры типов номеров добавлены")
# Таблица: tour_packages — готовые пакеты туров
# Назначение: стандартные предложения (например, "Горящий тур в Турцию 7 дней")
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tour_packages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,                 -- название пакета: "Лето в Турции"
        country_id INTEGER NOT NULL,        -- направление
        hotel_id INTEGER NOT NULL,          -- отель
        room_type_id INTEGER NOT NULL,      -- тип номера
        departure_date DATE NOT NULL,       -- дата вылета
        return_date DATE NOT NULL,          -- дата возврата
        nights INTEGER NOT NULL,            -- количество ночей
        base_price REAL NOT NULL,           -- базовая цена за человека
        max_slots INTEGER DEFAULT 20,       -- сколько человек можно продать
        sold_slots INTEGER DEFAULT 0,       -- сколько уже продано
        is_active INTEGER DEFAULT 1,        -- 1 = в продаже, 0 = снят
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (country_id) REFERENCES countries (id),
        FOREIGN KEY (hotel_id) REFERENCES hotels (id),
        FOREIGN KEY (room_type_id) REFERENCES room_types (id)
    )
''')
print("✅ Таблица 'tour_packages' создана")

# Добавим примеры пакетов
from datetime import datetime, timedelta
today = datetime.now().date()
in_7_days = today + timedelta(days=7)
in_14_days = today + timedelta(days=14)

tour_packages = [
    ('Горящий тур в Турцию', 1, 1, 1, in_7_days, in_7_days + timedelta(days=7), 7, 45000, 20, 0),
    ('Неделя в Египте', 2, 2, 2, in_14_days, in_14_days + timedelta(days=7), 7, 52000, 15, 0),
    ('Лето в Греции', 3, 3, 5, in_14_days, in_14_days + timedelta(days=10), 10, 75000, 10, 0)
]
cursor.executemany('''
    INSERT OR IGNORE INTO tour_packages 
    (name, country_id, hotel_id, room_type_id, departure_date, return_date, nights, base_price, max_slots, sold_slots) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', tour_packages)
print("✅ Примеры пакетов туров добавлены")
# Таблица: services — дополнительные услуги
# Назначение: трансфер, страховка, экскурсии
cursor.execute('''
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,                 -- "Трансфер", "Страховка", "Экскурсия"
        default_price REAL NOT NULL,        -- стандартная цена
        is_active INTEGER DEFAULT 1,        -- 1 = доступна, 0 = скрыта
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
print("✅ Таблица 'services' создана")

# Добавим примеры услуг
services = [
    ('Трансфер', 2000),
    ('Медицинская страховка', 3500),
    ('Городская экскурсия', 4000),
    ('VIP-обслуживание в аэропорту', 8000)
]
cursor.executemany('INSERT OR IGNORE INTO services (name, default_price) VALUES (?, ?)', services)
print("✅ Примеры услуг добавлены")
# Таблица: bookings — заказы клиентов
# Назначение: фиксирует, кто что купил, сколько стоит, оплата, статус
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,         -- кто купил
        agent_id INTEGER NOT NULL,          -- кто оформил
        tour_package_id INTEGER,            -- если из пакета
        hotel_id INTEGER,                   -- если индивидуальный
        room_type_id INTEGER,               -- тип номера
        departure_date DATE NOT NULL,       -- вылет
        return_date DATE NOT NULL,          -- возврат
        nights INTEGER NOT NULL,            -- ночей
        total_cost REAL NOT NULL,           -- общая стоимость
        paid_amount REAL DEFAULT 0,         -- сколько внесено
        payment_status TEXT DEFAULT 'не оплачено', -- 'не оплачено', 'частично', 'полностью'
        status TEXT DEFAULT 'новый',        -- 'новый', 'подтверждён', 'отменён', 'завершён'
        local_id INTEGER,                   -- ID в локальной базе (для синхронизации)
        sync_status TEXT DEFAULT 'не синхронизировано', -- 'не синхронизировано', 'синхронизировано'
        synced_at DATETIME,                 -- когда синхронизировано
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (client_id) REFERENCES clients (id),
        FOREIGN KEY (agent_id) REFERENCES agents (id),
        FOREIGN KEY (tour_package_id) REFERENCES tour_packages (id),
        FOREIGN KEY (hotel_id) REFERENCES hotels (id),
        FOREIGN KEY (room_type_id) REFERENCES room_types (id)
    )
''')
print("✅ Таблица 'bookings' создана")
# Таблица: booking_services — дополнительные услуги в заказе
# Назначение: связывает заказ и услуги (многие-ко-многим с количеством)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS booking_services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL,        -- к какому заказу
        service_id INTEGER NOT NULL,        -- какая услуга
        quantity INTEGER DEFAULT 1,         -- количество (например, 2 страховки)
        price_at_time REAL NOT NULL,        -- цена на момент продажи
        total_price REAL NOT NULL,          -- quantity * price_at_time
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (booking_id) REFERENCES bookings (id) ON DELETE CASCADE,
        FOREIGN KEY (service_id) REFERENCES services (id)
    )
''')
# Сохраняем изменения в базу данных
conn.commit()

# Закрываем соединение с базой данных
conn.close()

print("🎉 База данных успешно создана и закрыта.")

