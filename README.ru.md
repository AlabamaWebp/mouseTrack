# Сервис обработки видео (Backend)

Python-сервис, который принимает видеофайлы, сохраняет их локально, обрабатывает через нейросеть и асинхронно возвращает результаты пользователям.

## Возможности

- **Загрузка видео**: Загрузка видеофайлов с автоматической дедупликацией (хеш SHA-256)
- **Асинхронная обработка**: Длительная обработка нейросетью в фоновом режиме
- **Обновления в реальном времени**: WebSocket-трансляция статуса очереди всем подключённым клиентам
- **Polling API**: HTTP-эндпоинты для проверки статуса задачи и получения результатов
- **Задел под авторизацию**: Готовая архитектура для простой интеграции аутентификации в будущем

## Быстрый старт

### Требования

- Python 3.12+
- Conda (Miniconda или Anaconda)

### Установка

```bash
# Создание conda-окружения
conda env create -f environment.yml

# Активация окружения
conda activate mousetrack
```

Альтернативный вариант через pip с виртуальным окружением:

```bash
# Создание виртуального окружения
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Установка зависимостей
pip install -r requirements.txt
```

### Запуск сервера

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Сервер запустится по адресу `http://localhost:8000`.

### Документация API

После запуска перейдите:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Эндпоинты API

### Загрузка видео
```
POST /api/v1/videos/upload
Content-Type: multipart/form-data

Поля формы:
- video: File (видеофайл)
- user_id: String (временно, будет заменён на auth-токен)

Ответ:
{
    "task_id": "uuid",
    "status": "pending",
    "message": "Видео успешно загружено",
    "is_duplicate": false
}
```

### Получение статуса задачи
```
GET /api/v1/tasks/{task_id}

Ответ:
{
    "task_id": "uuid",
    "status": "processing",
    "video_filename": "video.mp4",
    "progress": 50,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:01:00Z"
}
```

### Получение результата задачи
```
GET /api/v1/tasks/{task_id}/result

Ответ (завершено):
{
    "task_id": "uuid",
    "status": "completed",
    "result": {...},
    "completed_at": "2024-01-01T00:05:00Z"
}
```

### WebSocket — статус очереди
```
WebSocket /ws/queue

Подключитесь для получения обновлений в реальном времени:
- Статус обработки нейросетью (занят/свободен)
- Имя текущего обрабатываемого файла
- Очередь ожидающих задач
- Недавно завершённые задачи
```

## Структура проекта

```
mouseTrack-backend/
├── app/
│   ├── main.py                 # Точка входа FastAPI
│   ├── config.py               # Настройки
│   ├── database.py             # Подключение к БД и управление сессиями
│   ├── models/
│   │   ├── task.py             # Модель задачи
│   │   └── user.py             # Модель пользователя (задел под авторизацию)
│   ├── schemas/
│   │   ├── task.py             # Pydantic-схемы для задач
│   │   └── user.py             # Pydantic-схемы для пользователей
│   ├── api/
│   │   ├── upload.py           # Эндпоинт загрузки
│   │   ├── tasks.py            # Эндпоинты статуса и результата
│   │   └── auth.py             # Эндпоинты авторизации (заглушка)
│   ├── services/
│   │   ├── upload_service.py   # Обработка файлов и дедупликация
│   │   ├── task_service.py     # Управление жизненным циклом задач
│   │   ├── nn_processor.py     # Обработка нейросетью (универсальная)
│   │   └── websocket_manager.py # Управление WebSocket-соединениями и трансляция
│   └── utils/
│       └── file_utils.py       # Хеширование и валидация файлов
├── videos/                     # Локальное хранилище видео (создаётся автоматически)
├── .env                        # Переменные окружения
├── .env.example
├── requirements.txt
└── README.md
```

## Конфигурация

Переменные окружения (`.env`):

```env
# Сервер
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Хранилище
VIDEO_STORAGE_PATH=./videos
MAX_FILE_SIZE_MB=500
ALLOWED_VIDEO_EXTENSIONS=mp4,avi,mov,mkv,webm

# База данных
DATABASE_URL=sqlite:///./app.db

# Обработка
NN_PROCESSING_TIMEOUT_SECONDS=3600
```

## Интеграция нейросети

Процессор нейросети находится в [`app/services/nn_processor.py`](app/services/nn_processor.py:1). Замените класс `DefaultNNProcessor` на вашу реальную реализацию:

```python
class MyNNProcessor(NNProcessor):
    async def process(self, video_path: str) -> dict:
        # Ваша логика обработки нейросетью
        pass
```

Затем обновите глобальный экземпляр `processor` в том же файле.

## Задел под авторизацию

Система авторизации спроектирована для добавления в будущем без ломающих изменений:

1. **Сейчас**: `user_id` передаётся как поле формы в запросах загрузки
2. **В будущем**: JWT-токен в заголовке Authorization, `user_id` извлекается из токена
3. **Middleware**: Middleware авторизации будет добавлен для перехвата запросов
4. **База данных**: Модель пользователя уже существует для будущего расширения

## Лицензия

MIT
