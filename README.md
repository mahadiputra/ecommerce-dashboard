# E-Commerce Data Analysis Dashboard 

## Setup Environment - Anaconda
```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```bash
# 1. Membuat virtual environment (venv)
python -m venv venv

# 2. Mengaktifkan virtual environment
# Untuk Windows:
venv\Scripts\activate
# Untuk macOS/Linux:
# source venv/bin/activate

# 3. Instalasi seluruh library yang dibutuhkan
pip install -r requirements.txt
```

## Run streamlit app
```bash
streamlit run dashboard/dashboard.py
```