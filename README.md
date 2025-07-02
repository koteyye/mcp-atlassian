# 🧠 MCP Atlassian Server

Model Context Protocol (MCP) server для интеграции с Atlassian Jira и Confluence. Сервер работает по stdio-протоколу и совместим с Roo Code.

## 🏗️ Архитектура

Проект построен с использованием паттернов проектирования:

- **Singleton** - управление конфигурацией и логгером
- **Builder** - построение JSON-запросов к API
- **Command** - реализация команд MCP
- **Strategy** - абстракция между Jira и Confluence API
- **Chain of Responsibility** - обработка входящих команд
- **Decorator** - логирование и валидация

## 🔧 Установка и настройка

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Конфигурация

Отредактируйте файл `mcp_settings.json`:

```json
{
  "jira": {
    "url": "https://your-domain.atlassian.net",
    "username": "your-email@example.com",
    "api_token": "your-jira-api-token"
  },
  "confluence": {
    "url": "https://your-domain.atlassian.net/wiki",
    "username": "your-email@example.com",
    "api_token": "your-confluence-api-token"
  },
  "logging": {
    "level": "INFO",
    "file": "mcp_server.log"
  }
}
```

### 3. Получение API токенов

1. Перейдите в [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Создайте новый API токен
3. Скопируйте токен в конфигурацию

### 4. Запуск сервера

```bash
python main.py
```

## 🌐 Возможности

### Jira

1. **Создание задачи** - `create_jira_issue`
2. **Редактирование задачи** - `update_jira_issue`
3. **Удаление задачи** - `delete_jira_issue`
4. **Создание подзадачи** - `create_jira_subtask`
5. **Поиск задач** - `search_jira_issues`
6. **Debug информация** - `get_jira_debug_info`

### Confluence

1. **Создание статьи** - `create_confluence_page`
2. **Редактирование статьи** - `update_confluence_page`
3. **Удаление статьи** - `delete_confluence_page`
4. **Поиск статей** - `search_confluence_pages`
5. **Поиск дочерних статей** - `search_confluence_pages_by_parent`
6. **Debug информация** - `get_confluence_debug_info`

### Системные команды

- **ping** - проверка связи
- **health** - статус сервера
- **list_commands** - список всех команд

## 📝 Примеры использования

### Создание задачи в Jira

```json
{
  "method": "create_jira_issue",
  "params": {
    "project": "TEST",
    "summary": "Новая задача",
    "issuetype": "Task",
    "description": "Описание задачи",
    "assignee": "john.doe",
    "labels": ["urgent", "bug"]
  }
}
```

### Поиск задач по проекту

```json
{
  "method": "search_jira_issues",
  "params": {
    "project": "TEST",
    "maxResults": 10
  }
}
```

### Создание страницы в Confluence

```json
{
  "method": "create_confluence_page",
  "params": {
    "space": "DEV",
    "title": "Новая документация",
    "content": "<h1>Заголовок</h1><p>Содержимое страницы</p>"
  }
}
```

## 🔄 Расширение функциональности

Архитектура готова к расширению для интеграции с:

- GitHub
- Notion
- Telegram
- Slack
- И другими системами

### Добавление новой интеграции

1. Создайте новую папку в `src/` (например, `github/`)
2. Реализуйте API стратегию на основе `APIStrategy`
3. Создайте команды на основе `Command`
4. Добавьте обработчик в цепочку `Chain of Responsibility`
5. Обновите конфигурацию в `mcp_settings.json`

## 🐛 Отладка

### Логи

Логи записываются в файл `mcp_server.log` и выводятся в консоль.

### Debug команды

Используйте команды `get_jira_debug_info` и `get_confluence_debug_info` для получения:

- Списка проектов
- Типов задач
- Пространств
- Информации о пользователе

### Проверка связи

```json
{
  "method": "ping"
}
```

Ответ:
```json
{
  "success": true,
  "message": "pong"
}
```

## 📋 Требования к полям

### Jira задача

**Обязательные поля:**
- `project` - ключ проекта
- `summary` - название задачи
- `issuetype` - тип задачи

**Опциональные поля:**
- `description` - описание
- `assignee` - исполнитель
- `labels` - метки
- `epic` - эпик (для связи с эпиком)

### Confluence страница

**Обязательные поля:**
- `space` - ключ пространства
- `title` - заголовок страницы
- `content` - содержимое страницы

**Опциональные поля:**
- `parent` - ID родительской страницы

## ⚡ Производительность

- Используется `requests.Session` для переиспользования соединений
- Логирование с ротацией файлов
- Ограничение результатов поиска (по умолчанию 50)
- Валидация входных данных на раннем этапе

## 🔒 Безопасность

- API токены хранятся в конфигурационном файле
- HTTPS соединения для всех API запросов
- Валидация входных данных
- Логирование всех операций

## 🤝 Совместимость

- Python 3.8+
- Совместим с Roo Code
- Поддержка MCP протокола 2024-11-05
- Работает на Windows, macOS, Linux
