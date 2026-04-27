import pyodbc
from datetime import date

import os
import pandas as pd
import pyodbc

DB_CONNECTION_STRING = ""

process_date = date.today()



def insert_one_row(data_dict):
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO OEM_Websites_data (
            [Vehicle Type (m/c or s/c or EV)],
            OEM_Name,
            Model_Name,
            Engine_Displacement,
            Variant,
            State_Name,
            City_Name,
            Ex_Showroom_Price,
            On_Road_Price,
            Process_Date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        row = [
                data_dict.get("Vehicle_type"),     # Vehicle Type
                data_dict.get("OEM_name"),          # OEM_Name
                data_dict.get("Model_Name"),       # Model_Name
                data_dict.get("Engine_Displacement"),                              # Engine_Displacement 
                data_dict.get("Variant"),          # Variant
                data_dict.get("State"),            # State_Name
                None,                              # City_Name (not in dict)
                data_dict.get("Ex_Showroom_Price"),
                data_dict.get("On_Road_Price"),
                process_date
            ]

        cursor.execute(insert_query, row)
        conn.commit()

        cursor.close()
        conn.close()

        print("Row inserted into DB")

    except Exception as e:
        print(f"DB Insert Error: {e}")



def fetch_data_today(excel_filename):
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)

        query = """
        SELECT *
        FROM OEM_Websites_data
        WHERE OEM_Name = ?
          AND CAST(Process_Date AS DATE) = ?
        """

        # 🔹 Just change values here when needed
        # df = pd.read_sql(
        #     query,
        #     conn,
        #     params=('Royal Enfield', '2026-01-05')
        # )


        df = pd.read_sql(
            query,
            conn,
            params=('Royal Enfield', date.today())
        )

        conn.close()

        base_path = r"E:\Desktop\OEM\royal_enfeild\excel_from_db"
        full_path = os.path.join(base_path, f"{excel_filename}.xlsx")

        if not df.empty:
            df.to_excel(full_path, index=False)
            print(f" Data fetched and saved to {full_path}")
        else:
            print("No data found for given OEM and date.")

    except Exception as e:
        print(f" DB Fetch Error: {e}")
