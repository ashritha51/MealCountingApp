from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client['meal']
meal_selections = db.meal_selections
students_collection = db.students

CHART_FOLDER = "static/charts"

def generate_dashboard_data():
    # Fetch all meal selections
    data = list(meal_selections.find({}, {"_id": 0}))

    if not data:
        return 0, 0, []

    df = pd.DataFrame(data)

    # Convert timestamps to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Filter for today
    today = datetime.today().date()
    today_df = df[df['timestamp'].dt.date == today]

    # Veg/Non-Veg count for today
    veg_count = today_df[today_df['meal_type'] == 'veg'].shape[0]
    nonveg_count = today_df[today_df['meal_type'] == 'nonveg'].shape[0]

    # 📊 Generate Pie Chart: Today's Meal Type %
    pie_path = os.path.join(CHART_FOLDER, "meal_pie.png")
    if not today_df.empty:
        today_df['meal_type'].value_counts().plot(kind='pie', autopct='%1.1f%%', title='Today\'s Meal Selection', ylabel='')
        plt.savefig(pie_path)
        plt.close()

    # 📊 Bar Chart: Weekly Meal Selection Trend
    last_7_days = datetime.now() - timedelta(days=7)
    last_week_df = df[df['timestamp'] >= last_7_days]
    last_week_df['day'] = last_week_df['timestamp'].dt.strftime('%A')

    bar_path = os.path.join(CHART_FOLDER, "weekly_trend.png")
    if not last_week_df.empty:
        trend = last_week_df.groupby(['day', 'meal_type']).size().unstack(fill_value=0)
        trend = trend.reindex(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'], fill_value=0)
        trend.plot(kind='bar', stacked=True, title="Weekly Meal Selection Trend")
        plt.ylabel("Count")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(bar_path)
        plt.close()

    # 📌 Top 5 students who missed most meals
    total_students = students_collection.distinct("student_id")
    all_days = pd.date_range(end=today, periods=7).to_pydatetime().tolist()
    expected = len(all_days)

    missed_counts = {}
    for student in total_students:
        student_records = df[df['student_id'] == student]
        days_selected = student_records['timestamp'].dt.date.nunique()
        missed = expected - days_selected
        missed_counts[student] = missed

    top_missers = sorted(missed_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return veg_count, nonveg_count, top_missers
