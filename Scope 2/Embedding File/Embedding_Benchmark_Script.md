# **Customer Support Ticket Classification and Similarity Search**

This notebook processes customer support tickets, transforms the data, applies machine learning techniques for classification, and utilizes vector embeddings to perform similarity searches using Qdrant.

## **1. Data Loading and Preprocessing**

### **1.1 Importing Required Libraries**
```python
import pandas as pd
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams
from sentence_transformers import SentenceTransformer
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.docstore.document import Document
from langchain.vectorstores import Qdrant
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report
from sklearn.model_selection import train_test_split
import requests
from langchain.schema import BaseRetriever
```

### **1.2 Loading Customer Support Tickets Data**
```python
df = pd.read_csv(r'E:ShadowingScope 1customer_support_tickets.csv')
```
* The dataset is loaded from a CSV file located on disk.

### **1.3 Data Transformation**

Each row in the dataset is transformed into a structured dictionary with simplified column names.
```python
def transform_row(row):  
    return {  
        "ticket_id": row["Ticket ID"],   
        "summary": row["Ticket Subject"],   
        "description": row["Ticket Description"],    
        "priority": row["Ticket Priority"],    
        "status": row["Ticket Status"],    
        "reporter": row["Customer Email"],    
        "label": row["Ticket Type"],    
        "created_at": row["Date of Purchase"],  
    }

# Apply transformation  
transformed_data = df.apply(transform_row, axis=1)  
df_Jira = pd.DataFrame(transformed_data.tolist())
```
* Converts raw dataset fields into a cleaner format for analysis.

---

## **2. Train-Test Split**

The dataset is split into training and testing sets for model evaluation.

```python
train_df, test_df_ = train_test_split(df_Jira, test_size=0.2, random_state=42)  
test_labels = test_df_['label'].copy()  
test_df = test_df_.drop(columns=['label'])
```
* **80% Training Set, 20% Testing Set**: Ensures generalization.  
* **Random seed (`random_state=42`)**: Makes the split reproducible.

---

## **3. Data Transformation for Model Input**

A second transformation function ensures that training data remains consistently structured.

```python
def transform_train(row):  
    return {  
        "ticket_id": row["ticket_id"],   
        "summary": row["summary"],   
        "description": row["description"],    
        "priority": row["priority"],    
        "status": row["status"],    
        "reporter": row["reporter"],    
        "label": row["label"],    
        "created_at": row["created_at"],  
    }

transformed_data = train_df.apply(transform_train, axis=1)
```
* This transformation aligns the training data format with earlier preprocessing steps.
```json
{
  "ticket_id": 1,
  "summary": "Product setup",
  "description": "I'm having an issue with the {product_purchased}. Please  assist.\n\nYour billing zip code is: 71701.\n\nWe appreciate that you have requested a website address.\n\nPlease double check your email address. I've tried troubleshooting steps mentioned in the user manual, but the issue persists.",
  "priority": "Critical",
  "status": "Pending Customer Response",
  "reporter": "carrollallison@example.com",
  "label": "Technical issue",
  "created_at": "2021-03-22"
}
```
---

## **4. Text Embedding Using Pretrained Sentence Transformers**

We use **Sentence-BERT models** to generate numerical vector embeddings for each ticket.

### **4.1 Loading Pretrained Embedding Models**

```python
models = {  
    "all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",  
    "all-mpnet-base-v2": "sentence-transformers/all-mpnet-base-v2",  
    "paraphrase-MiniLM-L3-v2": "sentence-transformers/paraphrase-MiniLM-L3-v2",  
    "bge-small-en": "BAAI/bge-small-en",   
    "paraphrase-MiniLM-L6-v2": "sentence-transformers/paraphrase-MiniLM-L6-v2",  
    "all-distilroberta-v1": "sentence-transformers/all-distilroberta-v1",  
}

model = models["paraphrase-MiniLM-L3-v2"]
```
* **Different Transformer Models**: Each model has a different architecture optimized for various NLP tasks.  
* **Selected Model**: `"paraphrase-MiniLM-L3-v2"` is used for embedding.

### **4.2 Encoding Ticket Data into Embeddings**
```python

texts_to_embed = [  
    f"Ticket ID: {row['ticket_id']}, Summary: {row['summary']}, "  
    f"Description: {row['description']}, Priority: {row['priority']}, "  
    f"Status: {row['status']}, Reporter: {row['reporter']}, "  
    f"Label: {row['label']}, Created At: {row['created_at']}"  
    for row in transformed_data  
]

train_embeddings = model.encode(texts_to_embed, show_progress_bar=True)
```
* **Each ticket is converted into a string** before being embedded into numerical vectors.  
* **Embeddings are computed for training data**.

---

## **5. Uploading Embeddings to Qdrant for Similarity Search**

### **5.1 Connecting to Qdrant**

