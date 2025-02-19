import random
import logging
import requests
import datetime
import html
import pylast
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from deep_translator import GoogleTranslator
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from googletrans import Translator

API_TOKEN = "7353125454:AAHIEN3FlgcJcjkdodkPjt7QEowOwqS4Lok"
KINOPOISK_TOKEN = "YH6CRVH-XNP4VHG-KFP5X4P-F5W9VM8", "ATN6000-G704F9D-KQCZT3E-KTH37YZ"
GOOGLE_API_KEY = "AIzaSyCx89KE_DA4nU_z7iF9NcoH_JQ8nuFT54E"
BASE_URL = "https://www.googleapis.com/books/v1/volumes"
open_weather_token = "e3cccd7d4cd9548c698de530fd4115d4"
API_KEY = "1b05b79dcbb6ccee0b0f744f181b440f"
API_SECRET = "a9e2240cc9f797e685b3d74d495febb1"

logging.basicConfig(level=logging.INFO)  # все сообщения логирования с уровнем важности INFO и выше (например, WARNING, ERROR, CRITICAL) будут обрабатываться и выводиться.

# Создаем сессию для работы с API
network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)

bot = Bot(token=API_TOKEN, parse_mode="HTML")  # эта строка кода создает экземпляр бота с заданным токеном и устанавливает режим парсинга текста в сообщениях на HTML.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)  # отвечает за создание экземпляра класса Dispatcher, который управляет обработкой входящих обновлений от Telegram и маршрутизацией их к соответствующим обработчикам.

LANGUAGES = ["ru", "en", "fr", "es"]

WORD_TRANSLATIONS = {
    "фэнтези": "fantasy",
    "детектив": "mystery",
    "научная фантастика": "science fiction",
    "ужасы": "horror",
    "роман": "romance",
    "история": "history",
    "биография": "biography",
    "наука": "science",
    "психология": "psychology",
    "философия": "philosophy",
    "искусство": "art",
    "комиксы": "comics",
    "поэзия": "poetry",
    "Русский": 'ru',
    "Английский": "en",
    "Французский": "fr",
    "Испанский": "es",
    "Рандом": "random",
}

TRANSLATIONS_GENRE = {
    "рок": "rock",
    "хип-хоп":"hip-hop",
    "инди":"indie",
    "рэп":"rap",
    "метал":"metal",
    "классика":"classical",
    "хардкор":"hardcore",
    "джаз":"jazz",
    "регги":"reggae",
    "панк":"punk"
}

search_requests = ["Поиск по годам", "Поиск по жанрам", "Случайный фильм"]
genres = ["комедия", "драма", "фантастика", "боевик", "триллер",]
years = ["90е-00ые", "00ые-10ые", "10ые-наше время"]
start_commands = ["Погода", "Фильмы", "Переводчик","Книги","Музыка"]
books_main_buttons = ["По жанрам", "По годам","случайная книга"]
back_button = ["Назад"]
buttons = ['Русский', 'English', 'Français', 'Español']
BOOKS_BUTTONS = list(WORD_TRANSLATIONS.keys())[:13]
MUSIC_BUTTONS = list(TRANSLATIONS_GENRE.keys())
MUSIC_BUTTONS_TYPES = ["по жанру", "по исполнителю"]
books_languages_buttons = ["Русский", "Английский", "Французский", "Испанский", "Рандом"]


user_languages = {} #словарь для хранения выбранного языка


# Определяем состояния для погоды
class GetInfo(StatesGroup):
    city = State()


# Определяем состояния для музыки
class MusicSearch(StatesGroup):
    music = State()
    choose = State()
    artist = State()
    lyrics = State()


# Определяем состояния для книг
class BookSearch(StatesGroup):
    choice = State()  # Выбор между "По жанрам" и "По годам"
    genre = State()  # Состояние для жанра
    language_by_genre = State() # Состояние для языка "По жанрам"
    language_by_year = State()  # Состояние для языка "По годам"
    year_range = State()  # Состояние для года
    random_book = State() # Состояние для случайной книги


