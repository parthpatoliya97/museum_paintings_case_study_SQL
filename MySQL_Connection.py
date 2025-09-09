from sqlalchemy import create_engine

conn_string = "mysql+pymysql://root:patricks114@localhost:3306/painting"

engine = create_engine(conn_string, pool_pre_ping=True)

try:
    conn = engine.connect()
    print("Successfully connected to MySQL database: painting")
    conn.close()
except Exception as e:
    print("Connection failed:", e)
