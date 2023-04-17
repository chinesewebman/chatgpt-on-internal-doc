import os
import re

from gpt_index import Document, SimpleDirectoryReader

def load_buddha_dict(dict_path='buddha-dict.txt'):
    with open(dict_path, 'r', encoding='utf-8') as f:
        words = f.read().splitlines()
    return words

def add_space_around_words(text, words):
    for word in words:
        text = text.replace(word, f' {word} ')
    return text
def merge_consecutive_spaces(text):
    return re.sub(r'\s+', ' ', text)

def refine_doc(directory_path, output_dir='output'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    reader = SimpleDirectoryReader(directory_path)
    documents = reader.load_data()
    refined_documents = []

    add_space_after = '，。、：”？！；》】）'
    add_space_before = '“《【（'
    buddha_dict = load_buddha_dict()

    for i, doc in enumerate(documents):
        if isinstance(doc, Document):
            doc = str(doc)
        for char in add_space_after:
            doc = doc.replace(char, char + ' ')

        for char in add_space_before:
            doc = doc.replace(char, ' ' + char)

        doc = add_space_around_words(doc, buddha_dict)
        doc = merge_consecutive_spaces(doc)
        refined_documents.append(doc)

        #with open(os.path.join(output_dir, f'output{i+1}.txt'), 'w', encoding='utf-8') as f:
        #    f.write(doc)

    return refined_documents

# 使用函数
refined_docs = refine_doc('input')
