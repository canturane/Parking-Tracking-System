# Parking Management System

This project aims to **automatically detect vehicle entry and exit** and **fully digitize parking management**. Vehicle and license plate recognition (YOLO + EasyOCR) is performed through camera footage, while users can manage reservations, payments, and balance operations through a Django-based web interface.

## Features

###  Vehicle Detection and License Plate Recognition
- Vehicle detection using YOLO
- License plate reading with EasyOCR
- Valid license plates stored in SQLite database

###  Reservation and Payment Management
- Create, edit, and delete reservations through web interface
- Parking fee calculation (time-based)
- User balance and payment processing

###  Database Integration (SQLite)
- Entry/exit information and billing records are stored
- User, reservation, and payment information centralized in one place

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd parking-management-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run Django migrations:
```bash
python manage.py migrate
```

4. Start the development server:
```bash
python manage.py runserver
```

## Usage

1. Navigate to the local server address (e.g., `http://127.0.0.1:8000/`) in your browser
2. Register or log in to your account
3. Manage your parking reservations
4. Track payment status with your license plate information

## Testing and Validation

- Test the project using **Pytest** or Django test commands:
```bash
python manage.py test
```

- Critical functionality including vehicle and license plate recognition, reservations, and payments are verified for proper operation

## Technology Stack

- **Backend**: Django (Python)
- **Computer Vision**: YOLO, EasyOCR
- **Database**: SQLite
- **Frontend**: Django Templates
- **Testing**: Pytest, Django Testing Framework

## Project Structure

```
parking-management-system/
├── manage.py
├── requirements.txt
├── parking_system/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── detection/
│   ├── models.py
│   ├── views.py
│   └── utils.py
├── reservations/
│   ├── models.py
│   ├── views.py
│   └── templates/
└── tests/
    ├── test_detection.py
    └── test_reservations.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request


