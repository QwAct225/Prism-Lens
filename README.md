# PrismLens

PrismLens is a comprehensive research visualization system designed to analyze and map MIT research trajectories using papers from the arXiv repository. By leveraging advanced topic modeling techniques with BERTopic, this project aims to provide insights into research trends, emerging topics, and evolution of scientific discourse within MIT-affiliated publications.

## Project Structure
```
Prism-Lens/
│
├── src/                       # Source code
│   └── data/                  # Data processing modules
│       ├── __init__.py
│       ├── preprocessing.py   # Text preprocessing functions
│       └── scraper.py         # ArXiv data collection
│
├── venv/                      # Virtual environment
│   ├── Lib/
│   │   └── site-packages/
│   └── Scripts/
│       ├── activate
│       ├── activate.bat
│       ├── Activate.ps1
│       ├── deactivate.bat
│       ├── pip.exe
│       ├── pip3.12.exe
│       ├── pip3.exe
│       ├── python.exe
│       └── pythonw.exe
│
├── arxiv_titles_raw.csv       # Raw dataset
├── README.md                  # Project documentation
├── requirements.txt           # Dependencies
├── run_scraper.py             # Script to run the scraper
└── pyvenv.cfg                 # Python venv configuration
```

## Getting Started

1. **Clone the repository**

    ```bash
    git clone https://github.com/your-username/prism-lens.git
    cd prism-lens
    ```

2. **Prerequisites**

    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
    ```

3. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    python -m nltk.downloader stopwords wordnet
    ```
   
4. **Running the Scraper**

    ```bash
    python run_scraper.py
    ```
## Technologies

- **Python**: Primary programming language
- **BeautifulSoup/Selenium**: Web scraping framework for ArXiv data collection
- **NLTK**: Natural Language Toolkit for text preprocessing and cleaning
- **BERTopic**: State-of-the-art topic modeling based on BERT embeddings

