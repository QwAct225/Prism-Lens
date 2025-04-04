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
├── .gitignore                 # Ignore unnecessary file
├── arxiv_papers_raw.csv       # Raw dataset
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
     
5. **Running API Locally**

    ```bash
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
    ```
     
6. **Using Docker Build and start the containers**

    ```bash
    docker-compose up --build
    ```
   
6. **Access API Endpoint (For Swagger UI documentation)**

   ```bash
    http://localhost:8000/docs
    ```
   or (For ReDoc documentation)
    ```bash
    http://localhost:8000/redoc
    ```
   
## API Examples

### 1. Get Dataset Statistics

**Request:**
GET http://localhost:8000/api/visualization/stats

**Response:**
```json
{
  "total_papers": 5839,
  "unique_authors": 12571,
  "average_authors_per_paper": 3.7355711594451106,
  "average_title_length": 69.38225723582805
}
```

### 2.  List Available Plots

**Request:**
GET http://localhost:8000/api/visualization/plots

**Response:**
```json
[
  "author_word_cloud.png",
  "authors_per_paper.png",
  "title_length_distribution.png",
  "top_authors.png",
  "word_cloud.png",
  "word_frequency.png"
]
```

### 3.  Get Papers with Search and Pagination

**Request:**
GET http://localhost:8000/api/visualization/papers?limit=2&search=quantum

**Response:**
```json
[
  {
    "title": "Quantum Computing: A New Era in Information Processing",
    "authors": ["Smith, John", "Johnson, Anna", "Zhang, Wei"],
    "cleaned_title": "quantum computing new era information processing",
    "cleaned_authors": ["smith john", "johnson anna", "zhang wei"]
  },
  {
    "title": "Advances in Quantum Field Theory Applications",
    "authors": ["Brown, Robert", "Davis, Emily"],
    "cleaned_title": "advances quantum field theory applications",
    "cleaned_authors": ["brown robert", "davis emily"]
  }
]
```

## Technologies

- **Python**: Primary programming language
- **BeautifulSoup**: Web scraping framework for ArXiv data collection
- **NLTK**: Natural Language Toolkit for text preprocessing and cleaning
- **BERTopic**: State-of-the-art topic modeling based on BERT embeddings
- **FastAPI**: Lightweight web framework used for building RESTful APIs
- **Docker**: Containerization tool used to package and deploy the application

