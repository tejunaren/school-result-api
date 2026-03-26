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


    def result_status(row):

        for sub in subjects:
            if row[sub] < 35:
                return "FAIL"

        return "PASS"


    df["Result"] = df.apply(result_status, axis=1)


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


    return f"""

<html>

<head>

<style>

body{
font-family:Times New Roman;
background:white;
}

.page{
width:210mm;
min-height:297mm;
margin:auto;
padding:40px;
border:2px solid black;
}

.header{
display:flex;
align-items:center;
border-bottom:1px solid black;
padding-bottom:10px;
}

.logo{
width:80px;
margin-right:15px;
}

.school-details{
line-height:24px;
}

.school-name{
font-size:20pt;
font-weight:bold;
}

.school-address{
font-size:14pt;
}

.title{
text-align:center;
margin-top:15px;
font-size:16pt;
font-weight:bold;
}

.exam{
text-align:center;
margin-top:5px;
font-size:13pt;
}

.info{
margin-top:25px;
line-height:28px;
font-size:13pt;
}

.photo{
position:absolute;
right:60px;
top:220px;
width:110px;
height:130px;
border:1px solid black;
}

.photo img{
width:100%;
height:100%;
object-fit:cover;
}

table{
width:100%;
border-collapse:collapse;
margin-top:30px;
font-size:13pt;
}

td,th{
border:1px solid black;
padding:8px;
}

.result-box{
text-align:center;
margin-top:30px;
font-size:16pt;
}

.pass{
color:green;
font-weight:bold;
}

.fail{
color:red;
font-weight:bold;
}

.division{
color:blue;
font-weight:bold;
}

.bottom{
text-align:center;
margin-top:20px;
}

button{
padding:8px 20px;
font-size:14px;
}

a{
display:block;
margin-top:15px;
font-size:14px;
}

@media print{
button,a{
display:none;
}
}

</style>

</head>

<body>

<div class="page">

<div class="header">

<img class="logo"
src="{s.School_Logo_URL}"
onerror="this.src='https://img.icons8.com/color/96/school.png'">

<div class="school-details">

<div class="school-name">

{s.School_Name}

</div>

<div class="school-address">

{s.School_Address}

</div>

</div>

</div>


<div class="title">

MEMORANDUM OF SUBJECT-WISE MARKS

</div>

<div class="exam">

SUMMATIVE EXAMINATIONS

</div>


<div class="info">

Roll No        : {s.Roll_NO}<br>

Student Name   : {s.Student_Name}<br>

Father's Name  : {s.Father_Name}<br>

Mother's Name  : {s.Mother_Name}<br>

Grade          : {s.Grade}<br>

Date of Birth  : {s.Date_of_Birth}

</div>


<div class="photo">

<img src="{s.Photo_URL}"
onerror="this.src='https://via.placeholder.com/110x130'">

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

<th>{num2words(int(s.Total)).title()}</th>

</tr>

</table>



<div class="result-box">

Results :

<span class="{'pass' if s.Result=='PASS' else 'fail'}">

{s.Result}

</span>

<br><br>

Division :

<span class="division">

{s.Division}

</span>

</div>



<div class="bottom">

<button onclick="window.print()">Print</button>

<a href="/">Search Another</a>

</div>


</div>

</body>

</html>

"""
