# Лейн Бот

Telegram бот на базе AI через OpenRouter API, который отвечает на сообщения с упоминанием "Лейн".

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/cryptexctl/openlain
cd openlain
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
.\venv\Scripts\activate  # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` на основе `env.example`:
```bash
cp env.example .env
```

5. Заполните `.env` файл своими данными:
- Получите токен бота у [@BotFather](https://t.me/BotFather)
- Получите API ключ на [OpenRouter](https://openrouter.ai/keys)

## Запуск

```bash
python main.py
```

## Устранение неполадок

### Бот не отвечает
1. Проверьте, что бот запущен и нет ошибок в логах
2. Убедитесь, что в сообщении есть слово "Лейн"
3. Проверьте подключение к интернету

### Ошибка с API ключом
1. Проверьте правильность API ключа в `.env`
2. Убедитесь, что ключ активен в OpenRouter
3. Проверьте баланс и квоты использования API

### Ошибки в логах
- Проверьте файл `bot.log` для детальной информации
- Убедитесь, что все переменные окружения установлены
- Проверьте версии зависимостей в `requirements.txt`

## Команды

- `/start` - Начало работы с ботом
- `/clear` - Очистка истории диалога

## Технические детали

- Python 3.8+
- aiogram 3.19.0
- OpenRouter API 
- Логирование в файл и консоль
- Автоматическая очистка старых диалогов
- Ограничение размера сообщений