#Функция для случайного трека по жанру
def get_random_track_by_genre(genre: str):
    try:
        tag = network.get_tag(genre)
        top_tracks = tag.get_top_tracks(limit=100)
        if not top_tracks:
            return f"Не найдено треков по жанру '{genre}'"

        random_track = random.choice(top_tracks)
        track = random_track.item
        artist = track.get_artist()

        track_name = track.get_title()
        artist_name = artist.get_name()
        album = track.get_album()
        album_name = album.get_title() if album else "Неизвестный альбом"
        playcount = track.get_playcount() or "Нет данных"
        track_url = track.get_url()

        # Попытка получить обложку альбома
        album_cover_url = album.get_cover_image() if album else None

        result = (f"*Вот что я нашел для тебя!*\n"
                  f"*Исполнитель:* {artist_name}\n"
                  f"*Трек:* {track_name}\n"
                  f"*Альбом:* {album_name}\n"
                  f"*Прослушиваний:* {playcount}\n"
                  f"*Слушать:* [Last.fm]({track_url})")

        return result,album_cover_url

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        return f"Произошла ошибка: {e}"


#Функция для случайного трека по артисту
def get_random_track_by_artist(genre: str, artist_name):
    try:
        artist = network.get_artist(artist_name)
        top_tracks2 = artist.get_top_tracks(limit=10)
        if not top_tracks2:
            return f"Не найдено треков по жанру '{artist_name}'"

        random_track2 = random.choice(top_tracks2)
        track = random_track2.item
        track_name = track.get_title()
        album = track.get_album()
        album_name = album.get_title() if album else "Неизвестный альбом"
        playcount = track.get_playcount() or "Нет данных"
        track_url = track.get_url()

        # Попытка получить обложку альбома
        album_cover_url = album.get_cover_image() if album else None

        result = (f"🎶 *Вот что я нашел для тебя!*\n"
                  f"🔥 *Исполнитель:* {artist_name}\n"
                  f"🎵 *Трек:* {track_name}\n"
                  f"💿 *Альбом:* {album_name}\n"
                  f"📅 *Прослушиваний:* {playcount}\n"
                  f"🎧 *Слушать:* [Last.fm]({track_url})")

        return result,album_cover_url

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        return f"Произошла ошибка: {e}"


# Функция перевода текста
def translate_text(text, user_id, to_lang=None):
    if not to_lang:
        to_lang = user_languages.get(user_id, 'ru')
    try:
        translator = GoogleTranslator(source='auto', target=to_lang)
        translation = translator.translate(text)
        return translation
    except Exception as e:
        return f"Произошла ошибка при переводе: {e}"


def translate_text_for_books(text, target_language="ru"):
    translator = Translator()
    try:
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except Exception as e:
        logging.error(f"Ошибка перевода: {e}")
        return text


