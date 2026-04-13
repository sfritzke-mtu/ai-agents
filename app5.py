#Wichtig: PandasAI läuft mit Python 3.11, library liteLLM lässt sich nicht auf Python 3.12 installieren!!
from pandasai import pandasAI
#Error: numpy.dtype size changed, may indicate binary incompatibility. Expected 96 from C header, got 88 from PyObject
#Lösung: This worked for me for those looking for the command it's: "pip uninstall numpy" followed by "pip install numpy==1.26.4"


from openai import OpenAI

client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',  # required but ignored
)


data  ={
    "Product" : ["Laptop", "Monitor", "Mouse" , "Keyboard", "Headset"],
    "Price"  : [1200, 300, 25, 45, 150],
    "Units_Sold" :[100, 150, 200, 160, 130],
    "Salesperson" :["Alice", "Bob", "Alice", "David", "Jack"] 
} 

pandas_ai = PandasAI(client)
df = pai.DataFrame(data)

df.chat("What are the total price by Salesperson")