import string
import re
from collections import Counter
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from nltk.tokenize import word_tokenize
import secrets


colors = ["hsv", 'viridis', 'cividis', 'magma', 'Purples', 'Blues', 'YlOrRd','YlGnBu', 'bone', 'copper', 'Spectral', 'seismic', 'twilight','tab20c','prism','cubehelix' ]
background = ['white', 'black']

def make_stopwords(string):
    lst = []
    for i in string.split():
        if i not in lst:
            lst.append(i)
    return lst

sss = """ “ ’ ” № « » і та щодо у п в во не ні що я ти він вона на с з як а то всі так його але так до к же ви за би по тільки її мені було ось від мене ще ні о йому тепер коли навіть ну навпаки лі якби вже або ні був бути нього до вас колись небудь знов знову вам там потім себе нічого їй може вони тут де є треба неї ней для ми тебе їх чим була сам щоб без чого раз еж собі під буде ж тоді хто цей того потім цього який зовсім ним тут цим один майже мій тим щоб неї зараз були куди нащо для чого всіх ніколи можно можна при нарешті два об інший хоч хоча б після над більше той через ці нас про всього них яка багато чи три цю моя алеж проте добре хорошо гарно свою цій перед іноді краще чуть трохи тім не можна такий їм більш більше завжди авжеж всю між"""
stopwords_ukraine = make_stopwords(sss)
s_rada = """ україни ради рада верховної комітет ст. I. ІІ. 1. 2. комітету законопроєкту верховна закону законом закона законів постанови статті стаття статтю вважає"""
stopwords_rada = make_stopwords(s_rada)
stopwords = set(stopwords_ukraine + stopwords_rada +list(string.punctuation))

def process(doc):
    doc_token = word_tokenize(doc.lower())
    filtered_text = [w for w in doc_token if not w in stopwords]
    dictionary=Counter(filtered_text)
    return dictionary

def img(doc, name):
    cloud1 = WordCloud(
        width=1200, height=800,
        colormap=secrets.choice(colors),
        max_font_size=400,
        margin=3,
        stopwords=stopwords,
        background_color=secrets.choice(background),
        mode="RGB",
        max_words=1000
        ).generate_from_frequencies(doc)
    cloud1.to_file(f'o{name}.jpg')
    # plt.figure(figsize=[6.33,3.07], dpi = 400)
    # plt.imshow(cloud1 ,interpolation='bilinear')
    # plt.axis('off')
    # plt.savefig(f'{name}.jpg', format='jpg', dpi = 400)
    
def bill_picture(doc, name):
    try:
        dictionary = process(doc)
        img(dictionary, name)
        print('complete')
    except LookupError:
        import nltk
        nltk.download('punkt')
        bill_picture(doc)