# 🚀 Azure Multiple Choice Extractor

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/) 
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Azure](https://img.shields.io/badge/Azure-0078D4?style=for-the-badge&logo=azure&logoColor=white)](https://azure.microsoft.com/)
[![Azure AI Document Intelligence](https://img.shields.io/badge/Azure%20AI%20Document%20Intelligence-0078D4?style=for-the-badge&logo=azure&logoColor=white)](https://azure.microsoft.com/en-us/services/cognitive-services/document-intelligence/)

**Azure Multiple Choice Extractor** is an advanced Python script designed for:
- 📄 **Document Analysis** using Azure AI Document Intelligence
- ✍️ **Automated Answer Detection** from exam answer sheets

---

## 📂 Project Structure

```
Azure Multiple Choice Extractor/
├── LICENSE
├── README.md
├── test.py
└── get_jawaban_himpunan.py
```

- **test.py**
  Demonstrates the workflow: text & layout extraction from documents, followed by exam answer detection.
- **get_jawaban_himpunan.py**
  Implements the `get_jawaban_himpunan()` function to obtain student answers using a set-based approach.

---

## 🔧 Prerequisites

- Python 3.8 or newer
- Azure Cognitive Services Account & API Key
- Azure AI Document Intelligence SDK

---

## 🚀 Installation

1. **Clone** the repository:
   ```bash
   git clone https://github.com/AneKazek/azure-multiplechoice-extractor.git
   cd azure-multiplechoice-extractor
   ```

2. **Create a virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```
3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ Configuration

1. Create a `.env` file in the project root:

   ```text
   AZURE_ENDPOINT=https://<your-resource-name>.cognitiveservices.azure.com/
   AZURE_API_KEY=<your-api-key>
   ```
2. Ensure environment variables are loaded (if using a virtualenv, run `source .env`).

---

## 🎯 How to Use

1. **Document Analysis**

   ```bash
   python test.py --input path/to/document.pdf
   ```

   * Output: detected layout structure & text in the console.

2. **Exam Answer Detection**

   ```bash
   python get_jawaban_himpunan.py --input path/to/answer-sheet.pdf
   ```

   * Output: list of student answers based on question numbers.

---

## 🛠️ Code Example

```python
from azure.ai.documentintelligence import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from get_jawaban_himpunan import get_jawaban_himpunan

# Initialize client
client = DocumentAnalysisClient(
    endpoint="YOUR_ENDPOINT",
    credential=AzureKeyCredential("YOUR_API_KEY")
)

# Analyze document
poller = client.begin_analyze_document("prebuilt-document", "sample.pdf")
result = poller.result()

# Print text extraction results
for page in result.pages:
    print(page.lines)

# Detect answers
answers = get_jawaban_himpunan("answer-sheet.pdf")
print("Student answers:", answers)
```

---

## 🤝 Contributing

1. Fork this repository.
2. Create a new branch: `git checkout -b new-feature`
3. Commit your changes: `git commit -m "Add new feature"`
4. Push to your branch: `git push origin new-feature`
5. Open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.
