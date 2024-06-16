# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем обновления и необходимые зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем содержимое проекта в рабочую директорию
COPY . .

# Устанавливаем зависимости проекта
RUN pip install --no-cache-dir -r requirements.txt

# Указываем порт, который будет использоваться контейнером
EXPOSE 8050

# Определяем команду для запуска приложения
CMD ["python", "main.py"]
