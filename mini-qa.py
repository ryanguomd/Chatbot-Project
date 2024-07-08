import os
import sys
import openai
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain_community.document_loaders import JSONLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper


# User-Defined Variables
os.environ["OPENAI_API_KEY"] = 'your_open_ai_key'  # Set your OpenAI API key here
json_file_path = '../configurations/kiosk_conf.json'  # Path to your JSON file 'AI_assistant/llm-observatory-conf-kit/configurations/kiosk_conf.json
model_version = 'gpt-3.5-turbo'  # Model version for ChatOpenAI

# Check for command line input
query = None
if len(sys.argv) > 1:
    query = sys.argv[1]

# Enable to save to disk & reuse the model (for repeated queries on the same data)
PERSIST = False

if PERSIST and os.path.exists("persist"):
    print("Reusing index...\n")
    vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
    index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
    # Load the JSON file
    # Set text_content to False (default is True) because input is not in string format.
    loader = JSONLoader(json_file_path, jq_schema=".modules", content_key= None, text_content= False)  # Adjust jq_schema and content_key according to your JSON structure
    if PERSIST:
        index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory": "persist"}).from_loaders([loader])
    else:
        index = VectorstoreIndexCreator().from_loaders([loader])

# Setup of the ConversationalRetrievalChain
# Incorporating the suggestion to change top_k_docs_for_context to k:10
chain = ConversationalRetrievalChain.from_llm(
    llm=ChatOpenAI(model=model_version),
    retriever=index.vectorstore.as_retriever(search_kwargs={"k": 10})
)
chat_history = []
while True:
    if not query:
        query = input("Prompt:")
    if query in ['quit', 'q', 'exit']:
        sys.exit()
    result = chain({"question": query, "chat_history": chat_history})
    print(result['answer'])

    chat_history.append((query, result['answer']))
    query = None