```python
client = QdrantClient("http://localhost:6333")
```
* Qdrant is an **open-source vector database** optimized for similarity search.

### **5.2 Uploading Ticket Embeddings to Qdrant**
```python
client.upload_collection(  
    collection_name="ticket_embeddings_paraphrase-MiniLM-L3-v2",  
    vectors=train_embeddings,  
    payload=[  
        {  
            "ticket_id": row["ticket_id"],  
            "summary": row["summary"],  
            "description": row["description"],  
            "priority": row["priority"],  
            "status": row["status"],  
            "reporter": row["reporter"],  
            "label": row["label"],  
            "created_at": row["created_at"]  
        }  
        for row in transformed_data  
    ]  
)
```
* **Vector embeddings are stored in Qdrant** with ticket metadata.

---

## **6. Similarity Search for New Tickets**

### **6.1 Querying Qdrant with a Test Ticket**
```python
test_ticket = test_df.iloc[10]  
test_text = (  
    f"Ticket ID: {test_ticket['ticket_id']}, Summary: {test_ticket['summary']}, "  
    f"Description: {test_ticket['description']}, Priority: {test_ticket['priority']}, "  
    f"Status: {test_ticket['status']}, Reporter: {test_ticket['reporter']}, "  
    f"Created At: {test_ticket['created_at']}"  
)

test_embedding = model.encode(test_text)

search_results = client.search(  
    collection_name="ticket_embeddings_paraphrase-MiniLM-L3-v2",  
    query_vector=test_embedding,  
    limit=5  
)
```
* **Encodes a test ticket** into an embedding and retrieves similar tickets.

### **6.2 Applying Softmax for Confidence Scoring**
```python
def softmax(x):  
    exp_x = np.exp(x - np.max(x))    
    return exp_x / exp_x.sum()

scores = np.array([result.score for result in search_results])  
normalized_scores = softmax(scores)
```
* **Softmax is used** to normalize similarity scores.

### **6.3 Displaying Results**
```python
for label, raw_score, norm_score in zip(labels, scores, normalized_scores):  
    print(f"Label: {label}, Raw Score: {raw_score:.4f}, Confidence Score: {norm_score:.4f}")
```
* Outputs similar tickets with their respective confidence scores.
```bash
Label: Technical issue
Raw Score (similarity): 0.8649
Confidence (softmax): 0.2015
Excerpt: Ticket ID: 414, Summary: Product compatibility, Description: I'm having an issue ...
--------------------------------------------------
Label: Refund request
Raw Score (similarity): 0.8623
Confidence (softmax): 0.2010
Excerpt: Ticket ID: 1409, Summary: Account access, Description: I'm having an issue with  ...
--------------------------------------------------
Label: Cancellation request
Raw Score (similarity): 0.8540
Confidence (softmax): 0.1994
Excerpt: Ticket ID: 7488, Summary: Data loss, Description: I'm having an issue with the { ...
--------------------------------------------------
Label: Cancellation request
Raw Score (similarity): 0.8527
Confidence (softmax): 0.1991
Excerpt: Ticket ID: 2859, Summary: Account access, Description: I'm having an issue with  ...
--------------------------------------------------
Label: Billing inquiry
Raw Score (similarity): 0.8520
Confidence (softmax): 0.1990
Excerpt: Ticket ID: 7689, Summary: Product compatibility, Description: I'm having an issu ...
--------------------------------------------------
```
---

## **7. Model Benchmarking**

To compare different models, we evaluate classification performance on test data.

