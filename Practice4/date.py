#Task 2
from datetime import datetime, timedelta

# Get current date
current_date = datetime.now()

# Subtract five days
five_days_ago = current_date - timedelta(days=5)

print(f"Current date: {current_date.strftime('%Y-%m-%d')}")
print(f"Five days ago: {five_days_ago.strftime('%Y-%m-%d')}")

#Task 2

# Get today's date
today = datetime.now().date()

# Calculate yesterday and tomorrow
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)

print(f"Yesterday: {yesterday}")
print(f"Today: {today}")
print(f"Tomorrow: {tomorrow}")

#Task 3

# Get current datetime with microseconds
current_datetime = datetime.now()
print(f"With microseconds: {current_datetime}")
print(f"Microseconds: {current_datetime.microsecond}")

# Drop microseconds (method 1: replace)
without_microseconds = current_datetime.replace(microsecond=0)
print(f"Without microseconds (replace): {without_microseconds}")

# Drop microseconds (method 2: strftime)
formatted = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
print(f"Without microseconds (format): {formatted}")

#Task 4

# Method 1: Using specific dates
date1 = datetime(2026, 2, 18, 12, 0, 0)  # Feb 18, 2026 at 12:00:00
date2 = datetime(2026, 2, 15, 10, 30, 0)  # Feb 15, 2026 at 10:30:00

difference = date1 - date2
difference_seconds = difference.total_seconds()

print(f"Date 1: {date1}")
print(f"Date 2: {date2}")
print(f"Difference: {difference}")
print(f"Difference in seconds: {difference_seconds} seconds")

#Task 5

print("=" * 50)
print("TASK 1: Subtract five days from current date")
print("=" * 50)
current = datetime.now()
five_days_ago = current - timedelta(days=5)
print(f"Current: {current.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Five days ago: {five_days_ago.strftime('%Y-%m-%d %H:%M:%S')}")

print("\n" + "=" * 50)
print("TASK 2: Yesterday, today, tomorrow")
print("=" * 50)
today = current.date()
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)
print(f"Yesterday: {yesterday}")
print(f"Today: {today}")
print(f"Tomorrow: {tomorrow}")

print("\n" + "=" * 50)
print("TASK 3: Drop microseconds from datetime")
print("=" * 50)
print(f"Original: {current}")
print(f"Without microseconds: {current.replace(microsecond=0)}")

print("\n" + "=" * 50)
print("TASK 4: Calculate two date difference in seconds")
print("=" * 50)
date1 = datetime(2026, 2, 18, 12, 0, 0)
date2 = datetime(2026, 2, 15, 10, 30, 0)
diff = date1 - date2
print(f"Date1: {date1}")
print(f"Date2: {date2}")
print(f"Difference in seconds: {diff.total_seconds()}")
