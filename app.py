import os
from pandas as pd
import streamlit as st
from openai import OpenAI
from elasticsearch import Elasticsearch

client = OpenAI(api_key=st.secrets["api_key"])

# https://www.elastic.co/search-labs/tutorials/install-elasticsearch/elastic-cloud#finding-your-cloud-id
ELASTIC_CLOUD_ID = st.secrets["elastic_cloud_key"]

# https://www.elastic.co/search-labs/tutorials/install-elasticsearch/elastic-cloud#creating-an-api-key
ELASTIC_API_KEY = st.secrets["elastic_api_key"]

es = Elasticsearch(
  cloud_id = ELASTIC_CLOUD_ID,
  api_key=ELASTIC_API_KEY
)

# Test connection to Elasticsearch
print(client.info())


st.title("Kevin의 위키피디아 AI 검색기(RAG)")

with st.form("form"):
    question = st.text_input("Prompt")
    submit = st.form_submit_button("Submit")

with st.spinner("Waiting for Kevin AI..."):
    question = question.replace("\n", " ")
    question_embedding = client.embeddings.create(input = [text], model="text-embedding-ada-002").data[0].embedding
  
    response = es.search(
      index = "wikipedia_vector_index",
      knn={
          "field": "content_vector",
          "query_vector":  question_embedding,
          "k": 10,
          "num_candidates": 100
        }
    )
    
    top_hit_summary = response['hits']['hits'][0]['_source']['text'] # Store content of top hit for final step
    
    summary = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Answer the following question in Korean.:"
             + question
             + "by using the following text:"
             + top_hit_summary},
        ]
    )

    choices = summary.choices
  
    for choice in choices:
      st.write(choice)