# VFS-Global

# Инструкция по запуску сайта (Flask)

1. **Установите Python 3.10+**  
   Скачать: https://www.python.org/downloads/

2. **Создайте и активируйте виртуальное окружение:**
   ```
   python -m venv venv
   # Для Windows:
   venv\Scripts\activate
   # Для Linux/Mac:
   source venv/bin/activate
   ```

3. **Установите зависимости:**
   ```
   pip install flask prometheus_flask_exporter
   ```

4. **Запустите Flask-приложение:**
   ```
   cd site
   python app.py
   ```

5. **Откройте сайт в браузере:**
   - Главная страница: http://127.0.0.1:5000/dashboard


---

**Примечания:**
- Для работы с ботом Telegram используйте отдельную инструкцию.