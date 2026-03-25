from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQkc1iWTYEe46zw15JHVii4vFSaackYx-bsveBu4IBdsdtaB6zGsh7P0v0aIyWWfWas9CEUbA9VI5IK/pub?output=csv"


def load_data():

    df = pd.read_csv(CSV_URL)

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

    def division(total):

        if total >= 360:
            return "1st Division"

        elif total >= 300:
            return "2nd Division"

        elif total >= 195:
            return "3rd Division"

        else:
            return "Fail"

    df["Division"] = df["Total"].apply(division)

    return df


@app.get("/", response_class=HTMLResponse)
def search_page():

    return """

    <html>

    <head>

    <title>Exam Result</title>

    <style>

    body{
    font-family:Arial;
    text-align:center;
    margin-top:100px;
    background:#f2f2f2;
    }

    input{
    padding:10px;
    width:220px;
    }

    button{
    padding:10px;
    background:#3498db;
    color:white;
    border:none;
    }

    </style>

    </head>

    <body>

    <h2>Exam Result Search</h2>

    <form action="/result" method="post">

    <input name="student_id" placeholder="Enter Roll Number" required>

    <br><br>

    <button type="submit">Search</button>

    </form>

    </body>

    </html>

    """


@app.post("/result", response_class=HTMLResponse)
def result(student_id: int = Form(...)):

    df = load_data()

    student = df[df["Student_ID"] == student_id]

    if student.empty:
        return "<h3>Result not found</h3>"

    s = student.iloc[0]

    return f"""

    <html>

    <head>

    <style>

    body{{font-family:Arial;text-align:center;background:#f2f2f2}}

    table{{margin:auto;border-collapse:collapse;background:white}}

    td,th{{padding:10px;border:1px solid #ddd}}

    </style>

    </head>

    <body>

    <h2>Student Result</h2>

    <table>

    <tr><th>Roll Number</th><td>{s.Student_ID}</td></tr>

    <tr><th>Total</th><td>{s.Total}</td></tr>

    <tr><th>Percentage</th><td>{s.Percentage}%</td></tr>

    <tr><th>Division</th><td>{s.Division}</td></tr>

    </table>

    <br>

    <a href="/">Search Another</a>

    </body>

    </html>

    """
