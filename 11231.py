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

# Установите URI для MLflow (если нужно)
# mlflow.set_tracking_uri("file:./mlruns")

# Создайте новый эксперимент для калифорнийского датасета
experiment_name = "California_Housing_Experiment"
try:
    # Попробуйте создать новый эксперимент
    experiment_id = mlflow.create_experiment(experiment_name)
    print(f"Создан новый эксперимент: {experiment_name} с ID: {experiment_id}")
except Exception as e:
    # Если эксперимент уже существует, получите его ID
    experiment_id = mlflow.get_experiment_by_name(experiment_name).experiment_id
    print(f"Используется существующий эксперимент: {experiment_name} с ID: {experiment_id}")

# Установите активный эксперимент
mlflow.set_experiment(experiment_name)

def preprocessing_data_frame(frame):
    df = frame.copy()
    
    # Удаление выбросов
    question_price = df[df["MedHouseVal"] > 5.0]
    df = df.drop(question_price.index)
    
    question_price_low = df[df["MedHouseVal"] < 0.5]
    df = df.drop(question_price_low.index)
    
    question_rooms = df[df["AveRooms"] > 20]
    df = df.drop(question_rooms.index)
    
    question_bedrooms = df[df["AveBedrms"] > 10]
    df = df.drop(question_bedrooms.index)
    
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

# Загрузка датасета
california_housing = fetch_california_housing(as_frame=True)
df = california_housing.frame

print("Первые 5 строк датасета:")
print(df.head())
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
with mlflow.start_run(run_name="California_Housing_SGD_GridSearch") as run:
    print(f"\nЗапуск run_id: {run.info.run_id}")
    print(f"Эксперимент ID: {run.info.experiment_id}")
    
    lr = SGDRegressor(random_state=42, max_iter=1000, tol=1e-3)
    clf = GridSearchCV(lr, params, cv=5, scoring='r2', n_jobs=-1)
    clf.fit(X_train, y_train.reshape(-1))
    
    best = clf.best_estimator_
    y_pred = best.predict(X_val)
    
    # Обратное преобразование
    y_price_pred = power_trans.inverse_transform(y_pred.reshape(-1, 1))
    y_val_original = power_trans.inverse_transform(y_val)
    
    (rmse, mae, r2) = eval_metrics(y_val_original, y_price_pred)
    
    alpha = best.alpha
    l1_ratio = best.l1_ratio
    
    # Логирование параметров и метрик
    mlflow.log_param("alpha", alpha)
    mlflow.log_param("l1_ratio", l1_ratio)
    mlflow.log_param("best_params", str(clf.best_params_))
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2", r2)
    mlflow.log_metric("mae", mae)
    
    # Логирование дополнительной информации
    mlflow.log_param("dataset", "California Housing")
    mlflow.log_param("train_size", len(X_train))
    mlflow.log_param("val_size", len(X_val))
    
    print(f"\nРезультаты:")
    print(f"Лучшие параметры: {clf.best_params_}")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")
    print(f"R2: {r2:.4f}")
    
    # Сохранение модели
    predictions = best.predict(X_train)
    signature = infer_signature(X_train, predictions)
    mlflow.sklearn.log_model(best, "california_housing_model", signature=signature)
    
    # Сохранение препроцессоров
    import pickle
    with open("scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    with open("power_transformer.pkl", "wb") as f:
        pickle.dump(power_trans, f)
    
    mlflow.log_artifact("scaler.pkl")
    mlflow.log_artifact("power_transformer.pkl")
    
    print(f"\nМодель сохранена в эксперименте: {experiment_name}")

# Просмотр всех экспериментов
print("\n" + "="*50)
print("ВСЕ ЭКСПЕРИМЕНТЫ:")
experiments = mlflow.search_experiments()
for exp in experiments:
    print(f"  - {exp.name} (ID: {exp.experiment_id})")

# Просмотр запусков в текущем эксперименте
print(f"\nЗАПУСКИ В ЭКСПЕРИМЕНТЕ '{experiment_name}':")
dfruns = mlflow.search_runs(experiment_ids=[experiment_id])
if len(dfruns) > 0:
    print(dfruns[['run_id', 'status', 'metrics.r2', 'metrics.rmse', 'params.alpha', 'params.l1_ratio']])
else:
    print("Нет запусков в этом эксперименте")

# Просмотр всех запусков во всех экспериментах
print("\n" + "="*50)
print("ВСЕ ЗАПУСКИ ВО ВСЕХ ЭКСПЕРИМЕНТАХ:")
all_runs = mlflow.search_runs()
print(f"Всего запусков: {len(all_runs)}")
if len(all_runs) > 0:
    print(all_runs[['run_id', 'experiment_id', 'status', 'metrics.r2']])
