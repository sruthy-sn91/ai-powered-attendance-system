import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import os
from config import DATABASE_PATH

def normalize_student_name(student_name):
    """
    Converts spaces to underscores to match the format used in the database.
    For example, "SRUTHY NATH" will become "SRUTHY_NATH".
    """
    return student_name.replace(" ", "_")

def print_distinct_names():
    """Debug helper to print the distinct names found in the attendance table."""
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query("SELECT DISTINCT name FROM attendance", conn)
    conn.close()
    print("Distinct names in DB:")
    print(df)

def get_attendance_for_student(student_name):
    """
    Retrieves attendance records for the given student using a case-insensitive comparison.
    The query uses COLLATE NOCASE to ensure matching does not depend on letter case.
    Before querying, the student name is normalized (spaces replaced by underscores)
    to match the database format.
    """
    normalized_name = normalize_student_name(student_name)
    conn = sqlite3.connect(DATABASE_PATH)
    query = "SELECT timestamp FROM attendance WHERE name = ? COLLATE NOCASE ORDER BY timestamp"
    df = pd.read_sql_query(query, conn, params=(normalized_name,))
    conn.close()
    
    # Convert the timestamp column to datetime objects.
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    except Exception as e:
        print("Error converting timestamps:", e)
    
    # Debug: Print the retrieved DataFrame
    print(f"Found {len(df)} attendance records for '{normalized_name}':")
    print(df.head())
    return df

def get_academic_for_student(student_name, csv_path="academic_data.csv"):
    df = pd.read_csv(csv_path)
    student_df = df[df["Name"].str.upper() == student_name.upper()]
    return student_df

def parse_date(date_str):
    """
    Tries to parse a date string using several common formats.
    If the year is represented with two digits, assume it belongs to the 2000s.
    """
    formats = ["%Y-%m-%d", "%d-%m-%Y", "%d-%m-%y", "%m-%d-%Y", "%m-%d-%y"]
    for fmt in formats:
        try:
            d = datetime.strptime(date_str, fmt).date()
            if d.year < 100:
                d = d.replace(year=2000 + d.year)
            return d
        except ValueError:
            continue
    raise ValueError("No valid date format found.")

def generate_student_report(student_name, report_date):
    """
    Generates a PDF report for a student with an hourly attendance breakdown
    for the given report_date (accepts various date formats).
    """
    print_distinct_names()   # Debug: list all names in DB

    attendance_df = get_attendance_for_student(student_name)
    total_records = len(attendance_df)
    
    # Calculate overall attendance metrics.
    if total_records > 0:
        first_ts = attendance_df['timestamp'].min()
        last_ts = attendance_df['timestamp'].max()
        duration = last_ts - first_ts
    else:
        first_ts, last_ts, duration = None, None, 0

    academic_df = get_academic_for_student(student_name)
    sem1_gpa = academic_df.iloc[0]['Sem1_TEE'] if not academic_df.empty else "NA"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Report for {student_name}", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Report generated on: {datetime.now().strftime('%d %B %Y %I:%M %p')}", ln=True)
    pdf.ln(5)
    
    pdf.cell(0, 10, "Attendance Summary:", ln=True)
    if total_records > 0:
        pdf.cell(0, 10, f"  First recorded: {first_ts}", ln=True)
        pdf.cell(0, 10, f"  Last recorded: {last_ts}", ln=True)
        pdf.cell(0, 10, f"  Total Duration: {duration}", ln=True)
    else:
        pdf.cell(0, 10, "  No attendance records.", ln=True)
    
    pdf.ln(5)
    pdf.cell(0, 10, "Academic Performance:", ln=True)
    pdf.cell(0, 10, f"  Semester 1 TEE GPA: {sem1_gpa}", ln=True)
    
    # Hourly Attendance Breakdown for the date entered by the user.
    try:
        report_date_obj = parse_date(report_date)
    except ValueError as e:
        pdf.ln(5)
        pdf.cell(0, 10, f"Invalid report date provided: {e}", ln=True)
    else:
        pdf.ln(5)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Hourly Attendance on {report_date_obj}", ln=True)
        pdf.set_font("Arial", "", 12)
        
        # Filter attendance records for the provided date.
        filtered_df = attendance_df[attendance_df['timestamp'].dt.date == report_date_obj]
        print(f"For date {report_date_obj}, found {len(filtered_df)} records.")
        
        if filtered_df.empty:
            pdf.cell(0, 10, "  No attendance records for this date.", ln=True)
        else:
            hour_counts = filtered_df['timestamp'].dt.hour.value_counts().sort_index()
            for hour in range(0, 24):
                count = hour_counts.get(hour, 0)
                # Convert count (numpy.int64) to a native integer.
                duration_str = str(timedelta(seconds=int(count)))
                pdf.cell(0, 10, f"  {hour:02d}:00 - {hour:02d}:59: Duration {duration_str} (based on {int(count)} records)", ln=True)
    
    output_path = f"{student_name}_report.pdf"
    pdf.output(output_path)
    return output_path

if __name__ == "__main__":
    student_name = input("Enter the student's name: ").strip()
    report_date = input("Enter the date for the report (e.g., YYYY-MM-DD or DD-MM-YYYY): ").strip()
    pdf_file = generate_student_report(student_name, report_date)
    print(f"Generated report: {pdf_file}")
