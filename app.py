from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# allow dashboard access
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


@app.get("/")
def home():
    return {"message": "Student Result API Running"}


# show only one student result
@app.get("/result/{student_id}")
def student_result(student_id: int):

    df = load_data()

    student = df[df["Student_ID"] == student_id]

    if student.empty:
        return {"message": "Student not found"}

    return student.to_dict(orient="records")