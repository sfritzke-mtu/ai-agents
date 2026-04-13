from openai import OpenAI
import pandas as pd 

def get_primer(df_dataset,df_name):
    # Primer function to take a dataframe and its name
    # and the name of the columns
    # and any columns with less than 20 unique values it adds the values to the primer
    # and horizontal grid lines and labeling
    primer_desc = "Use a dataframe called df from data_file.csv with columns '" \
        + "','".join(str(x) for x in df_dataset.columns) + "'. "
    for i in df_dataset.columns:
        if len(df_dataset[i].drop_duplicates()) < 20 and df_dataset.dtypes[i]=="O":
            primer_desc = primer_desc + "\nThe column '" + i + "' has categorical values '" + \
                "','".join(str(x) for x in df_dataset[i].drop_duplicates()) + "'. "
        elif df_dataset.dtypes[i]=="int64" or df_dataset.dtypes[i]=="float64":
            primer_desc = primer_desc + "\nThe column '" + i + "' is type " + str(df_dataset.dtypes[i]) + " and contains numeric values. "   
    primer_desc = primer_desc + "\nLabel the x and y axes appropriately."
    primer_desc = primer_desc + "\nAdd a title. Set the fig suptitle as empty."
    primer_desc = primer_desc + "{}" # Space for additional instructions if needed
    primer_desc = primer_desc + "\nUsing Python version 3.9.12, create a script using the dataframe df to graph the following: "
    pimer_code = "import pandas as pd\nimport matplotlib.pyplot as plt\n"
    pimer_code = pimer_code + "fig,ax = plt.subplots(1,1,figsize=(10,4))\n"
    pimer_code = pimer_code + "ax.spines['top'].set_visible(False)\nax.spines['right'].set_visible(False) \n"
    pimer_code = pimer_code + "df=" + df_name + ".copy()\n"
    return primer_desc,pimer_code

# chat_completion = client.chat.completions.create(
#     messages=[
#         {
#             'role': 'user',
#             'content': 'Say this is a test',
#         }
#     ],
#     model='gpt-4o-mini',
# )
# print(chat_completion.choices[0].message.content)

data  ={
    "Product" : ["Laptop", "Monitor", "Mouse" , "Keyboard", "Headset"],
    "Price"  : [1200, 300, 25, 45, 150],
    "Units_Sold" :[100, 150, 200, 160, 130],
    "Salesperson" :["Alice", "Bob", "Alice", "David", "Jack"] 
} 

df = pd.DataFrame(data)

primer1,primer2 = get_primer(df,'product_sales.csv') 

print(primer1)
print(primer2)