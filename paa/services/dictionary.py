import nltk
import math
import re
nltk.download("punkt")
nltk.download("stopwords")
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from string import digits, punctuation

# contar a quatidade vezes que cada palavra aparece no texto
def get_word_count(str):
    counts = {}
    words = str.split()

    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1

    return counts

def get_word_frequency(word_count):
    word_frequency = {}
    
    for word, count in word_count.items():
        word_frequency[word] = math.sqrt(count)

    return word_frequency

def get_text_length_norm(text_length):
    return 1 / math.sqrt(text_length)

def get_tags_weight(text):
    word_count = get_word_count(text)
    word_frequency = get_word_frequency(word_count)

    text_length = len(text)
    text_length_norm = get_text_length_norm(text_length)


    weight = {}
    for word, frequency in word_frequency.items():
        weight[word] = frequency * text_length_norm

    return weight
    
def remove_stopwords(text):
    text_tokens = word_tokenize(text, language='portuguese')
    tokens_without_sw = [word for word in text_tokens if (not word in stopwords.words('portuguese') and len(word) > 2)]
    return " ".join(tokens_without_sw)

def remove_numbers(text):
    remove_digits = str.maketrans('', '', digits)
    return text.translate(remove_digits)

def remove_punctuation(text):
    return text.translate(str.maketrans('', '', punctuation))

def remove_img(text):
    # as noticias sempre vem com a tag img, então vamos remover
    text = re.sub(r'<img.+\/>', "", text)
    return text

def to_lower_case(text):
    return text.lower()

def suit_text(text):
    text = remove_img(text);
    text = remove_numbers(text)
    text = remove_punctuation(text)
    text = to_lower_case(text)
    text = remove_stopwords(text)
    return text
    
