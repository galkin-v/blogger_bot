import os
import re
from openai import OpenAI
from langchain_community.tools import DuckDuckGoSearchResults
import requests
from bs4 import BeautifulSoup
from Markdown2docx import Markdown2docx
from PIL import Image
from io import BytesIO

class NewsBlogAssistant:
    def __init__(self, audience, details, API_KEY, add_image=True, backend='news', save_dir='output'):
        """Инициализируем ассистента с основными параметрами, включая директорию для сохранения файлов."""
        self.client = OpenAI(
            api_key=f'{API_KEY}',
            base_url='https://api.proxyapi.ru/openai/v1',
        )
        self.audience = audience
        self.details = details
        self.add_image = add_image
        self.backend = backend
        self.save_dir = save_dir
        self.title_history_file = os.path.join(self.save_dir, 'titles.txt')
        self.title_history = self.load_title_history()
        os.makedirs(self.save_dir, exist_ok=True)  # Создаем директорию, если она не существует

    def load_title_history(self):
        """Загружаем историю заголовков из файла."""
        if os.path.exists(self.title_history_file):
            with open(self.title_history_file, 'r') as f:
                return [line.strip() for line in f.readlines()]
        return []

    def save_title(self, title):
        """Сохраняем новый заголовок в файл и добавляем его в историю."""
        with open(self.title_history_file, 'a') as f:
            f.write(f"{title}\n")
        self.title_history.append(title)

    def generate_ideas(self):
        """Генерация новых идей для новостных запросов на основе аудитории и истории заголовков."""
        if self.title_history:
            history_statement = f"Вот твои предыдущие темы твоих постов: {self.title_history}. Не повторяйся."
        else:
            history_statement = "Учитывай, что это твой первый пост."

        while True:
            prompt = (
                f'Ты - ассистент, который должен находить в интернете последние новости, '
                f'связанные с целевой аудиторией - {self.audience}. '
                f'{history_statement} Сформируй 10 новых поисковых запросов для нахождения новостей. {self.details} '
                f'Выводи только в виде list, например: ["запрос1", "запрос2"].'
            )
            chat_completion = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[{'role': 'user', 'content': prompt}]
            )
            try:
                to_list = eval(chat_completion.choices[0].message.content)
                print('Идеи: ', to_list)
                return to_list
            except:
                continue

    def search(self, query):
        """Поиск новостей по заданному запросу через DuckDuckGo."""
        search_engine = DuckDuckGoSearchResults()
        response = search_engine.run(query, backend=self.backend)
        url_pattern = re.compile(r'https?://\S+')
        urls = re.findall(url_pattern, response)
        texts = re.split(url_pattern, response)
        results = [(text.strip()[:-7], url.rstrip(',')) for text, url in zip(texts, urls)]
        return results
    
    def scrape_text_from_urls(self, urls):
        """Скраппинг текста с новостных сайтов."""
        texts = []
        for url in urls:
            try:
                print(f"Scraping text from {url}...")
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                paragraphs = soup.find_all('p')
                text = '\n'.join([para.get_text() for para in paragraphs])
                if text:
                    texts.append(text)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {url}: {e}")
                continue
        return texts
    
    def selector(self, preview_news_text):
        """Выбор новостей и генерация заголовка для поста."""
        chat_completion = self.client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Проведи исследование, прочитав новости по сформированным запросам. Выяви запрос / несколько запросов, которые отлично подойдут для нового поста в твоем блоге (выведи их порядковый номер). Сделай акцент на новизну и актуальность информации для целевой аудитории российских {self.audience}. Глубоко вздохни и, хорошенько подумав, напиши заголовок твоего поста. Выводи в json. Пример вывода: {{website_ids: [0, 2, 5], title: ['Заголовок твоего поста']}} Новости: " + preview_news_text}],
        response_format={ "type": "json_object" })
        return eval(chat_completion.choices[0].message.content.replace('n  ', '').replace('n', ''))

    def collect_news(self):
        """Собираем новости по запросам и генерируем их краткий обзор."""
        search_ideas = self.generate_ideas()
        self.web = [self.search(idea) for idea in search_ideas]
        self.web = {i: content for i, content in enumerate([item for sublist in self.web for item in sublist])}
        previews = []
        for i, (key, value) in enumerate(self.web.items()):
            snippet, _ = value
            raw_text = f"Сайт {i}: {snippet.strip('snippet: ')}"
            previews.append(raw_text)
            
        return self.selector('\n'.join(previews))
    
    def generate_image(self, post):
        """Генерация изображения для поста на основе его содержания."""
        prompt = 'На основе данного поста предложи главную ассоциацию, которую можно использовать для генерации картинки. \n'
        chat_completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt + post}])
        
        association_prompt = chat_completion.choices[0].message.content
        
        post_cover = self.client.images.generate(
                model="dall-e-3",
                prompt=association_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
        return post_cover.data[0].url
            
    def write_post(self, news):
        """Генерация поста на основе собранных новостей и заголовка."""
        title = news['title'][0]
        selected_links = [self.web.get(x)[1] for x in news['website_ids']]
        scraped_data = 'Следующий сайт \n'.join(self.scrape_text_from_urls(selected_links))

        if self.title_history:
            history_statement = f"Вот твои предыдущие темы твоих постов: {self.title_history}. Не повторяй их."
        else:
            history_statement = "Учитывай, что это твой первый пост."

        prompt = (
            f'Представь, что ведешь свой блог. Используя собранные материалы и заголовок, напиши подходящий текст '
            f'краткого поста. {history_statement} '
            f'Сейчас 2024 год. Вспомни, что ты пишешь как блогер с целевой аудиторией - {self.audience}. '
            f'Текст должен подходить для блога, иметь новизну и актуальность. '
            f'Необязательно использовать всю информацию из материалов: сконцентрируйся на нескольких вещах и '
            f'разбери их более детально, высказывая своё мнение, как это делает блогер. Не делай пост слишком затянутым. '
            f'Используй emoji, где уместно. Веди себя наиболее естественно. Не пиши ничего, кроме поста, форматируй пост в стиле Markdown.'
        )
        chat_completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f'Заголовок поста: {title}' + prompt + f'Вот собранные материалы: {scraped_data}'}])

        post = chat_completion.choices[0].message.content

        # Сохраняем новый заголовок
        self.save_title(title)

        # Добавляем номер поста в имя файла
        post_number = len(self.title_history)
        post_file = os.path.join(self.save_dir, f'post_{post_number}.md')

        # Сохраняем пост
        with open(post_file, 'w+') as file:
            file.write(post)
        
        # Генерация изображения
        if self.add_image:
            post_cover_url = self.generate_image(post)
            print(f"Cover image URL: {post_cover_url}")

            try:
                response = requests.get(post_cover_url)
                response.raise_for_status()  # Проверка на ошибки запроса
                img = Image.open(BytesIO(response.content))

                # Сохранение изображения
                image_file = os.path.join(self.save_dir, f'post_{post_number}_cover.png')
                img.save(image_file)

            except requests.exceptions.RequestException as e:
                print(f"Failed to download the image: {e}")
            except Exception as e:
                print(f"Failed to save the image: {e}")
        
        # Преобразование markdown в docx
        try:
            print(f"Converting post to docx: {post_file}...")
            project = Markdown2docx(post_file[:-3], self.save_dir)
            project.eat_soup()
            project.save()
            print("Conversion completed successfully.")
        except Exception as e:
            print(f"Markdown conversion failed: {e}")
            
        return post
    
    def action(self):
        """Основной метод для запуска процесса сбора новостей и создания поста."""
        news = self.collect_news()  # Сбор новостей
        post = self.write_post(news)  # Генерация и запись поста
        return post  # Возвращаем созданный пост