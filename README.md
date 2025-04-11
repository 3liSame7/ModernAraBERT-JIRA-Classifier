# 🧠 ModernAraBERT: Multilingual JIRA Ticket Classifier

A bilingual JIRA ticket classification system built using a fine-tuned **ModernBERT** model to classify both Arabic and English support tickets. Designed for internal use at Giza Systems and deployed via a Forge App for seamless integration into the JIRA workflow.

---

## 🚀 Project Overview

- **Goal:** Automate manual ticket classification in both Arabic & English to save time and reduce costs.
- **Challenge:** Legacy manual triaging process consumed ~80 hours/month and led to inconsistent tagging of tickets.
- **Solution:** A custom fine-tuned BERT model trained on 4M+ Arabic-centric examples with a controlled mix of English samples.

---

## 📊 Impact

✅ Reduced manual ticket classification effort by ~80 hours/month  
✅ Improved ticket classification accuracy and consistency  
✅ Seamlessly integrated into JIRA via Forge for real-time classification

---

## 🧪 Technical Highlights

- **Model:** ModernAraBERT (based on ModernBERT + Arabic language datasets)
- **Preprocessing:**  
  - Used *Farasa* for Arabic tokenization and segmentation  
  - Applied custom data cleaning and formatting for BERT input  
- **Fine-tuning:**  
  - Used Hugging Face Transformers to fine-tune the model on labeled historical tickets  
- **Deployment:**  
  - Packaged as a JIRA Forge App using JavaScript frontend  
  - Automatically classifies tickets on arrival

---

## 🛠️ Tools & Technologies

| Category         | Stack                                         |
|------------------|-----------------------------------------------|
| Languages        | Python, JavaScript                            |
| Libraries        | Transformers, Hugging Face, Farasa            |
| Platform         | JIRA Forge                                     |
| Model            | ModernBERT (custom-trained multilingual model)|
| Deployment       | Forge App (JIRA Integration)                  |

---

## 📁 Project Structure