### **7.1 Computing Evaluation Metrics**
```python
accuracy = accuracy_score(y_true, y_pred)  
f1 = f1_score(y_true, y_pred, average="weighted")  
precision = precision_score(y_true, y_pred, average="weighted", zero_division=0)  
recall = recall_score(y_true, y_pred, average="weighted", zero_division=0)

* **Accuracy**: Measures correct predictions.  
* **F1-score**: Balances precision and recall.  
* **Precision & Recall**: Evaluates retrieval performance.

### **7.2 Comparing Different Models**

for model_name, metrics in results_summary.items():  
    print(f"Model: {model_name}")  
    for metric_name, value in metrics.items():  
        print(f"  {metric_name}: {value:.4f}")  
    print("----------------------------------------------------------------------")
```
* **Shows accuracy, precision, recall, and F1-score for each model**.
```bash
======================== MODEL: all-MiniLM-L6-v2 ========================

Accuracy:  0.1936
F1 Score:  0.1703
Precision: 0.1928
Recall:    0.1936
Full classification report:
                      precision    recall  f1-score   support

     Billing inquiry       0.22      0.07      0.10       357
Cancellation request       0.17      0.10      0.12       327
     Product inquiry       0.19      0.32      0.24       316
      Refund request       0.17      0.09      0.12       345
     Technical issue       0.20      0.40      0.27       349

            accuracy                           0.19      1694
           macro avg       0.19      0.20      0.17      1694
        weighted avg       0.19      0.19      0.17      1694

======================== MODEL: all-mpnet-base-v2 ========================

Accuracy:  0.2054
F1 Score:  0.1820
Precision: 0.2042
Recall:    0.2054
Full classification report:
                      precision    recall  f1-score   support

     Billing inquiry       0.21      0.14      0.16       357
Cancellation request       0.20      0.10      0.13       327
     Product inquiry       0.19      0.42      0.27       316
      Refund request       0.19      0.06      0.09       345
     Technical issue       0.22      0.33      0.27       349

            accuracy                           0.21      1694
           macro avg       0.20      0.21      0.18      1694
        weighted avg       0.20      0.21      0.18      1694

======================== MODEL: paraphrase-MiniLM-L3-v2 ========================

Accuracy:  0.2031
F1 Score:  0.2025
Precision: 0.2037
Recall:    0.2031
Full classification report:
                      precision    recall  f1-score   support

     Billing inquiry       0.21      0.17      0.19       357
Cancellation request       0.20      0.21      0.20       327
     Product inquiry       0.17      0.17      0.17       316
      Refund request       0.23      0.21      0.22       345
     Technical issue       0.21      0.25      0.23       349

            accuracy                           0.20      1694
           macro avg       0.20      0.20      0.20      1694
        weighted avg       0.20      0.20      0.20      1694

======================== MODEL: bge-small-en ========================

Accuracy:  0.1960
F1 Score:  0.1813
Precision: 0.1996
Recall:    0.1960
Full classification report:
                      precision    recall  f1-score   support

     Billing inquiry       0.19      0.09      0.12       357
Cancellation request       0.20      0.09      0.13       327
     Product inquiry       0.17      0.31      0.22       316
      Refund request       0.22      0.14      0.17       345
     Technical issue       0.22      0.35      0.27       349

            accuracy                           0.20      1694
           macro avg       0.20      0.20      0.18      1694
        weighted avg       0.20      0.20      0.18      1694

======================== MODEL: paraphrase-MiniLM-L6-v2 ========================

Accuracy:  0.1983
F1 Score:  0.1924
Precision: 0.1995
Recall:    0.1983
Full classification report:
                      precision    recall  f1-score   support

     Billing inquiry       0.21      0.10      0.13       357
Cancellation request       0.20      0.17      0.18       327
     Product inquiry       0.17      0.20      0.19       316
      Refund request       0.21      0.22      0.21       345
     Technical issue       0.21      0.30      0.25       349

            accuracy                           0.20      1694
           macro avg       0.20      0.20      0.19      1694
        weighted avg       0.20      0.20      0.19      1694

======================== MODEL: all-distilroberta-v1 ========================

Accuracy:  0.2007
F1 Score:  0.1967
Precision: 0.2007
Recall:    0.2007
Full classification report:
                      precision    recall  f1-score   support

     Billing inquiry       0.21      0.24      0.22       357
Cancellation request       0.19      0.13      0.16       327
     Product inquiry       0.20      0.26      0.23       316
      Refund request       0.21      0.13      0.16       345
     Technical issue       0.19      0.23      0.21       349

            accuracy                           0.20      1694
           macro avg       0.20      0.20      0.20      1694
        weighted avg       0.20      0.20      0.20      1694


===================== AGGREGATE BENCHMARK RESULTS =====================
Model: all-MiniLM-L6-v2
  accuracy: 0.1936
  f1_score: 0.1703
  precision: 0.1928
  recall: 0.1936
----------------------------------------------------------------------
Model: all-mpnet-base-v2
  accuracy: 0.2054
  f1_score: 0.1820
  precision: 0.2042
  recall: 0.2054
----------------------------------------------------------------------
Model: paraphrase-MiniLM-L3-v2
  accuracy: 0.2031
  f1_score: 0.2025
  precision: 0.2037
  recall: 0.2031
----------------------------------------------------------------------
Model: bge-small-en
  accuracy: 0.1960
  f1_score: 0.1813
  precision: 0.1996
  recall: 0.1960
----------------------------------------------------------------------
Model: paraphrase-MiniLM-L6-v2
  accuracy: 0.1983
  f1_score: 0.1924
  precision: 0.1995
  recall: 0.1983
----------------------------------------------------------------------
Model: all-distilroberta-v1
  accuracy: 0.2007
  f1_score: 0.1967
  precision: 0.2007
  recall: 0.2007
----------------------------------------------------------------------
```
---

## **8. Conclusion**

* **Transformers were used** to create embeddings for customer support tickets.  
* **Qdrant performed similarity search** to classify and retrieve similar tickets.  
* **Multiple models were evaluated**, with results comparing their effectiveness, and that to choose the best model for the project.


### The best model was **paraphrase-MiniLM-L3-v2** and that will be the one used in the main project.


