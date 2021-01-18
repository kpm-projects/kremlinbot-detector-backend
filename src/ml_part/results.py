import os
import re

# pip install sklearn_pandas
# pip install scikit-learn==0.22.2

import requests
import pickle
import pandas as pd

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from string import punctuation

from pymystem3 import Mystem
import pymorphy2

emoticons = [u'&#_128514;', u'&#_128517;', u'u&#34;\U0001F923&#34;']

emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U0001F923"
                           u"\U0001F9A0"
                           u"\U0001F000-\U0001FFFF"
                           u"\U00002639"
                           "]+", flags=re.UNICODE)


def preprocess_text_mention_and_n(text):
    if text.find(" ") - 1 > 0 and text[text.find(" ") - 1] == ',':
        text = text[text.find(" ") + 1:]
    text = text.replace('\\n', ' ')
    return text


def clean_emoticons(text):
    for word in emoticons:
        text = text.replace(word, '')
    text = emoji_pattern.sub(r'', text)
    return text


def preprocess_text_lemmatize(text, setting="mystem"):
    text = text.lower()
    if text == '@@@':
        return text
    if setting == "mystem":
        mystem = Mystem()
        tokens = mystem.lemmatize(text)
    elif setting == "pymorphy":
        tokens = word_tokenize(text, language="russian")
        morph = pymorphy2.MorphAnalyzer()
        tokens = [morph.parse(token)[0].normal_form for token in tokens]
    else:
        raise Exception('parameter setting should be fill')
    # if len(tokens) == 1 and tokens[0] == "@@@":
    #   return " ".join(tokens)
    tokens = [token for token in tokens if token.strip() not in punctuation]
    tokens = " ".join(tokens)
    tokens = tokens.replace('-', ' ').replace("``", '').replace("''", '').replace(".", '').replace("«", '').replace("»",
                                                                                                                    '').replace(
        "—", '').replace("№", '')
    for symbol in punctuation:
        tokens = tokens.replace(symbol, '')
    for symbol in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
        tokens = tokens.replace(symbol, '')
    # print(tokens)
    return ' '.join(tokens.split())


url_stopwords_ru = "https://raw.githubusercontent.com/stopwords-iso/stopwords-ru/master/stopwords-ru.txt"

badwords = [
    u'я', u'а', u'да', u'но', u'тебе', u'мне', u'ты', u'и', u'у', u'на', u'ща', u'ага',
    u'так', u'там', u'какие', u'который', u'какая', u'туда', u'давай', u'короче', u'кажется', u'вообще',
    u'ну', u'не', u'чет', u'неа', u'свои', u'наше', u'хотя', u'такое', u'например', u'кароч', u'как-то',
    u'нам', u'хм', u'всем', u'нет', u'да', u'оно', u'своем', u'про', u'вы', u'м', u'тд',
    u'вся', u'кто-то', u'что-то', u'вам', u'это', u'эта', u'эти', u'этот', u'прям', u'либо', u'как', u'мы',
    u'просто', u'блин', u'очень', u'самые', u'твоем', u'ваша', u'кстати', u'вроде', u'типа', u'пока', u'ок'
]


def get_text(url, encoding='utf-8', to_lower=True):
    url = str(url)
    if url.startswith('http'):
        r = requests.get(url)
        if not r.ok:
            r.raise_for_status()
        return r.text.lower() if to_lower else r.text
    elif os.path.exists(url):
        with open(url, encoding=encoding) as f:
            return f.read().lower() if to_lower else f.read()
    else:
        raise Exception('parameter [url] can be either URL or a filename')


github_stopwords = get_text(url_stopwords_ru).splitlines()


def preprocess_text_stopwords(text, setting="nltk-stopwords"):
    # print(text)
    tokens = text.split()
    if setting == "nltk-stopwords":
        stopwords_for_delete = stopwords.words("russian")
    elif setting == "github-stopwords":
        stopwords_for_delete = github_stopwords
    elif setting == "badwords":
        stopwords_for_delete = badwords
    else:
        raise Exception('parameter setting should be fill')

    tokens = [token for token in tokens if token not in stopwords_for_delete \
              and len(token) > 2 \
              and token != " " \
              and token.strip() not in punctuation]
    tokens = " ".join(tokens)
    return tokens


def get_answer_by_file(pkl_filename, X_test):
    with open(pkl_filename, 'rb') as file:
        model, mapper, min_max_scaler = pickle.load(file)
    return get_answer(model, mapper, min_max_scaler, X_test)


def get_answer(model, mapper, min_max_scaler, X_test):
    X_test.replace({True: 1, False: 0})
    X_test['mystem'] = X_test['text'].apply(preprocess_text_mention_and_n)
    X_test['mystem'] = X_test['mystem'].apply(clean_emoticons)
    X_test['mystem'] = X_test['mystem'].apply(preprocess_text_lemmatize)
    X_test['mystem_nltk-stopwords'] = X_test['mystem'].apply(preprocess_text_stopwords,
                                                             setting="nltk-stopwords")
    X_test['mystem_nltk-stopwords_badwords'] = X_test['mystem_nltk-stopwords'].apply(preprocess_text_stopwords,
                                                                                     setting="badwords")
    X_test = mapper.transform(X_test)
    np_scaled = min_max_scaler.transform(X_test)
    X_test = pd.DataFrame(np_scaled)
    Ypredict = model.predict(X_test)
    print(Ypredict[0])
    return Ypredict[0]

# if __name__ == '__main__':
#     X_test = pd.read_csv('./X_test.tsv', sep="\t", header=0)
#     get_answer("mystem_nltk-stopwords_badwords_RandomForestClassifier_model.pkl", X_test)
