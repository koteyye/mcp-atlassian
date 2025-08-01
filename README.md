# 🧠 MCP Atlassian Server

Model Context Protocol (MCP) сервер для интеграции с Atlassian Jira и Confluence. Работает с Roo Code и Cline через stdio-протокол.

## 📋 Требования

Перед установкой убедись что у тебя есть:

### Python 3.8 или новее
- **Windows**: Скачай с [python.org](https://www.python.org/downloads/) и поставь галочку "Add Python to PATH"
- **macOS**: `brew install python3` или скачай с [python.org](https://www.python.org/downloads/)
- **Linux**: `sudo apt install python3 python3-pip` (Ubuntu/Debian) или `sudo yum install python3 python3-pip` (CentOS/RHEL)

### Проверка установки:
```bash
python3 --version
# Должно показать Python 3.8.0 или выше

pip3 --version
# Должно показать версию pip
```

### Git (для скачивания проекта):
- **Windows**: Скачай с [git-scm.com](https://git-scm.com/download/win)
- **macOS**: `brew install git` или скачай с [git-scm.com](https://git-scm.com/download/mac)
- **Linux**: `sudo apt install git` (Ubuntu/Debian) или `sudo yum install git` (CentOS/RHEL)

## � Быстрая установка для Roo Code / Cline

### Шаг 1: Скачиваем проект

```bash
git clone https://github.com/koteyye/mcp-atlassian.git
cd mcp-atlassian
```

### Шаг 2: Устанавливаем зависимости

Выбери один из вариантов в зависимости от твоей системы:

**Вариант 1 (рекомендуемый):**
```bash
pip3 install -r requirements.txt
```

**Вариант 2 (если pip3 не найден):**
```bash
python3 -m pip install -r requirements.txt
```

**Вариант 3 (если используешь обычный pip):**
```bash
pip install -r requirements.txt
```

**Вариант 4 (через python напрямую):**
```bash
python -m pip install -r requirements.txt
```

> **Примечание:** Если получаешь ошибки с правами доступа, попробуй добавить `--user` в конце команды

### Шаг 3: Получаем API токены

#### Для Jira и Confluence:
1. Идем на [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Жмем **"Create API token"**
3. Даем название токену (например "MCP Server")
4. Копируем токен - **ВАЖНО: он показывается только один раз!**

### Шаг 4: Настраиваем MCP сервер в mcp_settings.json

Нужно добавить наш сервер в файл `mcp_settings.json` для Roo Code или Cline.

**Для Roo Code:**
1. Открываем **VS Code**
2. Идем в **Settings** (Cmd/Ctrl + ,)
3. Ищем **"MCP"** или **"Roo Code"**
4. Находим секцию **MCP Servers** или открываем файл `mcp_settings.json`
5. Добавляем наш сервер:

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "python3",
      "args": ["/полный/путь/к/проекту/mcp-atlassian/main.py"],
      "env": {
        "jira_url": "https://your-domain.atlassian.net",
        "jira_username": "your address",
        "jira_api_token": "your token",
        "confluence_url": "https://your-domain.atlassian.net/wiki",
        "confluence_username": "your address",
        "confluence_api_token": "your token",
        "confluence_auth_type": "bearer / basic"
      }
    }
  }
}
```

**Для Cline:**
1. Открываем **Cline**
2. Идем в **Settings** → **MCP Servers**
3. Добавляем в файл `mcp_settings.json`:

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "python3",
      "args": ["/полный/путь/к/проекту/mcp-atlassian/main.py"],
      "env": {
        "jira_url": "https://your-domain.atlassian.net",
        "jira_username": "your address",
        "jira_api_token": "your token",
        "confluence_url": "https://your-domain.atlassian.net/wiki",
        "confluence_username": "your address",
        "confluence_api_token": "your token",
        "confluence_auth_type": "bearer / basic"
      }
    }
  }
}
```

> **Важно:** Замени `/полный/путь/к/проекту/mcp-atlassian/main.py` на реальный путь к файлу `main.py` в твоей системе!

### Шаг 5: Проверяем работу

1. Перезапускаем Roo Code / Cline
2. В чате пишем: **"Проверь подключение к Jira"**
3. Должен ответить что-то типа: "Jira API работает, найдено X проектов"

## 🛠️ Что умеет сервер

### Jira команды:
- ✅ **Создать задачу** - "Создай задачу в проекте TEST с названием 'Исправить баг'"
- ✅ **Найти задачи** - "Найди все задачи в проекте TEST"
- ✅ **Получить инфо** - "Покажи информацию о Jira"

### Confluence команды:
- ✅ **Создать страницу** - "Создай страницу в пространстве DEV с заголовком 'Документация'"
- ✅ **Найти страницы** - "Найди страницы в пространстве DEV"
- ✅ **Получить инфо** - "Покажи информацию о Confluence"

### Системные команды:
- ✅ **Проверка связи** - "Проверь подключение к серверу"
- ✅ **Статус** - "Покажи статус конфигурации"

## 🔧 Ручная настройка (альтернативный способ)

Если не хочешь использовать переменные окружения, можешь создать файл `config.json`:

```json
{
  "jira": {
    "url": "https://your-domain.atlassian.net",
    "username": "your-email@example.com",
    "api_token": "your-jira-api-token",
    "auth_type": "basic"
  },
  "confluence": {
    "url": "https://your-domain.atlassian.net/wiki", 
    "username": "your-email@example.com",
    "api_token": "your-confluence-api-token",
    "auth_type": "basic"
  },
  "ssl_disable": false
}
```

## 🐛 Если что-то не работает

### Проблема: "Не могу подключиться к Jira"
**Решение:**
1. Проверь URL - должен быть без `/` в конце
2. Проверь токен - создай новый если нужно
3. Проверь username - должен быть email

### Проблема: "SSL ошибки"
**Решение:**
Добавь в переменные окружения:
```bash
SSL_DISABLE=true
```

### Проблема: "Сервер не отвечает"
**Решение:**
1. Проверь что Python 3.8+ установлен
2. Проверь что все зависимости установлены: `pip install -r requirements.txt`
3. Запусти сервер вручную: `python3 main.py`

### Проблема: "Много логов в консоли"
**Решение:**
Логирование уже настроено на минимум - показываются только ошибки и предупреждения.

## 📝 Примеры использования в чате

### Создание задачи:
```
Пользователь: "Создай задачу в проекте TEST с названием 'Исправить баг авторизации' и описанием 'Пользователи не могут войти в систему'"

Ответ: "Создал задачу TEST-123: Исправить баг авторизации"
```

### Поиск задач:
```
Пользователь: "Найди все открытые задачи в проекте TEST"

Ответ: "Найдено 5 задач:
- TEST-123: Исправить баг авторизации (Open)
- TEST-124: Добавить новую функцию (In Progress)
..."
```

### Создание документации:
```
Пользователь: "Создай страницу в Confluence в пространстве DEV с заголовком 'API документация' и содержимым 'Описание REST API'"

Ответ: "Создал страницу 'API документация' в пространстве DEV"
```

## 🔒 Безопасность

- ✅ API токены хранятся в переменных окружения
- ✅ HTTPS соединения для всех запросов  
- ✅ Валидация всех входных данных
- ✅ Минимальное логирование (только ошибки)

## 🤝 Совместимость

- ✅ Python 3.8+
- ✅ Roo Code
- ✅ Cline  
- ✅ MCP протокол 2024-11-05
- ✅ Windows, macOS, Linux


---

**Короче братан, следуй инструкции пошагово и все будет работать! 🚀**