# Функция для получения случайной книги по жанру
def get_random_book_by_genre(genre, language="ru"):
    genre = WORD_TRANSLATIONS.get(genre.lower(), genre)  # Перевод жанра

    params = {
        "q": f"subject:{genre}",
        "maxResults": 40,
        "printType": "books",
        "langRestrict": language,
        "key": GOOGLE_API_KEY
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        books = data.get("items", [])

        if books:
            book = random.choice(books)
            volume_info = book.get("volumeInfo", {})

            title = volume_info.get("title", "Без названия")
            authors = ", ".join(volume_info.get("authors", ["Неизвестный автор"]))
            description = volume_info.get("description", "Описание отсутствует")
            link = volume_info.get("infoLink", "Нет ссылки")

            # Извлечение обложки, если доступна
            image_links = volume_info.get("imageLinks", {})
            thumbnail = image_links.get("thumbnail", None)

            # Перевод заголовка, авторов и описания (если не на русском)
            if language != "ru":
                title = translate_text_for_books(title, target_language="ru")
                authors = translate_text_for_books(authors, target_language="ru")
                if description != "Описание отсутствует":
                    description = translate_text_for_books(description, target_language="ru")

            # Формирование сообщения
            message = (f" <b>{html.escape(title)}</b>\n"
                       f" <i>{html.escape(authors)}</i>\n"
                       f" {html.escape(description[:500])}...\n"
                       f" <a href='{link}'>Подробнее</a>")

            # Добавление обложки, если есть
            if thumbnail:
                message = f"<a href='{thumbnail}'>​</a>\n" + message

            return message
        else:
            logging.warning(f"No books found for genre: {genre} and language: {language}")
            return f" Книг в жанре <b>{genre}</b> на языке <b>{language}</b> не найдено."
    else:
        logging.error(f"API Error {response.status_code}: {response.text}")
        return f"Ошибка: {response.status_code}"


# Функция для получения случайной книги по языку
def get_random_book_by_year(year_range,genre, language="ru"):
    params = {
        "q": f"subject:{genre}",
        "maxResults": 40,
        "printType": "books",
        "langRestrict": language,
        "filter": "free-ebooks",
        "key": GOOGLE_API_KEY
    }
    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        books = data.get("items", [])

        if books:
            book = random.choice(books)
            volume_info = book.get("volumeInfo", {})

            title = volume_info.get("title", "Без названия")
            authors = ", ".join(volume_info.get("authors", ["Неизвестный автор"]))
            description = volume_info.get("description", "Описание отсутствует")
            link = volume_info.get("infoLink", "Нет ссылки")

            image_links = volume_info.get("imageLinks", {})
            thumbnail = image_links.get("thumbnail", None)

            if params.get("langRestrict") != "ru":
                title = translate_text_for_books(title, target_language="ru")
                authors = translate_text_for_books(authors, target_language="ru")
                if description != "Описание отсутствует":
                    description = translate_text_for_books(description, target_language="ru")

            message = (f" <b>{html.escape(title)}</b>\n"
                       f" <i>{html.escape(authors)}</i>\n"
                       f" {html.escape(description[:500])}...\n"
                       f" <a href='{link}'>Подробнее</a>")

            if thumbnail:
                message = f"<a href='{thumbnail}'>​</a>\n" + message

            return message
        else:
            return "Книги по вашему запросу не найдены."
    else:
        logging.error(f"API Error {response.status_code}: {response.text}")
        return f"Ошибка: {response.status_code}"


# Функция для получения случайной книги по языку
def get_random_book(genre, language="ru"):
    genre = WORD_TRANSLATIONS.get(genre.lower(), genre)  # Перевод жанра

    params = {
        "q": f"subject:{genre}",
        "maxResults": 40,
        "printType": "books",
        "langRestrict": language,
        "key": GOOGLE_API_KEY
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        books = data.get("items", [])

        if books:
            book = random.choice(books)
            volume_info = book.get("volumeInfo", {})

            title = volume_info.get("title", "Без названия")
            authors = ", ".join(volume_info.get("authors", ["Неизвестный автор"]))
            description = volume_info.get("description", "Описание отсутствует")
            link = volume_info.get("infoLink", "Нет ссылки")

            # Извлечение обложки, если доступна
            image_links = volume_info.get("imageLinks", {})
            thumbnail = image_links.get("thumbnail", None)

            # Перевод заголовка, авторов и описания (если не на русском)
            if language != "ru":
                title = translate_text_for_books(title, target_language="ru")
                authors = translate_text_for_books(authors, target_language="ru")
                if description != "Описание отсутствует":
                    description = translate_text_for_books(description, target_language="ru")

            # Формирование сообщения
            message = (f" <b>{html.escape(title)}</b>\n"
                       f" <i>{html.escape(authors)}</i>\n"
                       f" {html.escape(description[:500])}...\n"
                       f" <a href='{link}'>Подробнее</a>")

            # Добавление обложки, если есть
            if thumbnail:
                message = f"<a href='{thumbnail}'>​</a>\n" + message

            return message
        else:
            logging.warning(f"No books found for genre: {genre} and language: {language}")
            return f" Книг в жанре <b>{genre}</b> на языке <b>{language}</b> не найдено."
    else:
        logging.error(f"API Error {response.status_code}: {response.text}")
        return f"Ошибка: {response.status_code}"


def random_token():
    return random.choice(KINOPOISK_TOKEN)


"""
функция отвечает за получение случайного токена, который может использоваться для аутентификации или доступа к ресурсам, связанным с КиноПоиском

"""


def build_and_execute_request(limit, genre_name, selectFields, notNullFields):
    base_url = "https://api.kinopoisk.dev/v1.4/movie/random"
    params = f"token={random_token()}&limit={limit}&genres.name={genre_name}"
    """
    Функция предназначена для построения и выполнения запроса к API КиноПоиска, который возвращает случайные фильмы на основе заданных параметров.
    limit: определяет количество фильмов, которые необходимо вернуть в ответе
    genre_name: тип жанра, по которому будет осуществляться фильтрация
    selectFields: список полей, которые необходимо выбрать из данных, возвращаемых API
    notNullFields: аналогично selectFields, но для полей, которые должны содержать непустые значения
    base_url: задает базовый URL для API-запроса. В данном случае это адрес для получения случайных фильмов
    params: формирует параметры для запроса
    token={random_token()}: вызывает функцию random_token(), чтобы получить случайный токен для аутентификации.
    limit={limit}: добавляет параметр ограничения на количество возвращаемых фильмов
    genres.name={genre_name}: фильтрует результаты по имени жанра
    """
    if selectFields:
        for field in selectFields:
            params += f"&selectFields={field}"
    if notNullFields:
        for field in notNullFields:
            params += f"&notNullFields={field}"
    url = f"{base_url}?{params}"
    print(url)
    """
    Этот фрагмент кода формирует URL-адрес с параметрами запроса на основе значений из списков selectFields и notNullFields.
    Если переменная selectFields не пуста (то есть содержит элементы), то для каждого поля добавляется параметр selectFields к строке params.
    если notNullFields не пуст, то каждый элемент этого списка добавляет параметр notNullFields в params.
    создание итогового URL, где base_url — это базовый адрес
    """

    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка запроса: {response.status}")
            return None
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None


"""
Начало блока, в котором осуществляется попытка выполнения кода, который может вызвать исключение
response = requests.get(url): Выполняет HTTP GET-запрос по указанному URL. Результат запроса сохраняется в переменной response.
if response.status_code == 200: Проверяет, успешен ли запрос. Статус код 200 означает, что запрос выполнен успешно, и ресурс найден
return response.json(): Если запрос успешен, возвращает ответ в формате JSON (переводит ответ сервера в словарь Python)
print(f"Ошибка запроса: {response.status}"): Выводит сообщение о том, что произошла ошибка при запросе, и отображает статус ответа.
return None: Возвращает None, что сигнализирует о неудаче в получении данных
except Exception as e: Блок, который перехватывает все исключения, возникающие в блоке try
print(f"Произошла ошибка: {e}") - Выводит сообщение об ошибке, если она произошла во время выполнения запроса (например, проблемы с сетью, неправильный URL и т.д.)
return None: Возвращает None в случае возникновения исключения
"""


async def get_random_movies_by_genre_sync(genre: str) -> dict:
    """
    Получить случайный фильм заданного жанра с трейлером.
    :param genre: Жанр фильма
    :return: Случайный фильм и его постер
    """

    limit = 10
    selectFields = ["name", "description", "year", "poster", "videos"]
    notNullFields = ["videos.trailers.url"]

    response = build_and_execute_request(limit, genre, selectFields, notNullFields)

    if response:  # Эта строка проверяет, что переменная response содержит данные
        trailer_url = "No trailer available"  # переменная trailer_url с начальнм значением "No trailer available"
        if (
                "videos" in response
                and "trailers" in response["videos"]
                and response["videos"]["trailers"]
        ):
            trailer_url = response["videos"]["trailers"][0].get(
                "url", "No trailer available"
            )
            trailer_name = response["videos"]["trailers"][0].get(
                "name", "No trailer available"
            )
            """
            код проверяет, присутствуют ли в response разделы "videos" и "trailers", а также есть ли в trailers какие-либо данные.
            Если трейлеры есть, то он извлекает URL и имя первого трейлера. Если каких-либо данных нет, будет возвращено значение по умолчанию: "No trailer available".
            """
        genres = ", ".join(genre["name"] for genre in response["genres"])
        # строка создает строку с названиями жанров, которые находятся в response["genres"]. Каждое имя жанра будет разделено запятой
        description = response["description"]
        # Здесь просто извлекается описание фильма из ответа
        formatted_movie = f"""<b>{response['name']} ({response['year']})</b>
[{genres}]

{description[:800]}     


<b>Трейлер:</b> <a href='{trailer_url}'>{trailer_name}</a> """  # генерирует HTML-ссылку на трейлер фильма
        return formatted_movie, response.get("poster", {}).get("url",
                                                               "")  # возвращает два значения: отформатированную строку formatted_movie и URL постера фильма, если он существует (иначе возвращается пустая строка)
    else:
        print("Ошибка при получении данных.")
        return None, None


"""
<b>{response['name']} ({response['year']})</b>: В этом выражении используется значение имени фильма (response['name']) и год его выпуска (response['year']). 
Эти значения оборачиваются в HTML-теги <b>, чтобы сделать их жирными
[{genres}]: Это переменная, содержащая жанры фильма, и она также будет вставлена в строку
{description[:800]}: берется описание фильма и к строке добавляется только первые 800 символов
trailer_url: это URL трейлера
trailer_name: текст ссылки
"""


async def get_random_movies_by_year_range_sync(year_range: str) -> dict:
    """
    Получить случайный фильм заданного диапазона годов с трейлером.
    :param year_range: Диапазон годов (например, "90е-00ые")
    :return: Случайный фильм и его постер
    """
    limit = 10
    selectFields = ["name", "description", "year", "poster", "videos"]
    notNullFields = ["videos.trailers.url"]

    # Определение диапазона годов
    year_ranges = {
        "90е-00ые": "1990-1999",
        "00ые-10ые": "2000-2009",
        "10ые-наше время": "2010-2024",
    }
    years = year_ranges.get(year_range, "1990-2024")

    response = build_and_execute_request_for_years(
        limit, years, selectFields, notNullFields
    )

    if response:
        trailer_url = "No trailer available"
        if (
                "videos" in response
                and "trailers" in response["videos"]
                and response["videos"]["trailers"]
        ):
            trailer_url = response["videos"]["trailers"][0].get(
                "url", "No trailer available"
            )
            trailer_name = response["videos"]["trailers"][0].get(
                "name", "No trailer available"
            )

        genres = ", ".join(genre["name"] for genre in response["genres"])

        description = response["description"]

        formatted_movie = f"""<b>{response['name']} ({response['year']})</b>
[{genres}]

{description[:800]}

<b>Трейлер:</b> <a href='{trailer_url}'>{trailer_name}</a> """
        return formatted_movie, response.get("poster", {}).get("url", "")
    else:
        print("Ошибка при получении данных.")
        return None, None


def build_and_execute_request_for_years(limit, years, selectFields, notNullFields):
    base_url = "https://api.kinopoisk.dev/v1.4/movie/random"
    params = f"token={random_token()}&limit={limit}&year={years}"
    """

    """
    if selectFields:
        for field in selectFields:
            params += f"&selectFields={field}"

    if notNullFields:
        for field in notNullFields:
            params += f"&notNullFields={field}"

    url = f"{base_url}?{params}"
    print(url)

    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка запроса: {response.status_code}")
            return None
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None


# Обработчик команды /start
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_commands)
    await message.answer("Что умеет бот? \nМожет находить из базы данных 'Кинопоиска' фильмы \nДелать прогноз погоды \nПереводить текст с четырёх языков \nМожет находить из базы данных 'Google books' книги", reply_markup=keyboard)


# Обработчик запросов о музыке
@dp.message_handler(lambda message: message.text.lower() == "музыка")
async def create_keyboard_music(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*MUSIC_BUTTONS_TYPES, *back_button)  # Добавил правильные кнопки выбора
    await message.answer("Выберите способ поиска музыки:", reply_markup=keyboard)
    await MusicSearch.choose.set()


# Обработчик выбора критерия поиска музыки
@dp.message_handler(state=MusicSearch.choose)
async def music_criteria(message: types.Message, state: FSMContext):
    choice = message.text.strip().lower()

    if choice == "назад":
        await send_welcome(message)
        await state.finish()
        return

    if choice == "по жанру":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*MUSIC_BUTTONS, *back_button)
        await message.answer("Выберите жанр музыки из списка:", reply_markup=keyboard)
        await MusicSearch.music.set()

    elif choice == "по исполнителю":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*back_button)  # Добавляем кнопку назад
        await message.answer("Напишите имя исполнителя:", reply_markup=keyboard)
        await MusicSearch.artist.set()
    else:
        await message.answer("Пожалуйста, выберите корректный вариант из предложенных.")


