import streamlit as st

from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.vectorstores import Chroma
from langchain.llms import GPT4All, LlamaCpp
import os

load_dotenv()

embeddings_model_name = os.environ.get("EMBEDDINGS_MODEL_NAME")
persist_directory = os.environ.get('PERSIST_DIRECTORY')

model_type = os.environ.get('MODEL_TYPE')
model_path = os.environ.get('MODEL_PATH')
model_n_ctx = os.environ.get('MODEL_N_CTX')

from constants import CHROMA_SETTINGS

def run_app():
    st.title("Private GPT: Ask questions to your documents without an internet connection, using the power of LLMs.")
    query = st.text_input("Enter your question:")
    hide_source = st.checkbox("Hide source documents")
    mute_stream = st.checkbox("Mute streaming StdOut callback for LLMs")

    if st.button("Submit"):
        main(query, hide_source, mute_stream)

def main(query, hide_source, mute_stream):
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, client_settings=CHROMA_SETTINGS)
    retriever = db.as_retriever()
    callbacks = [] if mute_stream else [StreamingStdOutCallbackHandler()]

    match model_type:
        case "LlamaCpp":
            llm = LlamaCpp(model_path=model_path, n_ctx=model_n_ctx, callbacks=callbacks, verbose=False)
        case "GPT4All":
            llm = GPT4All(model=model_path, n_ctx=model_n_ctx, backend='gptj', callbacks=callbacks, verbose=False)
        case _default:
            print(f"Model {model_type} not supported!")
            exit;
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents= not hide_source)

    res = qa(query)
    answer, docs = res['result'], [] if hide_source else res['source_documents']

    st.subheader("Question:")
    st.write(query)
    st.subheader("Answer:")
    st.write(answer)

    if not hide_source:
        st.subheader("Relevant Sources:")
        for document in docs:
            st.write(f"> {document.metadata['source']}:")
            st.write(document.page_content)

if __name__ == "__main__":
    run_app()
