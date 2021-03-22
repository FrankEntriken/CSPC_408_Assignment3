# Frank Entriken
# entriken@chapman.edu
# CPSC 408 - Assignment 3

# Because it was not specified in the assignment descriptions, I still treat deleted students (isDeleted = 1) as
# any other; they can still be updated, show up in searches, and still occupy their unique StudentID.

import sqlite3
import pandas as pd
from pandas import DataFrame


# import csv file to student table
def ImportCSV(name):
    # https://stackoverflow.com/questions/2887878/importing-a-csv-file-into-a-sqlite3-database-table-using-python
    df = pd.read_csv(name)
    df.to_sql("Student", conn, if_exists='append', index=False)


# print DataFrame containing the entire student table
def DisplayAll():
    query = '''SELECT * FROM Student;'''  # displays deleted students
    cursor = conn.execute(query)
    df = DataFrame(cursor, columns=['StudentId', 'FirstName', 'LastName', 'GPA', 'Major', 'FacultyAdvisor',
                                    'Address', 'City', 'State', 'ZipCode', 'MobilePhoneNumber', 'isDeleted'])
    print(df)
    cursor.close()


# new entry to student table
def AddNewStudent():
    print("Please enter the students following information")

    uStudentId = NewValueInt("StudentId", "STUDENT ID............")
    uFirstName = NewValueStr("FIRST NAME............")
    uLastName = NewValueStr("LAST NAME.............")
    uGPA = NewValueFloat("GPA...................")
    uMajor = NewValueStr("MAJOR.................")
    uFacultyAdvisor = NewValueStr("FACULTY ADVISOR.......")
    uAddress = NewValueStr("ADDRESS...............")
    uCity = NewValueStr("CITY..................")
    uState = NewValueStr("STATE.................")
    uZipCode = NewValueStr("ZIP CODE..............")
    uMobilePhoneNumber = NewValueStr("MOBILE PHONE NUMBER...")
    # uisDeleted = NewValueInt("isDeleted", "IS DELETED............")

    query = '''
    INSERT INTO Student (StudentId, FirstName, LastName, GPA, Major, FacultyAdvisor, Address, City, State, ZipCode, 
                         MobilePhoneNumber)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?); '''

    cursor = conn.execute(query, (uStudentId, uFirstName, uLastName, uGPA, uMajor, uFacultyAdvisor, uAddress,
                                  uCity, uState, uZipCode, uMobilePhoneNumber))
    cursor.close()


# make sure new student value is an integer
def NewValueInt(column_name, pretty_name):
    while True:
        try:
            val = int(input(pretty_name))

            # if student id, make sure it is unique
            if column_name == 'StudentId':
                cursor = conn.execute("SELECT StudentId FROM Student;")
                df = DataFrame(cursor)
                if val in df.values:
                    print("This Student Id is already taken\n")
                    continue
                else:
                    cursor.close()
                    break

        except ValueError:
            print("Please enter an integer\n")

    return val


# make sure new student value is a string
def NewValueStr(pretty_name):
    while True:
        try:
            val = str(input(pretty_name))
            if "ADDRESS" in pretty_name or "ZIP" in pretty_name or "PHONE" in pretty_name:
                break
            # https://stackoverflow.com/questions/29460405/checking-if-string-is-only-letters-and-spaces-python
            if all(x.isalpha() or x.isspace() for x in val):
                break
            else:
                print("Please only use letters\n")
                continue
        except ValueError:
            print("Please enter a string\n")
    return val


# make sure new student value is a float
def NewValueFloat(pretty_name):
    while True:
        try:
            val = float(input(pretty_name))
            break
        except ValueError:
            print("Please enter a float\n")
    return val


