# https://github.com/py-pdf/PyPDF2
from PyPDF2 import PdfReader

# https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
# By default, input text longer than 256 word pieces is truncated.
from sentence_transformers import SentenceTransformer, util

import params
import os
from pymongo import MongoClient

# Importing all the functions defined in utils.py
from utils import *
import re

# Establish connections to MongoDB
mongo_client = MongoClient(params.mongodb_conn_string)
result_collection = mongo_client[params.database][params.collection]

# Empty the collection (Don't delete it to preserve the Search index)
result_collection.delete_many({})

files = []
pdfDir = "PDFs"
for pdf in os.listdir(pdfDir):

    print("Reading:", pdf)
    reader = PdfReader(pdfDir+"/"+pdf)
    number_of_pages = len(reader.pages)

    # Load the model
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    print("Encoding", number_of_pages, "pages...")

    for page_number in range(number_of_pages):
        print(page_number+1)
        # turn the page into an array of sentences

        page = reader.pages[page_number]

        text = page.extract_text()
        sentences = split_into_sentences(text)
        # print(sentences)

        # A placeholder for the result doc
        result_doc = {}

        for sentence in sentences:
            # Ignore sentences that are not properly extracted
            if (not re.search("^[a-zA-Z]\s[a-zA-Z]\s", sentence)):

                sentence_vector = model.encode(sentence).tolist()
                result_doc['pdf'] = pdf
                result_doc['page'] = page_number
                result_doc['sentence'] = sentence
                result_doc['sentenceVector'] = sentence_vector
                result = result_collection.insert_one(result_doc.copy())
