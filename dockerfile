# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем обновления и необходимые зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем содержимое проекта в рабочую директорию контейнера
COPY . .

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --upgrade pip wheel
RUN pip install --no-build-isolation catboost
RUN pip install --no-cache-dir -r requirements.txt

# Указываем порт, который будет использоваться контейнером
EXPOSE 8050

# Определяем команду для запуска приложения
CMD ["python", "main.py"]

