from datetime import datetime
import pandas as pd
import os



timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
file_name = f"datawith_variant_{timestamp}.xlsx"

def save_to_excel(data):
    df = pd.DataFrame(data)

    if os.path.exists(file_name):
        df_old = pd.read_excel(file_name)
        df = pd.concat([df_old, df], ignore_index=True)

    df.to_excel(file_name, index=False)
    print(f"Data saved to {file_name}")

# def save_to_excel(data , file_name):
#     df = pd.DataFrame(data)


#     if os.path.exists(file_name):
#         df_old = pd.read_excel(file_name)
#         df = pd.concat([df_old, df], ignore_index=True)

#     df.to_excel(file_name, index=False)
#     print(f" Data saved to {file_name}")




# def save_to_excel(data):
#     df = pd.DataFrame(data)

#     # create filename using current time
#     timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#     file_name = f"data_{timestamp}.xlsx"

#     df.to_excel(file_name, index=False)
#     print(f"Data saved to {file_name}")