@dp.message_handler(state=MusicSearch.music)
async def music_by_genre(message: Message, state: FSMContext):
    genre = message.text.strip().lower()

    if genre == "назад":
        await create_keyboard_music(message, state)  # Возвращаемся к выбору "по жанру" или "по исполнителю"
        return

    if genre not in MUSIC_BUTTONS:
        await message.answer("Пожалуйста, выберите жанр из списка.")
        return
    result, album_cover_url = get_random_track_by_genre(TRANSLATIONS_GENRE[genre])


    if album_cover_url:
        await message.answer_photo(album_cover_url)

    await message.answer(result)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*MUSIC_BUTTONS, *back_button)
    await message.answer("Вы можете выбрать другой жанр или вернуться назад.", reply_markup=keyboard)

    await MusicSearch.music.set()


@dp.message_handler(state=MusicSearch.artist)
async def music_by_artist(message: Message, state: FSMContext):
    artist_name = message.text.strip()

    if artist_name.lower() == "назад":
        await create_keyboard_music(message, state)  # Возвращаемся в меню выбора жанра/исполнителя
        return

    result, album_cover_url = get_random_track_by_artist("жанр", artist_name)

    if album_cover_url:
        await message.answer_photo(album_cover_url)

    await message.answer(result)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*back_button)
    await message.answer("Вы можете выбрать другого исполнителя или вернуться назад.", reply_markup=keyboard)

    await MusicSearch.artist.set()


