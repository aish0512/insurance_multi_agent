import pandas as pd

def handle_needs_assessment(user_data):
    df = pd.DataFrame([user_data])
    file_path = 'needs_assessment_data.xlsx'
    try:
        with pd.ExcelWriter(file_path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
    except FileNotFoundError:
        df.to_excel(file_path, index=False)

    summary = (
        f"Name: {user_data['Name']}\n"
        f"Age and Family Status: {user_data['Age and Family Status']}\n"
        f"Current Income: {user_data['Current Income']}\n"
    )

    return summary, file_path