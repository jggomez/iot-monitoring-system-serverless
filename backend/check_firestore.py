import google.auth
from google.cloud import firestore

def check_data():
    project_id = "lab-iot-493715"
    db = firestore.Client(project=project_id)
    
    docs = db.collection("sensor_data").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(5).get()
    
    count = 0
    for doc in docs:
        print(f"Document ID: {doc.id} => {doc.to_dict()}")
        count += 1
    
    if count == 0:
        print("No se encontraron datos en la colección 'sensor_data'.")
    else:
        print(f"Total de documentos encontrados (muestreo): {count}")

if __name__ == "__main__":
    check_data()
