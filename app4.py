import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_ollama.llms import OllamaLLM

data  ={
    "Product" : ["Laptop", "Monitor", "Mouse" , "Keyboard", "Headset"],
    "Price"  : [1200, 300, 25, 45, 150],
    "Units_Sold" :[100, 150, 200, 160, 130],
    "Salesperson" :["Alice", "Bob", "Alice", "David", "Jack"] 
} 

df = pd.DataFrame(data)

# Initialize the Chat Model (LLM)
model = OllamaLLM(model="qwen2.5-coder", temperatur = "0.0") # A temperature of 0 would make the model completely deterministic, always choosing the most likely token.

# Create a Pandas DataFrame Agent
agent = create_pandas_dataframe_agent(
    model,
    df,
    verbose=True,
    allow_dangerous_code=True,  # Allows execution of complex pandas operations
    agent_executor_kwargs={"handle_parsing_errors": True}  # Handles any parsing errors
)

# Example Query
response = agent.invoke("What are the total price by Salesperson")
#response = agent.invoke("Wie lautet die Summe von price by Salesperson")
print(response)