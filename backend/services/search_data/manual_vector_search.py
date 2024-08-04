from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from glob import glob


def create_vector_store():
    """Create a vector store from PDF files in the specified folder."""

    pdf_files = glob("./data/QA/*.pdf")
    all_docs = []

    for pdf_file in pdf_files:
        loader = PyPDFLoader(pdf_file)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs = text_splitter.split_documents(documents)
        all_docs.extend(docs)

    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(all_docs, embeddings)

    return vector_store


def search_vector_store(query, vector_store):
    """Search the vector store for similar documents based on the given query."""

    results_with_scores = vector_store.similarity_search_with_score(
        query, k=3, search_type="hybrid"
    )
    # print the each result
    # for result, score in results_with_scores:
        # print(f"result: {result}")
        # print(f"score: {score}")
        # print("-------------------------------------------------------------")

    return (
        results_with_scores
        if results_with_scores
        else "No relevant error handling method found."
    )
    # if results_with_scores:
    #     # Debug: Print a message if results are found
    #     print("Results found, returning them.")
    #     return results_with_scores
    # else:
    #     # Debug: Print a message if no results are found
    #     print("No results found, returning default message.")
    #     return "No relevant error handling method found."
