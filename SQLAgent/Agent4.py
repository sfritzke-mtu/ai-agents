### Dieser SQL Agent funktioniert!!!
##https://www.youtube.com/watch?v=YXDA4kfW_Dg


from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

import psycopg

db = SQLDatabase.from_uri("postgresql+psycopg://docker:docker@localhost:5432/exampledb", sample_rows_in_table_info=0)

def get_schema(_):
    return db.get_table_info()

def run_query(query):
    print(f'Query being run: {query} \n\n')
    return db.run(query)

print(get_schema(''))

def get_llm():
    
    return ChatOpenAI(
        model = "llama3.2",
        base_url='http://localhost:11434/v1/',
        api_key='ollama',  # required but ignored   
        temperature=0.0
    )    


def write_sql_query(llm):
    template = """Based on the table schema below, write a SQL query that would answer the user's question:
    {schema}

    Question: {question}
    SQL Query:"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Given an input question, convert it to a SQL query. No pre-amble. "
            "Please do not return anything else apart from the SQL query, no prefix aur suffix quotes, no sql keyword, nothing please"),
            ("human", template),
        ]
    )

    return (
        RunnablePassthrough.assign(schema=get_schema)
        | prompt
        | llm
        | StrOutputParser()
    )

def answer_user_query(query, llm):
    template = """Based on the table schema below, question, sql query, and sql response, write a natural language response:
    {schema}

    Question: {question}
    SQL Query: {query}
    SQL Response: {response}"""

    prompt_response = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Given an input question and SQL response, convert it to a natural language answer. No pre-amble.",
            ),
            ("human", template),
        ]
    )

    full_chain = (
        RunnablePassthrough.assign(query=write_sql_query(llm))
        | RunnablePassthrough.assign(
            schema=get_schema,
            response=lambda x: run_query(x["query"]),
        )
        | prompt_response
        | llm
    )

    return full_chain.invoke({"question": query})

#Liefert nur die SQL-Query
#query=write_sql_query(get_llm())
#response = query.invoke({"question": query})
#print(response)

#query = 'How many tasks are there?'
#query = 'How many completed tasks are there?'
#query = 'How many incompleted tasks are there?'
#query = 'Give me the name of 3 incompleted tasks'
query = 'Give me the name of 3 tasks with priority > 4'
response = answer_user_query(query, llm=get_llm())
print(response.content)

