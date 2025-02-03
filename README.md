# **RAG-configurator-for-Local-LLMs** 🚀

### **Overview**
This project is a **configurator for Retrieval-Augmented Generation (RAG) pipelines** using local Large Language Models (LLMs). It enables users to create, evaluate, and interact with different RAG configurations dynamically through a user-friendly web interface.

The application allows:
- **Defining RAG configurations** with customizable retrieval models, embedding strategies, and LLMs.
- **Evaluating the performance** of different configurations using metrics such as relevancy, precision, and faithfulness.
- **Deploying a chatbot interface** powered by selected RAG configurations for real-time interactions.

---

## **Features**
✅ **Dynamic RAG Configuration:** Create, store, and manage multiple RAG setups.  
✅ **Evaluation Framework:** Measure retrieval and generation quality based on defined metrics.  
✅ **Local LLM Integration:** Use locally hosted Hagging face models thanks to LM Studio instead of API-based ones.  
✅ **Chatbot Interface:** Interact with a chatbot that utilizes selected configurations.  
✅ **User-Friendly UI:** Built with **Flask, Bootstrap, and Tailwind CSS** for easy navigation.  

---

## **Tech Stack**
### **Backend**
- **Flask** (Python) - Web framework to handle configuration management and chatbot functionalities.
- **SQLAlchemy** - ORM for handling database operations and configuration saving.
- **ChromaDB** - Vector database for retrieval of relevant contexts.
- **SentenceTransformers** - For embedding text queries and document retrieval.
- **Local LLMs** - Configurable with models like **Mistral-7B** and **Llama-2-7B**, Notice that you can upload other ones from LM Studio if you want.

### **Frontend**
- **HTML, CSS, JavaScript** - Standard web technologies.
- **Bootstrap 5** - For responsive UI design.
- **Tailwind CSS** - For additional modern styling.

---

## **Project Structure**
```
📂 RAG-configurator-for-Local-LLMs
│── 📂 Rag/                  # Core logic (retriever, generator, evaluator)
│── 📂 instance/             # SQLite database instance
│── 📂 static/               # CSS, JS
│── 📂 templates/            # HTML templates
│── .env                     # Environment variables (API keys, paths)
│── .gitignore                
│── README.md                 # Project documentation
│── create_db.py              # Script to initialize the database
│── main.py                   # Flask application entry point
│── requirements.txt           # Dependencies for the project
```

---

## **Setup & Installation**
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/oussamaakdi/RAG-configurator-for-Local-LLMs.git
cd RAG-configurator-for-Local-LLMs
```

### **2️⃣ Set Up a Virtual Environment**
```bash
python -m venv env
source env/bin/activate  # On Windows use: env\Scripts\activate
```

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4️⃣ Install LM Studio & Set Up Local LLM**
Before running the application, you must install **LM Studio**, download a **local LLM**, and ensure it is served correctly.

#### **Install LM Studio**
- Download and install **LM Studio** from [lmstudio.ai](https://lmstudio.ai/).
- Open LM Studio after installation.

#### **Download a Local LLM**
- Inside LM Studio, navigate to the **Models** tab.
- Search for models :
  - `mistral-7b-instruct-v0.3`
  - `llama-2-7b-chat-finetune-qa-meta`
- Click **Download** and wait for the model to install.

#### **Serve the Model on Localhost**
- After downloading the model, go to the **Server** tab.
- Select the installed LLM and start the local API server.
- Ensure the server is running at **http://localhost:port**.
- Copy the API URL for later use.

### **5️⃣ Configure Environment Variables**
Create a `.env` file in the project root and define the API URL:
```bash
echo "url=http://localhost:5001" > .env
```
Alternatively, manually edit `.env`:
```env
url= "http://localhost:5001..."
```
Make sure the **URL matches the LM Studio API server**.

### **6️⃣ Initialize the Database**
```bash
python create_db.py
```

### **7️⃣ Replace `Chunks.csv` and `testset.csv` with Your Data**
Before running the application, you need to replace the default datasets in the **Rag** folder with your own.

#### **File Descriptions:**
- **`Chunks.csv`**: This file contains **preprocessed text chunks** that the retriever will use.
- **`testset.csv`**: This file contains **test queries and their ground truth answers** for evaluation.

#### **File Format Requirements:**
- **`Chunks.csv`** should have at least one column:
  - `"Content"` → Contains text chunks used by the retriever.
  
- **`testset.csv`** should contain:
  - `"Question"` → Test queries used for evaluation.
  - `"Ground Truth"` → Expected responses that will be compared with model outputs.

#### **Steps to Replace These Files:**
1. Navigate to the `Rag/` directory.
2. Delete the existing `Chunks.csv` and `testset.csv`.
3. Copy and paste your custom datasets into the folder.
4. Ensure they follow the correct column formats mentioned above.



### **8️⃣ Run the Application**
```bash
python main.py
```

### **🔟 Access the Web Interface**
Open [http://127.0.0.1:5000...](http://127.0.0.1:5000) in your browser.

---

## **Usage Guide**
1️⃣ **Create a new RAG Configuration** via the UI.  
2️⃣ **Evaluate the Configuration** to measure retrieval and generation quality.  
3️⃣ **Use a Configuration in Chatbot Mode** and interact with local LLMs.  

---



## **License**
🔓 **MIT License** - Free to use, modify, and distribute.  