# Обработчик запросов о книгах
@dp.message_handler(lambda c: c.text.startswith("Книги"))
async def create_keyboard_books(message: types.Message, state: FSMContext):
    await state.finish()  # Сброс всех состояний при вызове команды Фильмы
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*books_main_buttons,*back_button)
    await message.answer("Выберите способ поиска книги:", reply_markup=keyboard)
    await BookSearch.choice.set()


# Обработчик выбора критерия поиска
@dp.message_handler(state=BookSearch.choice)
async def choose_search_criteria(message: Message, state: FSMContext):
    choice = message.text.strip().lower()

    if choice == "назад":
        await send_welcome(message)
        await state.finish()
        return
    if choice == "по жанрам":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*BOOKS_BUTTONS, *back_button)
        await message.answer("Выберите жанр книги из списка:", reply_markup=keyboard)
        await BookSearch.genre.set()
    elif choice == "случайная книга":
        await BookSearch.random_book.set()
        await random_book(message)  # Вызов обработчика вручную
    elif choice == "по годам":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*years, *back_button)
        await message.answer("Выберите временной промежуток:", reply_markup=keyboard)
        await BookSearch.year_range.set()
    else:
        await message.answer("Пожалуйста, выберите корректный вариант: 'По жанрам', 'По годам' или 'Случайная книга' .")


