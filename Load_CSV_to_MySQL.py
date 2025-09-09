import pandas as pd
from sqlalchemy import create_engine
import os

conn_string = "mysql+mysqlconnector://root:patricks114@localhost:3306/painting"
db = create_engine(conn_string)
conn = db.connect()

folder_path = r"F:\paintings_data"

for file in os.listdir(folder_path):
    if file.endswith(".csv"):
        table_name = os.path.splitext(file)[0]  
        file_path = os.path.join(folder_path, file)

            df = pd.read_csv(file_path)

        df.to_sql(table_name, con=conn, if_exists='replace', index=False)

        print(f"{file} uploaded successfully into table '{table_name}'")
