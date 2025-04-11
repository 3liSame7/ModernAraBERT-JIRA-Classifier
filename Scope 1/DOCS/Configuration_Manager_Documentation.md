# **Configuration Manager Documentation**

This project includes a **Configuration Manager** to manage environment variables and settings, along with a **Singleton pattern** for shared instances.

## **Table of Contents**

* [Overview](https://chatgpt.com/?temporary-chat=true&model=gpt-4o#overview)  
* [Features](https://chatgpt.com/?temporary-chat=true&model=gpt-4o#features)  
* [Installation](https://chatgpt.com/?temporary-chat=true&model=gpt-4o#installation)  
* [Configuration](https://chatgpt.com/?temporary-chat=true&model=gpt-4o#configuration)  
* [Usage](https://chatgpt.com/?temporary-chat=true&model=gpt-4o#usage)   
* [Modules](https://chatgpt.com/?temporary-chat=true&model=gpt-4o#modules)  
  * [Singleton](https://chatgpt.com/?temporary-chat=true&model=gpt-4o#singleton)  
  * [Configuration Manager](https://chatgpt.com/?temporary-chat=true&model=gpt-4o#configuration-manager)  
  * [Qdrant Utilities](https://chatgpt.com/?temporary-chat=true&model=gpt-4o#qdrant-utilities)  
* [Environment Variables](https://chatgpt.com/?temporary-chat=true&model=gpt-4o#environment-variables)  
* [Django Settings](https://chatgpt.com/?temporary-chat=true&model=gpt-4o#django-settings)  
---

## **Overview**

This application is designed for **handling and classifying Jira tickets** using **vector search**. It leverages:

* **Qdrant** for storing embeddings.  
* **LangChain's SentenceTransformer** for generating embeddings.  
* **Django REST framework** for API interactions.

---

## **Features**

 ✅ Implements **Singleton pattern** for configuration management.  
 ✅ Loads configurations from **environment variables or .env files**.  
 ✅ Integrates **Qdrant** for **vector search** capabilities.  
 ✅ Supports **ML model paths** for classification.  
 ✅ Uses **Django settings** to dynamically load configuration.

---

## **Installation**

### **1\. Clone the Repository**
```bash
git clone --branch Badawy https://GS-SWDC@dev.azure.com/GS-SWDC/Data%20Team/_git/Modern%20Arabert%20and%20Ticket%20Classification
```
### **2\. Create a Virtual Environment**
```bash
python -m venv venv  
venv\\Scripts\\activate
```
### **3\. Install Dependencies**
```bash
pip install -r requirements.txt
```
### **4\. Set Up Configuration**

* Ensure the **`config.env`** file is placed inside the `resources` directory.

The `.env` file should contain:  
```config
QDRANT_URL="http://localhost:6333"  
COLLECTION_NAME="ticket_embeddings_django"  
EMBEDDING_MODEL="sentence-transformers/paraphrase-MiniLM-L3-v2"
```
* 

### **5\. Run the Django Server**

python manage.py runserver

---

## **Configuration**

The application uses a **Configuration Manager** that loads settings from:

* `.env` files (if present)  
* Environment variables (fallback)

Configuration values include:

* **QDRANT\_URL** → The Qdrant server URL.  
* **COLLECTION\_NAME** → The name of the Qdrant collection.  
* **EMBEDDING\_MODEL** → The model used for generating embeddings.

---

## **Usage**

### **1\. Ensure Qdrant is Running**

Before using the application, **start the Qdrant server**:
```bash
docker run -name qdrant -p 6334:6334 qdrant/qdrant
```
### **2\. Check Environment Variables**

If the `.env` file is not present, manually set:

```bash
export QDRANT_URL="http://localhost:6333"  
export COLLECTION_NAME="ticket_embeddings_django"  
export EMBEDDING_MODEL="sentence-transformers/paraphrase-MiniLM-L3-v2"
```
### **3\. Run the Application**
```bash
python manage.py runserver
```
---

## **Modules**

### **Singleton**

* Implements **SingletonABC** and **Singleton** metaclasses.  
* Ensures that only **one instance** of a class is created.

### **Configuration Manager**

* Loads environment variables.  
* Provides **paths to ML models**.  
* Reads **Qdrant settings** dynamically.

### **Qdrant Utilities**

* Connects to **Qdrant**.  
* Ensures the **collection exists**.  
* Loads the **embedding model**.

---

## **Environment Variables**

| Variable | Description | Default Value |
| ----- | ----- | ----- |
| `QDRANT_URL` | Qdrant database URL | `http://localhost:6333` |
| `COLLECTION_NAME` | Qdrant collection name | `ticket_embeddings_django` |
| `EMBEDDING_MODEL` | Path or name of embedding model | `sentence-transformers/paraphrase-MiniLM-L3-v2` |

---

## **Django Settings**

The `settings.py` file dynamically loads:
```python
from configuration_manager.configuration_manager import ConfigurationManager

config_manager = ConfigurationManager()

QDRANT_URL = config_manager.qdrant_url  
COLLECTION_NAME = config_manager.collection_name  
EMBEDDING_MODEL = config_manager.embedding_model
```
