import os
from dotenv import load_dotenv
from Database import setupDatabase, validate_sql, execute_read_only_query

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from pydantic import BaseModel, Field
from typing import List 

from langchain_core.output_parsers import PydanticOutputParser

class SQLResponse(BaseModel):
    sql: str = Field(description="AI Answer as SQL query")
    confidence: float



def get_allowed_schema():
    return """
    CREATE TABLE tasks
            (id SERIAL PRIMARY KEY,
            task TEXT NOT NULL COMMENT 'Naming of the task',
            completed BOOLEAN,
            due_date DATE,
            completion_date DATE,
            priority INTEGER,
            abc TEXT NOT NULL COMMENT 'Description of the task')
    """



load_dotenv()

setupDatabase('postgresql+psycopg://docker:docker@localhost/exampledb')

llm = ChatOllama(model = os.getenv("MODEL"), api_key =  os.getenv("API_KEY"), temperature = 0)

#Test llm
#out = llm.invoke("Was ist die Hauptstadt von DE?")
#print(out.content)



# Prompt definieren

parser = PydanticOutputParser(pydantic_object=SQLResponse)

prompt = ChatPromptTemplate.from_template(
"""
Du bist ein PostgreSQL-Experte.

Gegeben ist folgendes Datenbankschema:
{schema}

Wandle die folgende Anfrage in SQL um:
Anfrage: {question}

Gib NUR die SQL-Abfrage zurück, ohne Erklärung.
{format_instructions}
"""
)

#print(parser.get_format_instructions())


# User Input
frage = "Zeige alle tasks mit priority > 3" # OK
frage = "Wie viele tasks sind vorhanden?" # OK
frage = "Wie viele tasks sind vorhanden, die bereits beendet wurden?" # OK
#SELECT COUNT(*) AS number_of_completed_tasks
#FROM tasks
#WHERE completed = TRUE;
frage = "Welche tasks wurden bis zum 2023-05-05 erledigt? " # OK
#SELECT *  
#FROM tasks  
#WHERE completed = TRUE  
#AND completion_date <= DATE '2023-05-05';
frage = "Welche tasks müssen bis zum 2023-05-05 erledigt werden? " #OK
#SELECT * FROM tasks
#WHERE due_date <= '2023-05-05'
#  AND completed != TRUE;

frage ="Zeige mir die Beschreibung alle beendet tasks" # OK
#SELECT abc FROM tasks WHERE completed = TRUE;
#--> Funktioniert wenn über COMMENT die Column erklärt wird

frage ="Zeige mir die Bezeichnung alle beendet tasks" # OK
# --> zeigt abc als spalte nicht tasks --> Nach dem Kommentar in tasks, wird die Column task angezeigt
#```sql
#SELECT task
#FROM tasks
#WHERE completed;
#```

frage ="Zeige mir alle tasks die seit 7 Tage beendet wurden"  #OK
#SELECT * 
#FROM tasks 
#WHERE completed = TRUE 
#  AND completion_date >= current_date - INTERVAL '7 days';

frage ="Zeige mir alle tasks die seit 3 Jahren beendet wurden"  #OK

# Chain bauen

chain = prompt | llm | parser     

# SQL generieren
response = chain.invoke({"schema": get_allowed_schema(), "question": frage, "format_instructions": parser.get_format_instructions()})


print(response.sql)
print(validate_sql(response.sql))

rows = execute_read_only_query(response.sql)

for row in rows:
    print(row)
#print(len(rows))
#[{'count': 2}]

