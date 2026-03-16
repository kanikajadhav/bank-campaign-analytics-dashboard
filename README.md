# 📊 Bank Marketing Campaign Analytics Dashboard

An interactive data analytics dashboard built to analyse the performance of a bank's telemarketing campaigns — identifying which customer segments, contact methods, and call strategies drive the highest subscription conversion rates.

> Built as part of a Data Analyst portfolio project demonstrating end-to-end analytics skills relevant to campaign performance reporting.

---

## 🚀 Live Demo

> _Add your Streamlit Cloud link here after deployment_

---

## 📌 Key Features

- **KPI Overview** — Total contacts, conversions, conversion rate, avg call duration at a glance
- **Interactive Filters** — Filter by job category, month, contact method, and age range via sidebar
- **SQL-Powered Data Layer** — All aggregations run via SQLite SQL queries on the loaded dataset
- **6 Analytical Charts** — Conversion by job, monthly trends, age group response, contact method effectiveness, call duration distribution, campaign call frequency analysis
- **Live SQL Explorer** — Write and run your own SQL queries directly against the dataset from the UI
- **Raw Data Preview** — Inspect filtered records inline

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Data Collection & Prep | Python, Pandas |
| Data Storage & Querying | SQLite, SQL (CTEs, aggregations, filters) |
| Dashboard & UI | Streamlit |
| Visualisation | Plotly Express, Plotly Graph Objects |
| Dataset | [UCI Bank Marketing Dataset](https://archive.ics.uci.edu/ml/datasets/bank+marketing) |

---

## 📂 Project Structure

```
campaign_dashboard/
│
├── app.py               # Main Streamlit dashboard application
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## ⚙️ How to Run Locally

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/campaign-analytics-dashboard.git
cd campaign-analytics-dashboard
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the dashboard**
```bash
streamlit run app.py
```

The app will automatically download the UCI Bank Marketing dataset on first run. No manual data download needed.

---

## 📊 Dataset

**UCI Bank Marketing Dataset** — relates to direct phone call marketing campaigns of a Portuguese banking institution.

- **41,188 records**, 20 features
- Target variable: whether the client subscribed to a term deposit (`yes`/`no`)
- Features include: age, job, marital status, education, contact method, campaign call count, call duration, and economic indicators

---

## 🔍 Key Insights from the Analysis

- **Retired and student** segments show significantly higher conversion rates despite lower contact volumes
- **Cellular contact** outperforms telephone contact consistently across all job categories  
- **Call duration** is strongly correlated with conversion — calls under 100s rarely convert
- **March, September, October, December** show the highest conversion rates despite lower campaign volumes
- **1–3 calls** yield the best conversion efficiency; beyond 5 calls, returns diminish sharply

---

## 🧠 Skills Demonstrated

- Data collection, cleaning, and preparation using Pandas
- SQL query design — aggregations, filtering, grouping, derived metrics
- Dashboard design and performance reporting for non-technical stakeholders
- Translating data findings into actionable campaign recommendations
- End-to-end project documentation and deployment

---

## 👤 Author

**Your Name**  
[LinkedIn](https://linkedin.com/in/yourprofile) · [GitHub](https://github.com/yourusername)
