import sqlite3
from fix_path import create_directory

def create_table():
    conn = sqlite3.connect('criminals.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS criminaldata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            father_name TEXT,
            mother_name TEXT,
            gender TEXT NOT NULL,
            dob TEXT,
            blood_group TEXT,
            identification_mark TEXT NOT NULL,
            nationality TEXT NOT NULL,
            religion TEXT NOT NULL,
            crimes_done TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insertData(data):
    rowId = 0

    # Ensure the directory exists
    create_directory('face_samples/temp_criminal')

    create_table()  # Ensure table exists

    db = sqlite3.connect("criminals.db")
    cursor = db.cursor()
    print("database connected")

    query = "INSERT INTO criminaldata (name, father_name, mother_name, gender, dob, blood_group, identification_mark, nationality, religion, crimes_done) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    values = (data["Name"], data["Father's Name"], data["Mother's Name"], data["Gender"],
              data["DOB(yyyy-mm-dd)"], data["Blood Group"], data["Identification Mark"],
              data["Nationality"], data["Religion"], data["Crimes Done"])

    try:
        cursor.execute(query, values)
        db.commit()
        rowId = cursor.lastrowid
        print("data stored on row %d" % rowId)
    except Exception as e:
        db.rollback()
        print("Data insertion failed:", e)

    db.close()
    print("connection closed")
    return rowId

def retrieveData(name):
    conn = sqlite3.connect('criminals.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM criminaldata WHERE name=?", (name,))
    data = cursor.fetchone()

    if data is None:
        return None, None

    id = data[0]
    crim_data = {
        "Name": data[1],
        "Father's Name": data[2],
        "Mother's Name": data[3],
        "Gender": data[4],
        "DOB": data[5],
        "Blood Group": data[6],
        "Identification Mark": data[7],
        "Nationality": data[8],
        "Religion": data[9],
        "Crimes Done": data[10]
    }

    conn.close()
    return id, crim_data
