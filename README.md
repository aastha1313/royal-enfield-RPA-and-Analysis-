
# 🚗 Royal Enfield Data Extraction & Analytics Dashboard

## 📌 Project Overview

This project is an end-to-end data pipeline that:

1. Extracts vehicle data from the Royal Enfield website using browser automation
2. Stores the data in Excel
3. Builds an interactive analytics dashboard using Streamlit

The goal of this project is to demonstrate **web scraping, data processing, and data visualization** in a real-world use case.

---

## ⚙️ Tech Stack

* Python
* Playwright (Web Automation)
* Pandas (Data Processing)
* Streamlit (Dashboard)
* Plotly (Visualization)

---

## 🔍 Data Extraction (Playwright Automation)

The data extraction script uses Playwright to automate browser actions and collect:

* State-wise pricing
* Model details
* Variant (color) information
* On-road prices

### Key Features:

* Handles cookies and popups automatically
* Uses geolocation for accurate pricing (Delhi-based)
* Navigates through:

  * States → Cities → Models → Variants
* Extracts dynamic content (prices, variants)
* Saves structured data into Excel

### Output:

```plaintext
latest_data.xlsx
```

---

## 📊 Streamlit Dashboard

The dashboard provides interactive analytics on the extracted data.

### Features:

* Advanced filters:

  * State
  * OEM
  * Model
  * Variant
* Price range filtering
* KPI metrics:

  * Average Price
  * Minimum Price
  * Maximum Price
* Smart insights:

  * Cheapest variant
  * Most expensive variant
* Interactive charts:

  * Variant-wise price comparison
  * OEM distribution
  * Model-wise average pricing
* Top 5 expensive vehicles table

---

## 🌐 Live Application

👉 https://jvbjtztxblkimddlzywpcz.streamlit.app/

---

## 📁 Project Structure

```plaintext
project/
│
├── app.py                # Streamlit dashboard
├── main.py               # Playwright scraping script
├── utilities.py          # Helper functions
├── db_functions.py       # Data handling
├── logger_config.py      # Logging setup
├── latest_data.xlsx      # Extracted dataset
├── requirements.txt      # Dependencies
└── README.md
```

---

## ▶️ How to Run Locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run data extraction (optional)

```bash
python main.py
```

### 3. Run dashboard

```bash
streamlit run app.py
```

---

## 💡 Key Learnings

* Automating dynamic websites using Playwright
* Handling popups, retries, and dynamic elements
* Designing end-to-end data workflows
* Building interactive dashboards for business insights

---

## 🚀 Future Improvements

* Replace Excel with a live database
* Automate scheduled data updates
* Improve UI for production-level dashboard
* Add download/reporting features

---

## 👩‍💻 Author

Aastha Bhardwaj
