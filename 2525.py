import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, PowerTransformer
from sklearn.linear_model import SGDRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import mlflow
from mlflow.models import infer_signature
from sklearn.model_selection import GridSearchCV
from sklearn.datasets import fetch_california_housing

def preprocessing_data_frame(frame):
    df = frame.copy()
    
    # Удаление выбросов (опционально, можно настроить под датасет)
    # Удаляем дома с ценой > 500000 (выбросы)
    question_price = df[df["MedHouseVal"] > 5.0]  # MedHouseVal в сотнях тысяч долларов
    df = df.drop(question_price.index)
    
    # Удаляем дома с очень маленькой ценой
    question_price_low = df[df["MedHouseVal"] < 0.5]
    df = df.drop(question_price_low.index)
    
    # Удаляем выбросы по количеству комнат
    question_rooms = df[df["AveRooms"] > 20]
    df = df.drop(question_rooms.index)
    
    # Удаляем выбросы по количеству спален
    question_bedrooms = df[df["AveBedrms"] > 10]
    df = df.drop(question_bedrooms.index)
    
    # Удаляем выбросы по населению
    question_population = df[df["Population"] > 10000]
    df = df.drop(question_population.index)
    
    df = df.reset_index(drop=True)
    return df

def scale_frame(frame):
    df = frame.copy()
    X = df.drop(columns=['MedHouseVal'])
    y = df['MedHouseVal']
    
    scaler = StandardScaler()
    power_trans = PowerTransformer()
    
    X_scale = scaler.fit_transform(X.values)
    Y_scale = power_trans.fit_transform(y.values.reshape(-1, 1))
    
    return X_scale, Y_scale, scaler, power_trans

# Загрузка датасета California Housing
california_housing = fetch_california_housing(as_frame=True)
df = california_housing.frame

print("Первые 5 строк датасета:")
print(df.head())
print("\nИнформация о датасете:")
print(df.info())
print(f"\nРазмер датасета: {df.shape}")

# Предобработка данных
df_proc = preprocessing_data_frame(df)
X, Y, scaler, power_trans = scale_frame(df_proc)

# Разбиваем на тестовую и валидационную выборки
X_train, X_val, y_train, y_val = train_test_split(
    X, Y,
    test_size=0.3,
    random_state=42
)

def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2

# Параметры для GridSearch
params = {
    'alpha': [0.0001, 0.001, 0.01, 0.05, 0.1],
    'l1_ratio': [0.001, 0.05, 0.01, 0.2]
}

# Обучение модели с MLflow
with mlflow.start_run():
    lr = SGDRegressor(random_state=42, max_iter=1000, tol=1e-3)
    clf = GridSearchCV(lr, params, cv=5, scoring='r2')
    clf.fit(X_train, y_train.reshape(-1))
    
    best = clf.best_estimator_
    y_pred = best.predict(X_val)
    
    # Обратное преобразование целевой переменной
    y_price_pred = power_trans.inverse_transform(y_pred.reshape(-1, 1))
    y_val_original = power_trans.inverse_transform(y_val)
    
    (rmse, mae, r2) = eval_metrics(y_val_original, y_price_pred)
    
    alpha = best.alpha
    l1_ratio = best.l1_ratio
    
    # Логирование параметров и метрик
    mlflow.log_param("alpha", alpha)
    mlflow.log_param("l1_ratio", l1_ratio)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2", r2)
    mlflow.log_metric("mae", mae)
    
    print(f"\nЛучшие параметры: alpha={alpha}, l1_ratio={l1_ratio}")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")
    print(f"R2: {r2:.4f}")
    
    # Сохранение модели
    predictions = best.predict(X_train)
    signature = infer_signature(X_train, predictions)
    mlflow.sklearn.log_model(best, "california_housing_model", signature=signature)
    
    # Сохранение препроцессоров для использования в сервисе
    mlflow.log_artifact("scaler.pkl")
    mlflow.log_artifact("power_transformer.pkl")

# Просмотр запусков
dfruns = mlflow.search_runs()
print("\nИстория запусков:")
print(dfruns[['run_id', 'metrics.r2', 'metrics.rmse', 'params.alpha', 'params.l1_ratio']].head())

# Получение лучшей модели
best_run = dfruns.sort_values("metrics.r2", ascending=False).iloc[0]
model_uri = best_run['artifact_uri']
print(f"\nЛучшая модель: {model_uri}")

# Пример предсказания
test_input = X_val[0:1]
prediction = best.predict(test_input)
prediction_original = power_trans.inverse_transform(prediction.reshape(-1, 1))
print(f"\nПример предсказания:")
print(f"Входные признаки (нормализованные): {test_input[0][:5]}...")
print(f"Предсказанная цена (оригинальная): {prediction_original[0][0]:.2f} (в сотнях тысяч $)")
