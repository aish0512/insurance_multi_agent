import os
from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from pydantic import BaseModel
from docx import Document
from custom_memory import CustomMemory
from langchain.tools import StructuredTool
import traceback
from dotenv import load_dotenv
load_dotenv()

class ProductRecommendationInput(BaseModel):
    query: str

def extract_text_from_file(file_path):
    doc = Document(file_path)
    full_text = [para.text for para in doc.paragraphs]
    return '\n'.join(full_text)

def create_knowledge_base(text):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_text(text)
    embeddings = OpenAIEmbeddings()
    knowledge_base = FAISS.from_texts(texts, embeddings)
    return knowledge_base

openai_api_key = os.getenv('OPENAI_API_KEY')

text_file_path = "MBAL - UL limited pay - TnC - EN - clean.docx"
document_text = extract_text_from_file(text_file_path)
knowledge_base = create_knowledge_base(document_text)

llm = ChatOpenAI(temperature=0)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=knowledge_base.as_retriever()
)

product_recommendation_tool = StructuredTool(
    name="Document_QA_System",
    func=qa_chain.run,
    description="Useful for answering questions about the document.",
    args_schema=ProductRecommendationInput
)

product_memory = CustomMemory(memory_key="chat_history", return_messages=True)

product_prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="""You are an AI assistant helping users with life insurance recommendations. 
    After receiving the assessment details from the Needs Assessment Agent, you will provide a recommendation on the type of life insurance that might be suitable for the user, referencing the relevant parts of the document.
    After providing the recommendation, ask the user if they would like to know more about the product.
    If they are interested, prompt them to ask any questions they might have about the product.
    Once you have answered all their questions, politely ask for their contact number so that a live agent can reach out to them for further assistance.
    If the user indicates they are not interested, thank them for their time and offer assistance with any other queries they may have.
    If the user does not respond clearly, gently encourage them to respond with 'yes' or 'no' to continue the conversation."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

product_agent = OpenAIFunctionsAgent(llm=llm, tools=[product_recommendation_tool], prompt=product_prompt)

product_agent_executor = AgentExecutor.from_agent_and_tools(
    agent=product_agent, 
    tools=[product_recommendation_tool], 
    memory=product_memory,
    verbose=True
)

# def handle_product_recommendation(needs_summary):
#     try:
#         refined_query = (
#             f"Based on the following needs assessment, "
#             f"recommend a suitable life insurance product from the document: {needs_summary}. "
#         )
        
#         response = product_agent_executor.run(input={"query": refined_query})
#         print("Product Recommendation Agent:", response)
        
#         while True:
#             user_input = input("You: ").strip().lower()
            
#             if user_input in ['no', 'n']:
#                 print("Product Recommendation Agent: Thank you for your time. To help you further, can I have your contact number so that a live agent can reach out to you?")
#                 contact_number = input("You: ")
#                 print(f"Product Recommendation Agent: Thank you! A live agent will contact you shortly at {contact_number}.")
#                 break

#             elif user_input in ['yes', 'y']:
#                 user_query = input("You: Please ask your question about the product: ")
#                 answer = product_agent_executor.run(input={"query": user_query})
#                 print("Product Recommendation Agent:", answer)
#                 print("Product Recommendation Agent: Would you like to ask anything else about the product? (yes/no)")
            
#             else:
#                 print("Product Recommendation Agent: Please respond with 'yes' or 'no'.")

def handle_product_recommendation(needs_summary):
    try:
        refined_query = (
            f"Based on the following needs assessment, "
            f"recommend a suitable life insurance product from the document: {needs_summary}. "
        )
        
        response = product_agent_executor.run(input={"query": refined_query})
        return response
    except Exception as e:
        print("An error occurred in product recommendation:")
        traceback.print_exc()
        return "I apologize, but I encountered an error while processing your request. Please try again or contact customer support for assistance."

def process_product_query(query):
    try:
        answer = product_agent_executor.run(input={"query": query})
        return answer
    except Exception as e:
        print("An error occurred while processing the query:")
        traceback.print_exc()
        return "I apologize, but I encountered an error while processing your request. Please try again or contact customer support for assistance."

    # except Exception as e:
    #     print("An error occurred in product recommendation:")
    #     traceback.print_exc()
    #     return "I apologize, but I encountered an error while processing your request. Please try again or contact customer support for assistance."
