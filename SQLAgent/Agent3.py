
##Quelle: https://github.com/laxmimerit/Langchain-and-Ollama/blob/main/14.%20Text%20to%20MySQL%20Agent/Text%20to%20MySQL%20Agent.ipynb

from langchain_ollama import ChatOllama
from langchain_community.utilities import SQLDatabase
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langchain.agents import create_agent

import re

print("Setting up database...")

# STEP 1: DATABASE SETUP
# Connect to the database
db = SQLDatabase.from_uri('postgresql+psycopg://docker:docker@localhost/exampledb')

# Check connection and get basic info
try:
    # Test connection by getting table names
    tables = db.get_usable_table_names()
    print(f"✓ Database connected successfully")
    print(f"✓ Found {len(tables)} tables: {', '.join(tables)}")
    
except Exception as e:
    print(f"✗ Database connection failed: {e}")

# Get schema information
SCHEMA = db.get_table_info()
print("\nDatabase Schema:", SCHEMA)
print("✓ Connected to exampledb database")

# STEP 2: MODELS SETUP
llm = ChatOllama(
    model="llama3.2", 
    #model = "qwen2.5-coder",
    base_url="http://localhost:11434",
    temperature=0
)

#response = llm.invoke("Hello, how are you?")
#response.pretty_print()
print("✓ Initialized Ollama chat model")

# ============================================================================
# STEP 3: SQL TOOLS - One for each step
# ============================================================================

@tool
def get_database_schema(table_name: str = None) -> str:
    """Get database schema information for SQL query generation.
    Use this first to understand table structure before creating queries."""
    print(f"🔍 Getting schema for: {table_name if table_name else 'all tables'}")
    
    if table_name:
        try:
            # Get specific table info
            tables = db.get_usable_table_names()
            if table_name.lower() in [t.lower() for t in tables]:
                result = db.get_table_info([table_name])
                print(f"✓ Retrieved schema for table: {table_name}")
                return result
            else:
                return f"Error: Table '{table_name}' not found. Available tables: {', '.join(tables)}"
        except Exception as e:
            return f"Error getting table info: {e}"
    else:
        # Get all schema info
        print("✓ Retrieved full database schema")
        return SCHEMA

#result = get_database_schema.invoke({'table_name': 'tasks'})
#print(result)        

@tool
def generate_sql_query(question: str, schema_info: str = None) -> str:
    """Generate a SQL SELECT query from a natural language question using database schema.
    Always use this after getting schema information."""
    print(f"🔧 Generating SQL for: {question[:100]}...")
    
    # Use provided schema or get full schema
    schema_to_use = schema_info if schema_info else SCHEMA
    
    prompt = f"""
                Based on this database schema:
                {schema_to_use}

                Generate a SQL query to answer this question: {question}

                Rules:
                - Use only SELECT statements
                - Include only existing columns and tables
                - Add appropriate WHERE, GROUP BY, ORDER BY clauses as needed
                - Limit results to 10 rows unless specified otherwise
                - Use proper SQL syntax for SQLite

                Return only the SQL query, nothing else.
                """
    
    try:
        response = llm.invoke(prompt)
        query = response.content.strip()
        print(f"✓ Generated SQL query")
        return query
    except Exception as e:
        return f"Error generating query: {e}"

#query = generate_sql_query.invoke({"question": "How many tasks are there?"})
#print(query)  

@tool
def validate_sql_query(query: str) -> str:
    """Validate SQL query for safety and syntax before execution.
    Returns 'Valid: <query>' if safe or 'Error: <message>' if unsafe."""
    print(f"🔍 Validating SQL: {query[:100]}...")
    
    # Clean up the query
    clean_query = query.strip()
    
    # Remove SQL code block markers if present
    clean_query = re.sub(r'```sql\s*', '', clean_query, flags=re.IGNORECASE)
    clean_query = re.sub(r'```\s*', '', clean_query)
    clean_query = clean_query.strip().rstrip(";")
    
    # Check 1: Must be a SELECT statement
    if not clean_query.lower().startswith("select"):
        return "Error: Only SELECT statements are allowed"
    
    # Check 2: Block dangerous SQL keywords
    dangerous_keywords = ['INSERT', 'UPDATE', 'DELETE', 'ALTER', 'DROP', 'CREATE', 'TRUNCATE']
    query_upper = clean_query.upper()
    
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return f"Error: {keyword} operations are not allowed"
    
    print("✓ Query validation passed")
    return f"Valid: {clean_query}"

#result = validate_sql_query.invoke({"query": query})
#print(result)

@tool
def execute_sql_query(query: str) -> str:
    """Execute a validated SQL query and return results.
    Only use this after validating the query for safety."""
    print(f"🚀 Executing SQL: {query[:100]}...")
    
    try:
        # Clean the query
        clean_query = query.strip()
        if clean_query.startswith("Valid: "):
            clean_query = clean_query[7:]  # Remove "Valid: " prefix
        
        clean_query = re.sub(r'```sql\s*', '', clean_query, flags=re.IGNORECASE)
        clean_query = re.sub(r'```\s*', '', clean_query)
        clean_query = clean_query.strip().rstrip(";")
        
        # Execute query
        result = db.run(clean_query)
        print("✓ Query executed successfully")
       
        if result:
            return f"Query Results:\n{result}"
        else:
            return "Query executed successfully but returned no results."
            
    except Exception as e:
        error_msg = f"Execution Error: {str(e)}"
        print(f"✗ {error_msg}")
        return error_msg



#result = execute_sql_query.invoke({"query": query})
#print(result)

# ============================================================================
# STEP 4: SYSTEM PROMPT
# ============================================================================

SQL_SYSTEM_PROMPT = f"""You are an expert SQL analyst working with an employees database.

Database Schema:
{SCHEMA}

Your workflow for answering questions:
1. Use `get_database_schema` first to understand available tables and columns (if needed)
2. Use `generate_sql_query` to create SQL based on the question
3. Use `validate_sql_query` to check the query for safety and syntax
4. Use `execute_sql_query` to run the validated query
5. Provide a clear answer based on the query results

Rules:
- Always follow the workflow step by step
- Provide clear, informative answers
- Be precise with table and column names

Available tools for each step:
- get_database_schema: Get table structure info
- generate_sql_query: Create SQL from question
- validate_sql_query: Check query safety/syntax  
- execute_sql_query: Run the query

Remember: Always validate queries before executing them for safety.
"""

# ============================================================================
# STEP 5: CREATE AGENT
# ============================================================================

# All tools for the agent
tools = [
    get_database_schema,
    generate_sql_query,
    validate_sql_query, 
    execute_sql_query
]

# Create the SQL agent using create_agent
sql_agent = create_agent(
    llm, 
    tools, 
    system_prompt=SQL_SYSTEM_PROMPT
)

print("✓ Created SQL agent with create_agent")


# ============================================================================
# STEP 6: QUERY FUNCTIONS 
# ============================================================================
def ask_sql(question: str):
    """Ask the SQL agent a question using the full workflow."""
    print(f"\n{'='*60}")
    print(f"SQL AGENT - Question: {question}")
    print('='*60)
    
    for event in sql_agent.stream({"messages": question},stream_mode="values"):
        msg = event["messages"][-1]
        
        # Show tool usage
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"\n🔧 Using Tool: {tc['name']}")
                print(f"Args: {str(tc['args'])[:200]}")
        
        # Show final answer
        elif hasattr(msg, 'content') and msg.content:
            print(f"\n💬 Answer:\n{msg.content}")


ask_sql("How many tasks are completed?")


