# Инструкция для фронтенда — API бэкенда обработки видео

## Базовый URL

```
http://localhost:8000
```

## Генерация user_id

Поскольку авторизация ещё не реализована, фронтенд должен самостоятельно генерировать `user_id`. Рекомендуется использовать UUID и сохранять его в `localStorage`:

```javascript
// Генерация или получение user_id
let userId = localStorage.getItem('user_id');
if (!userId) {
    userId = crypto.randomUUID();
    localStorage.setItem('user_id', userId);
}
```

---

## API Эндпоинты

### 1. Загрузка видео

**Метод:** `POST`
**URL:** `/api/v1/videos/upload`
**Content-Type:** `multipart/form-data`

**Параметры формы:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| video | File | Видеофайл для загрузки |
| user_id | String | Идентификатор пользователя (сгенерированный UUID) |

**Пример запроса:**
```javascript
const formData = new FormData();
formData.append('video', videoFile);
formData.append('user_id', userId);

const response = await fetch('/api/v1/videos/upload', {
    method: 'POST',
    body: formData
});
const data = await response.json();
```

**Ответ (новое видео):**
```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "pending",
    "message": "Video uploaded successfully",
    "is_duplicate": false,
    "result": null
}
```

**Ответ (дубликат):**
```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "message": "Video already processed",
    "is_duplicate": true,
    "result": { /* результат обработки */ }
}
```

**Возможные статусы:**
- `pending` — ожидает обработки
- `processing` — обрабатывается
- `completed` — завершено
- `failed` — ошибка

---

### 2. Получение статуса задачи

**Метод:** `GET`
**URL:** `/api/v1/tasks/{task_id}`

**Пример запроса:**
```javascript
const response = await fetch(`/api/v1/tasks/${taskId}`);
const data = await response.json();
```

**Ответ:**
```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "processing",
    "video_filename": "my_video.mp4",
    "progress": 50,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:01:00Z"
}
```

---

### 3. Получение результата задачи

**Метод:** `GET`
**URL:** `/api/v1/tasks/{task_id}/result`

**Пример запроса:**
```javascript
const response = await fetch(`/api/v1/tasks/${taskId}/result`);
const data = await response.json();
```

**Ответ (завершено):**
```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "result": { /* результат обработки нейросетью */ },
    "error_message": null,
    "completed_at": "2024-01-01T00:05:00Z"
}
```

**Ответ (ещё обрабатывается):**
```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "processing",
    "result": null,
    "error_message": null,
    "completed_at": null
}
```

**Ответ (ошибка):**
```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "failed",
    "result": null,
    "error_message": "Ошибка обработки видео",
    "completed_at": "2024-01-01T00:05:00Z"
}
```

---

### 4. WebSocket — статус очереди в реальном времени

**URL:** `ws://localhost:8000/ws/queue`

Подключитесь для получения обновлений о состоянии очереди обработки в реальном времени.

**Пример подключения:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/queue');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Получено обновление:', data);
};

ws.onclose = () => {
    console.log('Соединение закрыто, переподключение...');
    setTimeout(connect, 3000);
};
```

**Типы сообщений:**

#### queue_update — обновление статуса очереди
```json
{
    "type": "queue_update",
    "nn_status": "busy",
    "current_processing": {
        "task_id": "uuid",
        "filename": "video.mp4",
        "user_id": "user123",
        "progress": 45
    },
    "pending_queue": [
        {
            "task_id": "uuid",
            "filename": "video2.mp4",
            "user_id": "user456"
        }
    ],
    "recently_completed": [
        {
            "task_id": "uuid",
            "filename": "video3.mp4",
            "user_id": "user789"
        }
    ]
}
```

#### nn_status_change — изменение статуса нейросети
```json
{
    "type": "nn_status_change",
    "status": "busy",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

#### task_completed — задача завершена
```json
{
    "type": "task_completed",
    "task_id": "uuid",
    "filename": "video.mp4"
}
```

**Поля `nn_status`:**
- `busy` — нейросеть занята обработкой
- `idle` — нейросеть свободна

---

## Типичный сценарий использования

```javascript
// 1. Генерация user_id
let userId = localStorage.getItem('user_id') || crypto.randomUUID();
localStorage.setItem('user_id', userId);

// 2. Подключение к WebSocket для получения обновлений
const ws = new WebSocket('ws://localhost:8000/ws/queue');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'queue_update') {
        updateQueueUI(data);
    }
    if (data.type === 'task_completed') {
        // Можно проверить результат задачи
        fetchTaskResult(data.task_id);
    }
};

// 3. Загрузка видео
async function uploadVideo(file) {
    const formData = new FormData();
    formData.append('video', file);
    formData.append('user_id', userId);

    const response = await fetch('/api/v1/videos/upload', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();

    if (data.is_duplicate) {
        // Видео уже обработано, результат сразу доступен
        showResult(data.result);
    } else {
        // Начать polling статуса
        startPolling(data.task_id);
    }
}

// 4. Polling статуса задачи
function startPolling(taskId) {
    const interval = setInterval(async () => {
        const response = await fetch(`/api/v1/tasks/${taskId}/result`);
        const data = await response.json();

        if (data.status === 'completed') {
            clearInterval(interval);
            showResult(data.result);
        } else if (data.status === 'failed') {
            clearInterval(interval);
            showError(data.error_message);
        }
    }, 2000); // Проверка каждые 2 секунды
}
```

---

## Интерактивная документация

После запуска сервера доступна интерактивная документация Swagger:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Ошибки

| Код | Описание |
|-----|----------|
| 400 | Неверный тип файла или файл слишком большой |
| 404 | Задача не найдена |
| 500 | Внутренняя ошибка сервера |
