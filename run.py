from model import NewsBlogAssistant
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('API_KEY')

if __name__ == "__main__":
    assistant = NewsBlogAssistant(audience="мамы", details="Основной фокус на новости, касающиеся важности раннего обучения детей арифметике, скорочтению (это просто примеры, придумывай более разнообразные тематики) и другим предметам.", API_KEY=API_KEY, add_image=True, save_dir='my_posts')
    generated_post = assistant.action()
    print("Сгенерированный пост:\n", generated_post)