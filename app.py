from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import os
import arxiv
import chainlit as cl
from chainlit import user_session

user_env = user_session.get("env")

system_template = """Use the following pieces of context to answer the users question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
ALWAYS return a "SOURCES" part in your answer.
The "SOURCES" part should be a reference to the source of the document from which you got your answer.

Example of your response should be:

```
The answer is foo

SOURCES: 
Title: xyz 
Page Number: 1
URL: https://arxiv.org/abs/X.Y.Z
```

Begin!
----------------
{summaries}"""
messages = [
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template("{question}"),
]
prompt = ChatPromptTemplate.from_messages(messages)
chain_type_kwargs = {"prompt": prompt}


@cl.langchain_factory
def init():
    arxiv_query = None

    # Wait for the user to ask an Arxiv question
    while arxiv_query == None:
        arxiv_query = cl.AskUserMessage(
            content="Please enter a topic to begin!", timeout=15
        ).send()

    # Obtain the top 30 results from Arxiv for the query
    search = arxiv.Search(
        query=arxiv_query["content"],
        max_results=30,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    # download each of the pdfs
    pdf_data = []

    for result in search.results():
        loader = PyMuPDFLoader(result.pdf_url)
        loaded_pdf = loader.load()

        for document in loaded_pdf:
            document.metadata["source"] = result.entry_id
            document.metadata["file_path"] = result.pdf_url
            document.metadata["title"] = result.title
            pdf_data.append(document)

    # Create a Chroma vector store
    embeddings = OpenAIEmbeddings(disallowed_special=())
    docsearch = Chroma.from_documents(pdf_data, embeddings)

    # Create a chain that uses the Chroma vector store
    chain = RetrievalQAWithSourcesChain.from_chain_type(
        ChatOpenAI(
            model_name="gpt-4",
            temperature=0,
            openai_api_key=user_env.get("OPENAI_API_KEY"),
        ),
        chain_type="stuff",
        retriever=docsearch.as_retriever(),
        return_source_documents=True,
    )

    # Let the user know that the system is ready
    cl.Message(
        content=f"We found a few papers about `{arxiv_query['content']}` you can now ask questions!"
    ).send()

    return chain


@cl.langchain_postprocess
def process_response(res):
    answer = res["answer"]
    source_elements_dict = {}
    source_elements = []
    for idx, source in enumerate(res["source_documents"]):
        title = source.metadata["title"]

        if title not in source_elements_dict:
            source_elements_dict[title] = {
                "page_number": [source.metadata["page"]],
                "url": source.metadata["file_path"],
            }

        else:
            source_elements_dict[title]["page_number"].append(source.metadata["page"])

        # sort the page numbers
        source_elements_dict[title]["page_number"].sort()

    for title, source in source_elements_dict.items():
        # create a string for the page numbers
        page_numbers = ", ".join([str(x) for x in source["page_number"]])
        text_for_source = f"Page Number(s): {page_numbers}\nURL: {source['url']}"
        source_elements.append(
            cl.Text(name=title, text=text_for_source, display="inline")
        )

    cl.Message(content=answer, elements=source_elements).send()
