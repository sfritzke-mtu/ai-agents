from sqlalchemy import create_engine, text
from sqlalchemy import insert, MetaData, Table 
import sqlalchemy
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from typing import Any, Dict, List
import re

databaseUrl = ""

FORBIDDEN_KEYWORDS = (
    "INSERT", "UPDATE", "DELETE",
    "DROP", "ALTER", "TRUNCATE", "CREATE"
)


## Besser Parser verwenden!!!
#https://pub.towardsai.net/sql-parsing-and-validation-for-llms-a-comprehensive-guide-4e33aef586cc

def validate_sql(sql: str):
    upper = sql.upper()
    if not upper.startswith(("SELECT", "WITH")):
        return {"status": "blocked", "reason": "Only SELECT allowed"}

    for kw in FORBIDDEN_KEYWORDS:
        if kw in upper:
            return {"status": "blocked", "reason": f"Forbidden keyword: {kw}"}

    return {"status": "ok", "sql": sql}

def execute_read_only_query(sql: str) -> Dict[str, Any]:
    """Execute a safe SELECT query and return columns, rows, and timing.

    Rejects any query containing write-related keywords or that does not start
    with SELECT/WITH. Rows are returned as dictionaries keyed by column name.
    """
    normalized_sql = sql.strip().rstrip(";")
    upper_sql = normalized_sql.upper()

    if not upper_sql.startswith(("SELECT")):
        raise ValueError("Only SELECT queries are permitted.")

    for keyword in FORBIDDEN_KEYWORDS:
        pattern = rf"\b{keyword}\b"
        if re.search(pattern, upper_sql):
            raise ValueError("Write operations are not allowed in read-only mode.")

    engine = create_engine(databaseUrl)

    with engine.connect() as conn:

        try:
            cursor = conn.execute(text(sql))
            rows = cursor.mappings().all()
        except SQLAlchemyError  as err:
            print("SQL execution error: %s", err)
            raise RuntimeError("SQL execution error") from err
        #duration_ms = (perf_counter() - start) * 1000

    return rows

def setupDatabase(url):
    global databaseUrl 
    databaseUrl= url
    engine = create_engine(databaseUrl)

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