#Получение случайной книги
@dp.message_handler(state=BookSearch.random_book)
async def random_book(message: Message):
    logging.info(f"Пользователь {message.from_user.id} запросил случайную книгу.")

    genre = random.choice(list(WORD_TRANSLATIONS.values())[:13])
    language = random.choice(LANGUAGES)

    logging.info(f"Выбранный жанр: {genre}, язык: {language}")

    result = get_random_book(genre, language)

    if not result:
        await message.answer(
            f"К сожалению, не удалось найти книгу для жанра <b>{genre}</b> на языке <b>{language}</b>.",
            parse_mode="HTML")
    else:
        await message.answer(f"Жанр: <b>{genre}</b>\nЯзык: <b>{language}</b>\n\n{result}",
                             parse_mode="HTML",
                             disable_web_page_preview=False)

    await BookSearch.choice.set()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*books_main_buttons, *back_button)
    await message.answer("Выберите способ поиска книги:", reply_markup=keyboard)

    logging.info(f"Пользователь {message.from_user.id} возвращен в состояние выбора.")


# Получение жанра
@dp.message_handler(state=BookSearch.genre)
async def get_genre(message: Message, state: FSMContext):
    genre = message.text.strip().lower()

    if genre == "назад":
        await create_keyboard_books(message, state)
        return
    if genre not in WORD_TRANSLATIONS:  # Проверка на корректный ввод
        await message.answer("Пожалуйста, выберите жанр из предложенных кнопок.")
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*books_languages_buttons, *back_button)
    await state.update_data(genre=genre)
    await message.answer("Теперь выберите язык книги или нажмите 'Рандом' для случайного выбора:", reply_markup=keyboard)
    await BookSearch.language_by_genre.set()


