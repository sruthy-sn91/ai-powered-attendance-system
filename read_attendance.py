# import sqlite3
# from datetime import datetime, timedelta

# def compute_attendance_duration(db_path="attendance.db", gap_threshold=30):
#     """
#     Reads the attendance database and computes the total duration for each person.
    
#     Args:
#         db_path (str): Path to the attendance database.
#         gap_threshold (int): Maximum gap in seconds between consecutive detections 
#                              to consider them as part of the same continuous session.
                             
#     Returns:
#         dict: Mapping of person name to total attendance duration (timedelta).
#     """
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     # Get records grouped by name and ordered by timestamp
#     cursor.execute("SELECT name, timestamp FROM attendance ORDER BY name, timestamp")
#     rows = cursor.fetchall()
#     conn.close()

#     # Group timestamps by name
#     attendance = {}
#     for name, ts_str in rows:
#         ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
#         attendance.setdefault(name, []).append(ts)
    
#     # Compute total duration for each person
#     durations = {}
#     threshold = timedelta(seconds=gap_threshold)
    
#     for name, times in attendance.items():
#         times.sort()  # Ensure sorted order
#         total_duration = timedelta(0)
#         # Start a new session with the first timestamp
#         session_start = times[0]
#         prev_time = times[0]
#         for current_time in times[1:]:
#             # If the gap is small, consider the session ongoing
#             if current_time - prev_time <= threshold:
#                 prev_time = current_time
#             else:
#                 # End current session and add its duration
#                 total_duration += (prev_time - session_start)
#                 # Start new session
#                 session_start = current_time
#                 prev_time = current_time
#         # Add the final session duration
#         total_duration += (prev_time - session_start)
#         durations[name] = total_duration
#     return durations

# def format_timedelta(td):
#     """Formats a timedelta object as HH:MM:SS."""
#     total_seconds = int(td.total_seconds())
#     hours = total_seconds // 3600
#     minutes = (total_seconds % 3600) // 60
#     seconds = total_seconds % 60
#     return f"{hours:02}:{minutes:02}:{seconds:02}"

# if __name__ == "__main__":
#     durations = compute_attendance_duration()
#     print("Attendance Duration per Person:")
#     for name, duration in durations.items():
#         print(f"{name}: {format_timedelta(duration)}")

# read_attendance.py
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict

# Configuration
DB_PATH = "attendance.db"
SCHOOL_START_HOUR = 8    # 8:00 AM
SCHOOL_END_HOUR = 18     # 6:00 PM; we will consider hours 8,9,...,17 (i.e. 10 slots per day)
SECONDS_IN_HOUR = 3600
PRESENT_THRESHOLD = 0.75  # 75%

def read_attendance(db_path=DB_PATH):
    """Reads all records from the attendance table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, timestamp FROM attendance ORDER BY timestamp")
    rows = cursor.fetchall()
    conn.close()
    # Convert timestamp strings to datetime objects
    records = [(name, datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")) for name, ts in rows]
    return records

def group_by_day_hour(records):
    """
    Groups records by (date, hour) for school hours only.
    Returns a nested dictionary: attendance[date][hour][name] = count_of_records
    """
    attendance = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for name, dt in records:
        # Only consider school hours: from SCHOOL_START_HOUR (inclusive) to SCHOOL_END_HOUR (exclusive)
        if SCHOOL_START_HOUR <= dt.hour < SCHOOL_END_HOUR:
            # Use the date part and the hour slot
            date_key = dt.date()  # e.g. 2025-04-06
            hour_key = dt.hour   # e.g. 8 for 8:00-9:00, etc.
            attendance[date_key][hour_key][name] += 1
    return attendance

def format_seconds_to_hhmmss(seconds):
    """Converts a number of seconds to HH:MM:SS format."""
    return str(timedelta(seconds=seconds))

def print_attendance_report(attendance):
    """
    For each day and each hour slot, prints the attendance durations per student,
    and then prints overall attendance percentages per student (only counting an hour as present
    if attendance >= 75% of that hour).
    """
    overall = defaultdict(lambda: {"present_hours": 0, "total_hours": 0})
    
    # Get sorted dates
    for date_key in sorted(attendance.keys()):
        print(f"Date: {date_key.strftime('%d %B %Y')}")
        # For each hour slot from SCHOOL_START_HOUR to SCHOOL_END_HOUR - 1:
        for hour in range(SCHOOL_START_HOUR, SCHOOL_END_HOUR):
            # Define the time range label
            # Format hour in 12-hour format with AM/PM:
            start_dt = datetime.combine(date_key, datetime.min.time()).replace(hour=hour)
            end_dt = start_dt + timedelta(hours=1)
            time_label = f"Hour: {start_dt.strftime('%-I:%M %p')} to {end_dt.strftime('%-I:%M %p')} IST"
            print(time_label)
            # For this date and hour, get attendance for each student.
            hour_records = attendance[date_key].get(hour, {})
            # Get all student names that have records in this slot.
            # Alternatively, if you want to list all students (even if absent) you can
            # obtain a set of all names from the entire DB.
            # Here we list only those with at least one record.
            if not hour_records:
                print("  No attendance records for this slot.")
            else:
                for name, count in hour_records.items():
                    duration = count  # assuming one record per second
                    percentage = (duration / SECONDS_IN_HOUR) * 100
                    duration_str = format_seconds_to_hhmmss(duration)
                    print(f"  {name} - {duration_str} ({percentage:.2f}%)")
                    # For overall attendance, count this hour as present only if >=75%
                    overall[name]["total_hours"] += 1
                    if percentage >= (PRESENT_THRESHOLD * 100):
                        overall[name]["present_hours"] += 1
            print()  # blank line after each hour slot
        print("-" * 40)
    
    # Compute overall attendance percentage per student across all slots
    print("Overall Attendance:")
    for name, data in overall.items():
        if data["total_hours"] > 0:
            overall_percentage = (data["present_hours"] / data["total_hours"]) * 100
            print(f"  {name} - {overall_percentage:.2f}% (Present in {data['present_hours']} out of {data['total_hours']} hours)")
        else:
            print(f"  {name} - No attendance recorded.")
    
def main():
    records = read_attendance(DB_PATH)
    attendance = group_by_day_hour(records)
    print_attendance_report(attendance)

if __name__ == "__main__":
    main()
