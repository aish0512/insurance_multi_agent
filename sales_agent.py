import os
from langchain.agents import Tool, OpenAIFunctionsAgent, AgentExecutor
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from custom_memory import CustomMemory
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')


search = DuckDuckGoSearchAPIWrapper()
search_tool = Tool(
    name="current_search",
    func=search.run,
    description="You are a sales agent. You will have a conversation with the user. Have a friendly conversation and then ask about life insurance..."
)

tools = [search_tool]

llm_sales = ChatOpenAI(model="gpt-4-1106-preview", temperature=0,openai_api_key=openai_api_key)

memory = CustomMemory(memory_key="chat_history", return_messages=True)

sales_prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="""You are a friendly sales agent having a casual conversation with a potential customer. 
    Your goal is to naturally steer the conversation towards life insurance.
    Start with general small talk and slowly introduce the topic of financial security and life insurance.
    Only suggest moving to a needs assessment when the customer shows clear interest in discussing life insurance further.
    You should not do needs assessment."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
sales_agent = OpenAIFunctionsAgent(llm=llm_sales, tools=tools, prompt=sales_prompt)

sales_agent_executor = AgentExecutor.from_agent_and_tools(
    agent=sales_agent, 
    tools=tools, 
    memory=memory,
    verbose=True
)
