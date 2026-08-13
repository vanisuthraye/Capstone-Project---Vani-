Module 2 Analytics Pipeline
import pandas as pd
import seaborn as sns

df = sns.load_dataset("titanic")

# Offline fallback
df.to_csv("titanic.csv", index=False)

df.head()
missing = df.isnull().mean()*100

missing[missing > 0]
df_clean = df.copy()

# Drop high missing column
df_clean.drop(columns=["deck"], inplace=True)

# Drop rows where missing <5%
df_clean.dropna(subset=["embarked","embark_town"], inplace=True)

# Impute age
df_clean["age"].fillna(
    df_clean["age"].median(),
    inplace=True
)
df_clean["age"] = df_clean["age"].fillna(df_clean["age"].median())
import matplotlib.pyplot as plt

sns.histplot(df_clean["age"], kde=True)
plt.show()


sns.boxplot(x=df_clean["age"])
plt.show()
sns.histplot(df_clean["fare"], kde=True)
plt.show()


sns.boxplot(x=df_clean["fare"])
plt.show()
def count_outliers(column):

    Q1 = df_clean[column].quantile(0.25)
    Q3 = df_clean[column].quantile(0.75)

    IQR = Q3-Q1

    lower = Q1 - 1.5*IQR
    upper = Q3 + 1.5*IQR

    return ((df_clean[column]<lower) |
            (df_clean[column]>upper)).sum()


age_outliers=count_outliers("age")
fare_outliers=count_outliers("fare")

age_outliers, fare_outliers
mean = df_clean.fare.mean()
median = df_clean.fare.median()
mode = df_clean.fare.mode()[0]

mean,median,mode
df_clean.groupby("sex")["survived"].mean()
df_clean.groupby("pclass")["survived"].mean()
df_clean.groupby(
    ["sex","pclass"]
)["survived"].mean()
corr_cols=[
    "survived",
    "pclass",
    "age",
    "sibsp",
    "parch",
    "fare"
]


corr=df_clean[corr_cols].corr()

sns.heatmap(
    corr,
    annot=True,
    cmap="coolwarm"
)

plt.show()
corr_pairs = (
    corr.where(
        ~pd.DataFrame(
            False,
            index=corr.index,
            columns=corr.columns
        )
    )
)

pairs = (
    corr.abs()
    .unstack()
    .sort_values(
        ascending=False
    )
)

pairs.head(10)
sns.barplot(
    data=df_clean,
    x="sex",
    y="survived"
)
sns.barplot(
    data=df_clean,
    x="pclass",
    y="survived"
)
sns.boxplot(
    data=df_clean,
    x="survived",
    y="age"
)
sns.boxplot(
    data=df_clean,
    x="survived",
    y="fare"
)
from sklearn.preprocessing import StandardScaler

scaler=StandardScaler()

scaled=df_clean.copy()

scaled[
    ["age","fare"]
]=scaler.fit_transform(
    df_clean[["age","fare"]]
)


scaled[["age","fare"]].describe()
df=pd.read_csv("titanic_clean.csv")
from sklearn.model_selection import train_test_split


X=df.drop("survived",axis=1)
y=df["survived"]


X_train,X_test,y_train,y_test=train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)
numeric=[
"age",
"sibsp",
"parch",
"fare"
]

categorical=[
"sex",
"embarked"
]
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder,StandardScaler


numeric_pipe=Pipeline([
    ("imputer",
     SimpleImputer(strategy="median")),
    ("scale",
     StandardScaler())
])


cat_pipe=Pipeline([
    ("imputer",
     SimpleImputer(strategy="most_frequent")),
    ("encode",
     OneHotEncoder(handle_unknown="ignore"))
])


preprocessor=ColumnTransformer([
    ("num",numeric_pipe,numeric),
    ("cat",cat_pipe,categorical)
])
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier


models={

"Logistic Regression":
LogisticRegression(),

"Decision Tree":
DecisionTreeClassifier(),

"Random Forest":
RandomForestClassifier()

}
for name,model in models.items():

    pipe=Pipeline([
        ("prep",preprocessor),
        ("model",model)
    ])

    pipe.fit(X_train,y_train)
    from sklearn.metrics import *

from sklearn.metrics import *

accuracy_score(y_test, y_pred)
precision_score(y_test, y_pred)
recall_score(y_test, y_pred)
f1_score(y_test, y_pred)
roc_auc_score(y_test, y_pred_proba)

from sklearn.tree import plot_tree
features = X_train.columns.tolist()

plot_tree(
    model,
    feature_names=features,
    class_names=["Dead", "Survived"],
    filled=True
)
RandomForestClassifier()
RandomForestClassifier(
class_weight="balanced"
)
from imblearn.over_sampling import SMOTE

smote=SMOTE()

X_train_sm, y_train_sm = smote.fit_resample(
    X_train,
    y_train
)
from sklearn.model_selection import GridSearchCV


rf=RandomForestClassifier(
oob_score=True,
random_state=42
)


params={
"n_estimators":[100,200],
"max_depth":[5,10,None],
"max_features":["sqrt","log2"]
}


grid=GridSearchCV(
rf,
params,
cv=5
)


grid.fit(
X_train_processed,
y_train
)


grid.best_params_

grid.best_estimator_.oob_score_
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

n = X_test.shape[0]
p = X_test.shape[1]
adjusted_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1)

print("MAE:", mae)
print("RMSE:", rmse)
print("R2:", r2)
print("Adjusted R2:", adjusted_r2)
residuals = y_test - y_pred

sns.scatterplot(
    x=y_test,
    y=residuals
)
plt.axhline(y=0, color='red', linestyle='--')
plt.xlabel("Actual Fare")
plt.ylabel("Residuals")
plt.title("Residual Plot")
plt.show()

joblib.dump(
best_pipeline = grid_search.best_estimator_

joblib.dump(
    best_pipeline,
    "best_titanic_pipeline.joblib"
)
loaded.predict(
X_test.head()
)
