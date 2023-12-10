import unicodedata
import re

def _customImplementation(self, text):

    text = text.lower()
    text = re.sub(r'[^\w\s]',' ', text)
    text = self.unicodetext(text)
    text = ' '.join(word for word in text.split())
    return text
 
def unicodetext(text):
    text = unicodedata.normalize('NFD', text)
    text = re.sub(r'[\u0300\u0301\u0308]',  '',  text)
    text = unicodedata.normalize( 'NFC', text)
    return text.lower()