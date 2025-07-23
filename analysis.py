import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split,cross_val_score
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
from imblearn.over_sampling import SMOTE



# # Connect to MongoDB
# client = MongoClient("mongodb://localhost:27017/")
# db = client["meal"]
# meals_collection = db["meals"]

# # Fetch data
# data = list(meals_collection.find({}, {"_id": 0}))
# df = pd.DataFrame(data)

# # Optional: Convert timestamp
# if 'timestamp' in df.columns:
#     df['timestamp'] = pd.to_datetime(df['timestamp'])

# # Save as CSV
# df.to_csv("meal_data.csv", index=False)
# print("✅ Exported meal_data.csv")


df = pd.read_csv("meal_data.csv")

print(df.shape)
print(df.columns)
print(df.dtypes)
print(df.head())
print("Total Records:", len(df))
print("Unique Students:", df['student_id'].nunique())
print("\nMeal Type Count:\n", df['meal_type'].value_counts())
print("\nStatus Count:\n", df['status'].value_counts())
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['day_name'] = df['timestamp'].dt.day_name()
df['hour'] = df['timestamp'].dt.hour
df['date'] = df['timestamp'].dt.date
df['day_of_week'] = df['timestamp'].dt.day_name()
df['slot'] = df['hour'].apply(lambda h: 0 if h < 12 else 1)


# Meals per Day of Week
df['day_of_week'].value_counts().plot(kind='bar', title='Meals per Day of Week')
plt.xlabel('Day')
plt.ylabel('Count')
plt.show()

# Meals per Hour
df['hour'].value_counts().sort_index().plot(kind='bar', title='Meals per Hour of Day')
plt.xlabel('Hour')
plt.ylabel('Count')
plt.show()

# Morning vs Evening
df['slot'].value_counts().plot(kind='pie', autopct='%1.1f%%', title='Morning vs Evening Slot')
plt.ylabel('')
plt.show()

# Students with both veg and nonveg
mixed_students = df.groupby('student_id')['meal_type'].nunique()
print("Students with both veg and nonveg:")
print(mixed_students[mixed_students > 1])

# Pending meals by type
sns.countplot(data=df[df['status'] == 'pending'], x='meal_type')
plt.title('Pending Meals by Meal Type')
plt.show()

# Pending meals by day
sns.countplot(data=df[df['status'] == 'pending'], x='day_of_week', order=[
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
plt.title('Pending Meals by Day')
plt.xticks(rotation=45)
plt.show()

# Duplicate timestamp for same student
duplicates = df[df.duplicated(subset=['student_id', 'timestamp'], keep=False)]
print("Duplicate Meal Entries (same timestamp):\n", duplicates)

# Students with both 'pending' and 'used' for same time
conflicts = df.groupby(['student_id', 'timestamp'])['status'].nunique()
conflicted = conflicts[conflicts > 1]
print("Conflicting Records (used & pending same time):\n", conflicted)

# Filter only used meals
df = df[df['status'] == 'used']

# Encode meal type as target variable
df['meal_type_encoded'] = df['meal_type'].map({'veg': 0, 'nonveg': 1})

# Feature engineering
df['day_encoded'] = df['day_of_week'].astype('category').cat.codes
df['student_encoded'] = df['student_id'].astype('category').cat.codes

# Domain logic: nonveg only on Wed night and Sun morning
df['is_nonveg_day'] = df.apply(
    lambda row: 1 if ((row['day_of_week'] == 'Wednesday' and row['hour'] >= 19) or
                      (row['day_of_week'] == 'Sunday' and row['hour'] < 12)) else 0, axis=1)

# More domain features
df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday']).astype(int)
df['is_lunch_time'] = df['hour'].between(11, 14).astype(int)
df['is_dinner_time'] = df['hour'].between(19, 21).astype(int)
df['day_hour_combo'] = df['day_encoded'] * 100 + df['hour']

# Final feature set
features = ['hour', 'slot', 'day_encoded', 'student_encoded',
            'is_nonveg_day', 'is_weekend', 'is_lunch_time', 'is_dinner_time', 'day_hour_combo']
X = df[features]
y = df['meal_type_encoded']

# Stratified train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# Apply SMOTE for class balancing
sm = SMOTE(random_state=42, k_neighbors=2)
X_resampled, y_resampled = sm.fit_resample(X_train, y_train)

# Train Gradient Boosting model
model = GradientBoostingClassifier(random_state=42)
model.fit(X_resampled, y_resampled)

# Predict on test set
y_pred = model.predict(X_test)

# Evaluate
print("✅ Accuracy:", accuracy_score(y_test, y_pred))
print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred, target_names=["Veg", "Nonveg"]))

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Veg", "Nonveg"])
disp.plot()
plt.title("Confusion Matrix")
plt.show()

# Cross-validation accuracy (optional)
cv_scores = cross_val_score(model, X, y, cv=5)
print("🧪 Cross-Validation Accuracy:", round(cv_scores.mean() * 100, 2), "%")