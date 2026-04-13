#install psycopg
#install psycopg-binary
import psycopg
from sqlalchemy import create_engine
from sqlalchemy import insert, MetaData, Table 
import sqlalchemy
from sqlalchemy import text

#pip install langchain
#pip install langchain-openai

from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit


#docker compose -up d database adminer

engine = create_engine('postgresql+psycopg://docker:docker@localhost/exampledb')

# Define custom table info for better LLM context
# custom_table_info = {
#     "tasks": (
#         "A table of tasks.\n"
#         "- id (SERIAL PRIMARY KEY): Unique ID of task\n"
#         "- task (TEXT): Description of the task\n"
#         "- completed (BOOLEAN): Flag of task. True if the task are completed. False if the task are not completed.\n"
#         "- completion_date (DATE): Date of the completed task\n"
#         "- priority (INTEGER): Number of the priority. Low Number means low priority\n"
#     )
# }


#Langchain SQLAgent
#https://github.com/EliasK93/LangChain-SQL-Agent-for-dynamic-data-visualization/blob/master/agent_tools.py

def setupDatabase():
    with engine.connect() as conn:

        if not sqlalchemy.inspect(engine).has_table("tasks"):
            print("Creating tasks table...")

            conn.execute(text('''CREATE TABLE IF NOT EXISTS tasks
                    (id SERIAL PRIMARY KEY,
                    task TEXT NOT NULL,
                    completed BOOLEAN,
                    due_date DATE,
                    completion_date DATE,
                    priority INTEGER)'''))
            
            # Insert sample tasks into the tasks table
            print("Inserting sample tasks ...")

            conn.commit()
            
            metadata = MetaData()
            tasks = Table('tasks', metadata, autoload_with=engine)

            stmt = insert(tasks).values(task='Complete the web page design', completed=True, due_date = '2023-05-01', completion_date='2023-05-03', priority = 1)
            result = conn.execute(stmt)
            
            stmt = insert(tasks).values(task='Create login and signup pages', completed=True, due_date = '2023-05-03', completion_date='2023-05-05', priority = 2)
            result = conn.execute(stmt)

            stmt = insert(tasks).values(task='Product management', completed=False, due_date = '2023-05-05', priority = 3)
            result = conn.execute(stmt)

            stmt = insert(tasks).values(task='Cart and wishlist creation', completed=False, due_date = '2023-05-08', priority = 4)
            result = conn.execute(stmt)

            stmt = insert(tasks).values(task='Payment gateway integration', completed=False, due_date = '2023-05-10', priority = 5)
            result = conn.execute(stmt)

            stmt = insert(tasks).values(task='Order management', completed=False, due_date = '2023-05-10', priority = 6)
            result = conn.execute(stmt)
            
            conn.commit()
        else:
            print("tasks table already exists!")



setupDatabase()


db = SQLDatabase.from_uri("postgresql+psycopg://docker:docker@localhost:5432/exampledb")

print(f"Dialect: {db.dialect}")
print(f"Available tables: {db.get_usable_table_names()}")
print(f'Sample output: {db.run("SELECT * FROM tasks LIMIT 5;")}')


#Initialize the LLM
llm = ChatOpenAI(
    model = "llama3.2",
    #model = "qwen2.5-coder",
    base_url='http://localhost:11434/v1/',
    api_key='ollama'  # required but ignored   
    #model='gpt-4o-mini',
    #temperature=0
)


system_prompt = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.

Then you should query the schema of the most relevant tables.
""".format(
    dialect=db.dialect,
    top_k=5,
)

#Initialize the Agent
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=SQLDatabaseToolkit(db=db, llm=llm),
    verbose=True,
    #agent_type="tool-calling"
    #agent_type = "openai-tools",
    agent_type = "zero-shot-react-description"
    #system_prompt=system_prompt
)

answer = agent_executor.invoke({"How many tasks are there?"})["output"]

print(answer)
