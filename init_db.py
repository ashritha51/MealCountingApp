from pymongo import MongoClient
from werkzeug.security import generate_password_hash
import pandas as pd
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['meal']

# Collections
students_collection = db.students
counts_collection = db.meal_counts
mess_collection=db.mess_staff
menu_collection=db.menu
meal_selections = db.meal_selections
# Student Data with Unique IDs & Hashed Passwords
# students_data = [
#     {"username": "student1", "password": generate_password_hash("password123"), "student_id": "S001", "is_first_login": True,"phone_number":6305382285},
#     {"username": "student2", "password": generate_password_hash("pass456"), "student_id": "S002", "is_first_login": True,"phone_number":9502182285},
#     {"username": "student3", "password": generate_password_hash("pass12"), "student_id": "S003", "is_first_login": True,"phone_number":8985707363}
# ]

df = pd.read_excel("studentinfo.xlsx")  # Make sure file is in same directory

for _, row in df.iterrows():
    student_data = {
        "username": row['username'],
        "password": generate_password_hash(row['password']),
        "student_id": row['student_id'],
        "is_first_login": bool(row['is_first_login']),
        "phone_number": int(row['phone_number']),
        "email": row['email']
    }

    students_collection.update_one(
        {"username": student_data["username"]},
        {"$set": student_data},
        upsert=True
    )



mess_data=[
    {"username":"staff1","password":generate_password_hash("mess123")}
]

menu_data = {
    "Monday": {
        "Breakfast": "Puri/Aloo Bhaji/Chole Masala/Idli/Ground nut chutney, Coffee & Milk",
        "Lunch": "Pulihara/Plain Rice/Kaddu Tomato/Sambhar/Chutney/Bathakakura Fry/Dal/Pudina Chutney",
        "Evening Snacks": "Samosa with Fried Chili/Veg Puff with Tomato Sauce Sachet, Tea & Milk",
        "Dinner": "Plain Rice/Boiled Egg/Milk Maker Curry/Tomato Dal/Sambhar"
    },
    "Tuesday": {
        "Breakfast": "Uthappam/Ground Nut Chutney, Coffee/Milk, Alternate: Vegetable Khichdi",
        "Lunch": "Jeera Rice/Plain Rice/Fried Egg/Tomato Curry/Palak Dal/Rasam/Gongura Chutney",
        "Evening Snacks": "Mirchi Bajji, Onions/Sweet Corn, Tea & Milk",
        "Dinner": "Plain Rice/Chole Masala/Dal Tadaka/Sambhar/Pulka"
    },
    "Wednesday": {
        "Breakfast": "Dosa/Masala Curry/Tomato Chutney/Ground Nut Chutney, Coffee/Milk",
        "Lunch": "Chapathi/Plain Rice/Brinjal Fry/Methi Dal/Rasam/Popad/Potato Chutney",
        "Evening Snacks": "Pav Bhaji/Bhel Puri, Tea & Milk",
        "Dinner": "Baghara Rice/Plain Rice/Chicken Curry/Paneer Curry/Cabbage 65/Egg Bhurji/Raitha"
    },
    "Thursday": {
        "Breakfast": "Mysore Bhajji/Groundnut Chutney/Allam Chutney, Idly, Coffee/Milk",
        "Lunch": "Plain Rice/Chamagadda Pulusu/Gongura Dal/Rasam/Dosakayi Chutney",
        "Evening Snacks": "Veg Noodles, Tea & Milk",
        "Dinner": "Plain Rice/Boiled Egg with Onion Curry/Palak Dal/Sambhar/Sweet"
    },
    "Friday": {
        "Breakfast": "Idly 02/Vada/Sambhar/Chutney, Coffee/Milk, Alternate: Pesarattu/Ground Nut Chutney",
        "Lunch": "Jeera Rice/Plain Rice/Brinjal Fry/Chukka Kura Dal/Masoor Dal/Rasam/Popad",
        "Evening Snacks": "Cupcake (2) & Tea, Milk",
        "Dinner": "Egg Fried Rice/Veg Fried Rice/White Rice, Curd, Sambhar, Alternate: Veg Pulao, Plain Rice/Dal/Sambhar/Curd"
    },
    "Saturday": {
        "Breakfast": "Idly/Sambhar/Groundnut Chutney, Coffee/Milk",
        "Lunch": "Gongura Rice/Plain Rice/Ridge Gourd Fry/Dal/Rasam/Chutney/Appadam",
        "Evening Snacks": "Onion Pakoda, Tea & Milk",
        "Dinner": "Aloo 65 Rice/Chapathi/Mixed Veg Curry/Curd"
    },
    "Sunday": {
        "Breakfast": "Veg Upma/Ground Nut Chutney/Pickle, Coffee/Milk, Alternate: Tomato Bath",
        "Lunch": "Baghara Rice/Plain Rice/Aloo Fry/Chicken Curry/Omelette/Potato Butter Masala/Sambhar/Onion & Lemon",
        "Evening Snacks": "Biscuits/Fruits (Orange, Watermelon, Banana), Tea & Milk",
        "Dinner": "Plain Rice/Vankaya Masala/Dal/Sambhar/Sweet (Badusha/Gulab Jamun)"
    }
}

    
for staff in mess_data:
    mess_collection.update_one(
        {"username": staff["username"]},
        {"$set": staff},
        upsert=True
    )
    
menu_collection.update_one({}, {"$set": menu_data}, upsert=True)

meal_selections.insert_one({
    "student_id": "S001",
    "meal_type": "veg",
    "meal_slot": "morning",
    "timestamp": datetime.today()  # use datetime.now() or parsed date
})


# Initialize meal counts if not already present
if counts_collection.count_documents({}) == 0:
    counts_collection.insert_one({"veg": 0, "nonveg": 0})

print("✅ Database initialized successfully!")
