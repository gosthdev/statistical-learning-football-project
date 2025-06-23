from .models.multiple_linear_regression import MultipleLinearRegressionModel

print("MODEL_TRAINER: Initializing and loading the global prediction model...")

# Esta variable contendrá la única instancia del modelo para toda la app.
model_instance = None

try:
    # Creamos la instancia del modelo
    model_instance = MultipleLinearRegressionModel()
    
    # Cargamos los modelos y los datos de prueba que ya existen en disco
    model_instance.load_models()
    model_instance.load_test_data()
    
    print("MODEL_TRAINER: Global model instance created and loaded successfully.")
except Exception as e:
    print(f"MODEL_TRAINER: FAILED to load global model. Error: {e}")
    # Dejamos la variable como None si algo falla para poder manejar el error
    model_instance = None