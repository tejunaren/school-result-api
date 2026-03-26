from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import pandas as pd
from num2words import num2words

app = FastAPI()

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQkc1iWTYEe46zw15JHVii4vFSaackYx-bsveBu4IBdsdtaB6zGsh7P0v0aIyWWfWas9CEUbA9VI5IK/pub?output=csv"

def load_data():

    df = pd.read_csv(CSV_URL)

    df.columns = df.columns.str.strip()

    subjects = [
        "Telugu",
        "Hindi",
        "English",
        "Mathematics",
        "Science",
        "Social_Studies"
    ]

    df[subjects] = df[subjects].apply(pd.to_numeric, errors="coerce").fillna(0)

    df["Total"] = df[subjects].sum(axis=1)

    df["Percentage"] = (df["Total"] / 600 * 100).round(2)


    # PASS FAIL
    def result_status(row):

        for sub in subjects:

            if row[sub] < 35:
                return "FAIL"

        return "PASS"


    df["Result"] = df.apply(result_status, axis=1)


    # Division
    def division(total, result):

        if result == "FAIL":
            return "-"

        if total >= 360:
            return "FIRST DIVISION"

        elif total >= 300:
            return "SECOND DIVISION"

        elif total >= 195:
            return "THIRD DIVISION"

    df["Division"] = df.apply(lambda x: division(x["Total"], x["Result"]), axis=1)

    return df



# SEARCH PAGE
@app.get("/", response_class=HTMLResponse)
def search():

    return """

<html>

<head>

<title>Student Result</title>

<style>

body{

font-family:Arial;

background:#f2f2f2;

display:flex;

justify-content:center;

align-items:center;

height:100vh;

}

.box{

background:white;

padding:40px;

border:1px solid black;

text-align:center;

}

input{

padding:10px;

font-size:16px;

width:250px;

}

button{

padding:10px 20px;

margin-top:15px;

}

</style>

</head>

<body>

<div class="box">

<h3>STUDENT RESULT</h3>

<form action="/result" method="post">

<input name="roll_no" placeholder="Enter Roll Number" required>

<br><br>

<button>Search</button>

</form>

</div>

</body>

</html>

"""



# RESULT PAGE
@app.post("/result", response_class=HTMLResponse)
def result(roll_no: int = Form(...)):

    df = load_data()

    student = df[df["Roll_NO"] == roll_no]

    if student.empty:

        return "<h3>Result not found</h3>"

    s = student.iloc[0]


    subjects = [

        ("FIRST LANGUAGE (TELUGU)", s.Telugu),

        ("SECOND LANGUAGE (HINDI)", s.Hindi),

        ("THIRD LANGUAGE (ENGLISH)", s.English),

        ("MATHEMATICS", s.Mathematics),

        ("GENERAL SCIENCE", s.Science),

        ("SOCIAL STUDIES", s.Social_Studies)

    ]


    rows = ""

    for subject, mark in subjects:

        rows += f"""

<tr>

<td>{subject}</td>

<td>100</td>

<td>{mark}</td>

<td>{num2words(int(mark)).title()}</td>

</tr>

"""


    total_words = num2words(int(s.Total)).title()


    return f"""

<html>

<head>

<style>

body{{

font-family:Times New Roman;

background:white;

}}

.page{{

width:210mm;

min-height:297mm;

margin:auto;

padding:40px;

border:2px solid black;

}}

.header{{

text-align:center;

line-height:28px;

margin-bottom:20px;

}}

.logo{{

width:70px;

}}

.title{{

font-size:18px;

font-weight:bold;

margin-top:10px;

}}

.exam{{

font-size:14px;

margin-top:5px;

}}

.info{{

margin-top:20px;

line-height:28px;

}}

.photo{{

float:right;

width:110px;

height:130px;

border:1px solid black;

margin-top:-120px;

}}

.photo img{{

width:100%;

height:100%;

object-fit:cover;

}}

table{{

width:100%;

border-collapse:collapse;

margin-top:30px;

}}

td,th{{

border:1px solid black;

padding:8px;

font-size:14px;

}}

.print-btn{{

margin-top:30px;

text-align:center;

}}

button{{

padding:10px 20px;

}}

@media print{{

button{{display:none;}}

}}

</style>

</head>

<body>

<div class="page">


<div class="header">

<img class="logo" src="{s.School_Logo_URL}"><br>

<b>{s.School_Name}</b><br>

{s.School_Address}

<div class="title">

MEMORANDUM OF SUBJECT-WISE MARKS

</div>

<div class="exam">

SUMMATIVE EXAMINATIONS

</div>

</div>



<div class="info">

Roll No : {s.Roll_NO}<br>

Student Name : {s.Student_Name}<br>

Father's Name : {s.Father_Name}<br>

Mother's Name : {s.Mother_Name}<br>

Grade : {s.Grade}<br>

Date of Birth : {s.Date_of_Birth}

</div>



<div class="photo">

<img src="{s.Photo_URL}">

</div>



<table>

<tr>

<th>SUBJECT</th>

<th>MAX MARKS</th>

<th>MARKS SECURED</th>

<th>MARKS IN WORDS</th>

</tr>


{rows}



<tr>

<th>GRAND TOTAL</th>

<th>600</th>

<th>{s.Total}</th>

<th>{total_words}</th>

</tr>

</table>


<br><br>

Results : {s.Result}<br><br>

Division : {s.Division}



<div class="print-btn">

<button onclick="window.print()">Print</button>

</div>


</div>

</body>

</html>

"""