# Получение языка и поиск книги
@dp.message_handler(state=BookSearch.language_by_genre)
async def get_language(message: Message, state: FSMContext):
    user_data = await state.get_data()
    genre = user_data["genre"]
    language = message.text.strip()

    if language == "Назад":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*BOOKS_BUTTONS, *back_button)
        await message.answer("Выберите жанр книги из списка:", reply_markup=keyboard)
        await BookSearch.genre.set()
        return
    if language.capitalize() not in WORD_TRANSLATIONS:
        await message.answer("Пожалуйста, выберите язык из предложенных кнопок.")
        return

    if language == "Рандом":
        language = random.choice(LANGUAGES)
    else:
        language = WORD_TRANSLATIONS[language.capitalize()]

    result = get_random_book_by_genre(genre, language)
    await message.answer(f"Жанр: <b>{genre}</b>\nЯзык: <b>{language}</b>\n\n{result}",
                         parse_mode="HTML",
                         disable_web_page_preview=False)

    # Добавляем кнопку "Назад" для возврата к выбору жанра
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*BOOKS_BUTTONS,*back_button)
    await message.answer("Вы можете выбрать другой жанр или завершить сессию.", reply_markup=keyboard)

    await BookSearch.genre.set()  # Возвращаемся к выбору жанра


# Получение временного диапазона для поиска по годам
@dp.message_handler(state=BookSearch.year_range)
async def get_year_range(message: Message, state: FSMContext):
    year_range = message.text.strip()

    if year_range == "Назад":
        await create_keyboard_books(message, state)
        return
    if year_range not in years:
        await message.answer("Пожалуйста, выберите временной промежуток из предложенных кнопок.")
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*books_languages_buttons, *back_button)
    await state.update_data(year_range=year_range)
    await message.answer("Теперь выберите язык книги или нажмите 'Рандом' для случайного выбора:", reply_markup=keyboard)
    await BookSearch.language_by_year.set()


# Получение языка для поиска по годам
@dp.message_handler(state=BookSearch.language_by_year)
async def get_language_by_year(message: Message, state: FSMContext):
    user_data = await state.get_data()
    year_range = user_data.get("year_range", "")
    language = message.text.strip()

    if language == "Назад":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*years, *back_button)
        await message.answer("Выберите временной промежуток:", reply_markup=keyboard)
        await BookSearch.year_range.set()
        return
    if language not in WORD_TRANSLATIONS:
        await message.answer("Пожалуйста, выберите язык из предложенных кнопок.")
        return

    if language == "Рандом":
        language = random.choice(LANGUAGES)
    else:
        language = WORD_TRANSLATIONS[language.capitalize()]

    # Выбираем случайный жанр
    genre = random.choice(list(WORD_TRANSLATIONS.values())[:13])

    # Определяем годовые параметры
    if year_range == "90-е - 00-е":
        date_range = "1990-2000"
    elif year_range == "00-е - 10-е":
        date_range = "2000-2010"
    else:
        date_range = "2010-2025"

    result = get_random_book_by_year(year_range, genre, language)
    await message.answer(f"Временной промежуток: <b>{year_range}</b>\nЖанр: <b>{genre}</b>\nЯзык: <b>{language}</b>\n\n{result}",
                         parse_mode="HTML",
                         disable_web_page_preview=False)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*years, *back_button)
    await message.answer("Вы можете выбрать другой временной промежуток или завершить сессию:", reply_markup=keyboard)
    await BookSearch.year_range.set()


