# 🏦 NOVA BANK — Digital Banking Web Application

NOVA BANK is a Django-based digital banking web application developed to demonstrate modern banking interface design and core banking-related web functionality.

The project includes a banking dashboard, user authentication, loan-related pages, and multilingual interface support.

## ✨ Features

- 🔐 User authentication
- 📊 Banking dashboard
- 💳 Banking interface and account overview
- 💰 Loan-related functionality
- 🌐 Multilingual interface: Uzbek, Russian, and English
- 🎨 Modern, responsive web interface
- 🛠️ Django application structure

*Feature availability depends on the current implementation of the project.*

## 🛠️ Technologies

- Python
- Django
- SQLite
- HTML5
- CSS3
- JavaScript
- Django Templates
- Git and GitHub

## 🌍 Languages

- Uzbek
- Russian
- English

## 📁 Project Structure

```text
NOVA-BANK/
├── config/
├── manage.py
├── templates/
├── static/
└── ...
```

*The structure above is illustrative. Folder names may differ in the actual repository.*

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/aziz-yuldoshev/nova-bank.git
cd nova-bank
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

**Windows CMD:**

```cmd
venv\Scripts\activate
```

### 4. Install dependencies

If the repository contains `requirements.txt`:

```bash
pip install -r requirements.txt
```

Otherwise, install the Django version required by the project:

```bash
pip install django
```

### 5. Configure environment variables

Configure the Django secret key and other required environment variables before starting the application. Never publish real secrets or passwords.

### 6. Apply database migrations

```bash
python manage.py migrate
```

### 7. Start the development server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## 🔐 Security Notes

- Never commit secret keys, passwords, or private credentials.
- Keep virtual environments and local database files out of version control when appropriate.
- Do not use `DEBUG = True` in production.
- This project is a portfolio demonstration, not a claim of a production-ready banking system.

## 🎯 Project Purpose

NOVA BANK demonstrates practical Django development, authentication workflows, multilingual interfaces, and the design of a banking-themed web application.

## 👨‍💻 Author

**Aziz Yuldoshev**

GitHub: [@aziz-yuldoshev](https://github.com/aziz-yuldoshev)

## 📄 License

No specific open-source license is declared here. Add a license if you intend to define permissions for reuse and distribution.
