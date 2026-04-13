#Quelle: https://www.youtube.com/watch?v=xG3ubpRnFnw

##---> Funktioniert nicht so zuverlässig

from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI

db = SQLDatabase.from_uri("postgresql+psycopg://docker:docker@localhost:5432/exampledb")

#Initialize the LLM
llm = ChatOpenAI(
    model = "llama3.2",
    base_url='http://localhost:11434/v1/',
    api_key='ollama'  # required but ignored   
)

toolkit = SQLDatabaseToolkit(db = db, llm =llm)

tools = toolkit.get_tools()
for tool in tools:
     print(f"{tool.name}: {tool.description}\n")

#deprecated
#from langgraph.prebuilt import create_react_agent 
from langchain.agents import create_agent

system_prompt = """
You are an agent designed to interact with a SQL database.
Give an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query an return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting 
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query an try again.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.

Then you should query the schema of the most relevant tables.
""".format(
    dialect=db.dialect, 
    top_k =5
)

agent = create_agent(llm, tools, system_prompt=system_prompt)

#question = "How many tasks are there?"
question = 'How many completed tasks are there?'

for step in agent.stream({"messages" :[{"role" : "user", "content" : question}]}, stream_mode="values"):
    step["messages"][-1].pretty_print()