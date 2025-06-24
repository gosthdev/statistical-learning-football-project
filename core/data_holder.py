from .data_manager import DataManager, DataType

print("DATA_HOLDER: Initializing and pre-loading data into memory...")

# Variables globales para almacenar los datos como strings JSON
PROCESSED_DATA_JSON = '{"error": "No processed data found."}'
TEST_DATA_JSON = '{"error": "No test data found."}'

try:
    # Creamos una única instancia de DataManager para usarla aquí
    data_loader = DataManager()
    
    # Precargamos los datos procesados
    if data_loader.check_file_exists():
        PROCESSED_DATA_JSON = data_loader.get_data_as_json()
        print("DATA_HOLDER: Processed data pre-loaded successfully.")
    else:
        print("DATA_HOLDER: No processed data file found to pre-load.")

    # Precargamos los datos de prueba
    TEST_DATA_JSON = data_loader.get_data_as_json(DataType.TEST)
    print("DATA_HOLDER: Test data pre-loaded successfully.")

except Exception as e:
    print(f"DATA_HOLDER: FAILED to pre-load data. Error: {e}")