# https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
from sentence_transformers import SentenceTransformer, util
import params
from pymongo import MongoClient
import argparse

# Process arguments
parser = argparse.ArgumentParser(description='Atlas Vector Search PDF Demo')
parser.add_argument('-q', '--question', help="The question to ask")
args = parser.parse_args()

if args.question is None:
    # Some questions to try...
    query = "Where can I find training?"
    query = "Does MongoDB support visualizations?"
    query = "How do I build an Operational Data Layer?"
    query = "How can I create a single view of my customer?"
    query = "How can I build a microservice?"
    query = "Can I query data in AWS S3?"

else:
    query = args.question

# Load the model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Show the default question if one wasn't provided:
if args.question is None:
    print("\nYour question:")
    print("--------------")
    print(query)

# Encode our question
query_vector = model.encode(query).tolist()

# Establish connections to MongoDB
mongo_client = MongoClient(params.mongodb_conn_string)
result_collection = mongo_client[params.database][params.collection]

desired_answers = 3

pipeline = [
    {
        "$search": {
            "knnBeta": {
                "vector": query_vector,
                "path": "sentenceVector",
                "k": 15
            }
        }
    },
    {
        "$limit": desired_answers
    }
]

results = result_collection.aggregate(pipeline)

print("\nThe following PDFs may contain the answers you seek:")
print("----------------------------------------------------")

for result in results:

    print("PDF:     ", result['pdf'])
    print("Page:    ", result['page']), "\n)"
    print("Sentence:", result['sentence'], "\n")