# update student information based on student id
def UpdateStudents():

    # make sure student id is integer and unique
    while(True):
        try:
            id = int(input("Enter the ID of the student that you would like to update..."))
        except ValueError:
            print("Please enter an integer\n")
            continue
        cursor = conn.execute("SELECT StudentId FROM Student;")
        df = DataFrame(cursor)
        if id not in df.values:
            print("Please enter a valid student id\n")
            continue
        else:
            break

    # user input valid field
    while(True):
        field = input("Enter the field you would like to update (Major, FacultyAdvisor, MobilePhoneNumber)...")
        if field != "Major" and field != "FacultyAdvisor" and field != "MobilePhoneNumber":
            print("Enter either Major, FacultyAdvisor, or MobilePhoneNumber with capitalization as shown\n")
        else:
            break

    # user input new value and update to this new value
    major = input("Enter the new field value...")
    cursor = conn.execute("UPDATE Student SET %s = ? WHERE StudentId = ?;" % field, (major, id))
    print("Major has been updated, here is what the Student's information now looks like:")
    cursor2 = conn.execute("SELECT * FROM Student WHERE StudentId = ?;", (id,))
    for i in cursor2:
        print(i)
    cursor.close()


# soft delete student by setting isDeleted to 1
def DeleteStudent():
    # make sure student id is integer and unique
    while(True):
        try:
            id = int(input("Enter the ID of the student that you would like to delete..."))
        except ValueError:
            print("Please enter an integer\n")
            continue
        cursor = conn.execute("SELECT StudentId FROM Student;")
        df = DataFrame(cursor)
        if id not in df.values:
            print("Please enter a valid student id\n")
            continue
        else:
            break

    cursor = conn.execute("UPDATE Student SET isDeleted = 1 WHERE StudentId = ?;", (id,))
    cursor2 = conn.execute("SELECT * FROM Student WHERE StudentId = ?", (id,))
    for i in cursor2:
        print(i)
    print("Student has been deleted\n")
    cursor.close()


# search students by attribute
def Query():
    # user input valid attribute
    while(True):
        column_name = input("What attribute would you like to search by? (Major, GPA, City, State or Advisor)...")
        if column_name != "Major" and column_name != "GPA" and column_name != "City" \
                and column_name != "State" and column_name != "Advisor":
            print("Enter either Major, GPA, City, State or Advisor with capitalization as shown\n")
        else:
            break

    val = input("What will be the value of that attribute that you would like to search by? ...")
    cursor = conn.execute("SELECT * FROM Student WHERE %s IS ?;" % column_name, (val,))

    df = DataFrame(cursor, columns=['StudentId', 'FirstName', 'LastName', 'GPA', 'Major', 'FacultyAdvisor',
                                    'Address', 'City', 'State', 'ZipCode', 'MobilePhoneNumber', 'isDeleted'])
    print(df)
    cursor.close()


# main
# https://thispointer.com/python-pandas-how-to-display-full-dataframe-i-e-print-all-rows-columns-without-truncation/
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

conn = sqlite3.connect("./StudentDB.db")
cursor = conn.cursor()

# if Student table exists from previous running of this program, drop it and create a fresh one
try:
    cursor.execute("DROP TABLE Student")
except sqlite3.OperationalError:
    pass

cursor.execute("CREATE TABLE Student "
                 "(StudentId INTEGER PRIMARY KEY, "
                 "FirstName TEXT,"
                 "LastName TEXT,"
                 "GPA REAL,"
                 "Major TEXT,"
                 "FacultyAdvisor TEXT,"
                 "Address TEXT,"
                 "City TEXT,"
                 "State TEXT,"
                 "ZipCode TEXT,"
                 "MobilePhoneNumber TEXT,"
                 "isDeleted INTEGER)"
                 )
cursor.close()

ImportCSV("students.csv")

while(True):
    print("\nWhat option would you like to perform?")
    print("1. Display All Students")
    print("2. Add New Student")
    print("3. Update Student Information")
    print("4. Delete Student")
    print("5. Search Students by Attribute")
    print("6. Exit")
    user_in = int(input("..."))

    if user_in == 1:
        DisplayAll()
        continue

    if user_in == 2:
        AddNewStudent()
        continue

    if user_in == 3:
        UpdateStudents()
        continue

    if user_in == 4:
        DeleteStudent()
        continue

    if user_in == 5:
        Query()
        continue

    if user_in == 6:
        break