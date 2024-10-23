# Blogger Bot

`Blogger Bot` — это инструмент для автоматизации создания блогов, основанная на поиске актуальных новостей для заданной целевой аудитории. Ассистент автоматически собирает новости, анализирует их и формирует посты с возможностью добавления изображений, генерируемых через API OpenAI (провайдер proxyapi.ru). Для генерации текста используется __gpt-4o-mini__, изображений – __dall-e-3__.

Примеры работы можно посмотреть в папках my_posts, output.

#### В решении можно выделить несколько ключевых агентов:

- **Генератор идей**: Генерирует идеи для постов, формируя поисковые запросы на основе аудитории и истории заголовков, а также дополнительно заданных деталей.

- **Исследователь**: Осуществляет поиск новостей и скраппинг данных с различных источников, собирая актуальную информацию.

- **Аналитик**: Выбирает наиболее подходящие новости и генерирует заголовки, акцентируя внимание на новизне и актуальности.

- **Создатель контента**: Пишет посты на основе собранных материалов, делая акцент на целевую аудиторию и стиль блога.

#### Возможности:
- Поиск новостей на основе целевой аудитории.
- Генерация заголовков и содержания постов.
- Хранение и использование истории заголовков во избежание повторов контента
- Выбор произвольной аудитории бота
- Скраппинг текста с новостных сайтов.
- Автоматическая генерация изображений.
- Сохранение постов в `.md` и конвертация в `.docx`.

## Технические особенности решения

### Используемые библиотеки
- **OpenAI**: Для взаимодействия с моделями GPT и генерации текстов.
- **Langchain**: Для поиска актуальных новостей по заданным запросам.
- **BeautifulSoup**: Для парсинга HTML-кода и извлечения текстовой информации с веб-страниц.
- **Markdown2docx**: Для конвертации Markdown в формат .docx.
- **PIL (Pillow)**: Для работы с изображениями.

### Архитектура класса `NewsBlogAssistant`
1. **Инициализация**: При создании экземпляра класса задаются параметры аудитории, деталей поста, API ключа и настроек для сохранения файлов.
2. **Генерация идей**: Используя историю заголовков, ассистент формирует новые поисковые запросы для сбора новостей.
3. **Поиск и скраппинг**: Ассистент ищет новости по запросам и собирает текстовую информацию с веб-страниц.
4. **Выбор и генерация заголовка**: На основе собранных данных выбирается наиболее актуальная информация, формируется заголовок поста.
5. **Генерация контента**: Используя собранные материалы, ассистент создает текст поста с учетом стиля блога.
6. **Генерация изображений**: Создание иллюстраций на основе содержимого поста с использованием DALL-E-3.
7. **Сохранение и конвертация**: Сохранение поста в формате Markdown и его конвертация в .docx.

### Обработка ошибок
Программа включает обработку ошибок для сетевых запросов и сохранения файлов, что позволяет избежать падения при возникновении исключительных ситуаций.

### Возможные улучшения
- **Использование другого API для извлечения новостей**: в качестве базового варианта был выбран api DuckDuckGo, однако он не подойдет, если требуется использовать бота несколько раз в час: имеется лимит на количесвто запросов. Как альтернативу можно рассмотреть Serper, который предоставляет 2500 бесплатных запросов в месяц, далее 50000 за 50$. Еще одно преимущество в том, что Serper предоставляет, в целом, более релевантные новости, а также дату их написания, что может улучшить процесс отбора новостей. Пример использования и вывод этого API есть в папке notebooks.

- **Встроить функционал отправки поста в некоторую социальную сеть**: была протестирована отправка поста в телеграм-канал. Пример также есть в notebooks.

- **Добавить возможность пользователю определять личности ботов**: в коде заложена направленность на естественность текста, который генерируется ботом, однако данная функция может добавить блогу своеобразность, что имеет значение для социальных сетей.

- **Добавить возможность пользователю самому задавать фиксированные идеи для интернет-поиска**: для некоторых тематик может быть уместно каждый раз искать какой-то один запрос, например "AI". Такие тематики отличаются тем, что они постоянно имеют большой поток новостей.

### Установка
1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/galkin-v/blogger_bot.git
### Использование
1. Создайте файл `.env` и добавьте в него ваш API ключ:

   ```env
   API_KEY=ваш_ключ
2. Запустите бота:

   ```python3
   python3 run.py
