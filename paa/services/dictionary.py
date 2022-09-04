import nltk
from nltk.corpus import stopwords
from string import digits, punctuation

# contar a quatidade vezes que cada palavra aparece no texto
def word_count(str):
    counts = dict()
    words = str.split()

    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1

    return counts
    
def remove_stopwords(text):
    text = nltk.sent_tokenize(text)
    
    for i in range(len(text)):
        words = nltk.word_tokenize(text[i])
        newwords = [word for word in words if word not in stopwords.words('portuguese')]
        text[i] = ' '.join(newwords)
    return text

def remove_numbers(text):
    remove_digits = str.maketrans('', '', digits)
    return text.translate(remove_digits)

def remove_punctuation(text):
    return text.translate(str.maketrans('', '', punctuation))

def remove_img(text):
    # as noticias sempre vem com a tag img, então vamos remover
    text = text.replace('<img src="', '')

def suit_text(text):
    text = remove_numbers(text)
    text = remove_punctuation(text)
    text = remove_stopwords(text)
    return text
    