# Обработчик запросов о фильмах
@dp.message_handler(lambda c: c.text.startswith("Фильмы"))
async def create_keyboard_kino(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(*search_requests, "↩ Назад")
    await message.answer("Выбери категорию", reply_markup=keyboard)


@dp.message_handler(lambda c: c.text.startswith("Поиск по жанрам"))
async def process_callback_button(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(*genres, "↩ Назад")
    await message.answer("Выбери жанр фильма:", reply_markup=keyboard)


@dp.message_handler(lambda c: c.text.startswith("Поиск по годам"))
async def process_callback_button(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(*years, "↩ Назад")
    await message.answer("Выбери годы выпуска:", reply_markup=keyboard)


# Обработчик запросов о погоде
@dp.message_handler(lambda c: c.text.startswith('Погода'))
async def weather_base(message: types.Message):
    # Создаем клавиатуру с кнопками "Назад"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Назад"))
    await message.reply("Напишите мне название города, и я пришлю сводку погоды!", reply_markup=keyboard)
    await GetInfo.city.set()


# Обработка ввода названия города
@dp.message_handler(state=GetInfo.city)
async def city_handler(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Назад"))
    if message.text.lower() == "назад":
        # Если нажата кнопка "Назад", возвращаемся к приветствию
        await state.finish()
        return await send_welcome(message)

    async with state.proxy() as data:
        data['city'] = message.text

    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={data['city']}&appid={open_weather_token}&units=metric"
        )
        data = r.json()

        city = data["name"]
        cur_weather = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
            data["sys"]["sunrise"])

        # Отправка ответа с повторной отправкой клавиатуры
        await message.reply(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"Погода в городе: {city}\nТемпература: {cur_weather}C°\n"
            f"Влажность: {humidity}%\nДавление: {pressure} мм рт. ст.\nВетер: {wind} м/с\n"
            f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}\n"
            f"Хотите узнать погоду в другом городе?\n"
            f'Тогда напишите название города ещё раз',
            reply_markup=keyboard  # Повторная отправка клавиатуры
        )

        # Оставляем состояние активным для следующего города
        await GetInfo.city.set()

    except Exception as e:
        # В случае ошибки выводим сообщение об ошибке и предлагаем попробовать снова
        await message.reply(
            f"Не удалось получить данные о погоде. Проверьте правильность написания города и попробуйте еще раз.",
            reply_markup=keyboard  # Повторная отправка клавиатуры
        )
        await GetInfo.city.set()


@dp.message_handler(lambda c: c.text.startswith("Переводчик"))
async def set_language(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*buttons, *back_button)
    await message.reply("Выберите язык перевода:", reply_markup=keyboard)


# Обработчик выбора языка
@dp.message_handler(lambda msg: msg.text in {'Русский', 'English', 'Français', 'Español'})
async def language_chosen(message: types.Message):
    lang_map = {
        'Русский': 'ru',
        'English': 'en',
        'Français': 'fr',
        'Español': 'es'
    }
    user_languages[message.from_user.id] = lang_map[message.text]
    await message.reply(f"Язык перевода установлен на {message.text}. Теперь отправляйте тексты для перевода.")


# Обработчик кнопки "Назад"
@dp.message_handler(lambda msg: msg.text == "Назад")
async def back_to_start(message: types.Message):
    await send_welcome(message)


@dp.message_handler(lambda msg: msg.text in genres or msg.text in years or msg.text == "Случайный фильм")
async def send_movies(message: types.Message):
    try:
        if message.text == "Случайный фильм":
            genre = random.choice(genres)
            text, image = await get_random_movies_by_genre_sync(genre)
        elif message.text.lower() in genres:
            genre = message.text.lower()
            text, image = await get_random_movies_by_genre_sync(genre)
        elif message.text.lower() in years:
            year = message.text.lower()
            text, image = await get_random_movies_by_year_range_sync(year)
        else:
            await send_welcome(message)
            return

        if not text:
            return

        await message.answer_photo(photo=image, caption=text)
    except:
        await send_movies(message)


@dp.message_handler(lambda msg: msg.text == "↩ Назад")
async def back_to_start(message: types.Message):
    await send_welcome(message)


# Обработчик всех сообщений
@dp.message_handler()
async def handle_message(message: types.Message):
    # Проверяем, является ли сообщение выбором языка
    if message.text in {'Русский', 'English', 'Français', 'Español'}:
        return

    # Получаем текст сообщения
    text_to_translate = message.text

    # Переводим текст
    translated_text = translate_text(text_to_translate, message.from_user.id)

    # Отправляем ответ пользователю
    await message.answer(translated_text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
