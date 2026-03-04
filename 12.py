from sklearn.preprocessing import StandardScaler, PowerTransformer
import pandas as pd
from sklearn.model_selection import train_test_split
import mlflow
from sklearn.linear_model import SGDRegressor
from sklearn.model_selection import GridSearchCV
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from mlflow.models import infer_signature
import joblib


TARGET_COL = 'MedHouseVal'


def scale_frame(frame):
    df = frame.copy()
    X, y = df.drop(columns=[TARGET_COL]), df[TARGET_COL]
    scaler = StandardScaler()
    power_trans = PowerTransformer()
    X_scale = scaler.fit_transform(X.values)
    Y_scale = power_trans.fit_transform(y.values.reshape(-1, 1))
    return X_scale, Y_scale, power_trans


def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


def train():
    df = pd.read_csv("./df_clear.csv")
    X, Y, power_trans = scale_frame(df)
    X_train, X_val, y_train, y_val = train_test_split(X, Y, test_size=0.2, random_state=42)

    params = {
        'alpha': [0.0001, 0.001, 0.01],
        'penalty': ['l2', 'elasticnet'],
        'loss': ['squared_error', 'huber']
    }

    mlflow.set_experiment("California_Housing_Project")
    with mlflow.start_run():
        lr = SGDRegressor(max_iter=2000, random_state=42)
        clf = GridSearchCV(lr, params, cv=3)
        clf.fit(X_train, y_train.reshape(-1))

        best = clf.best_estimator_
        y_pred = best.predict(X_val)

        y_val_inv = power_trans.inverse_transform(y_val)
        y_pred_inv = power_trans.inverse_transform(y_pred.reshape(-1, 1))

        (rmse, mae, r2) = eval_metrics(y_val_inv, y_pred_inv)

        mlflow.log_params(clf.best_params_)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)

        signature = infer_signature(X_train, best.predict(X_train))
        mlflow.sklearn.log_model(best, "california_model", signature=signature)

        with open("california_model.pkl", "wb") as file:
            joblib.dump(best, file)
