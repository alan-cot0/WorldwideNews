# WorldwideNews
Description TBA (The name of the project, at the moment, is a placeholder.)

## Setup / Running

### PostgreSQL (required before running the backend)
Install and start PostgreSQL via Homebrew:
```
brew install postgresql@16
brew services start postgresql@16
echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
createdb worldwidenews
```

### Database Setup & CSV Parsing
This loads the GDELT GKG CSV into PostgreSQL (creates tables automatically):
```
cd backend
pip3 install psycopg2-binary
python3 parse_csv.py
```

The script expects `data/gkg.csv` to be in the root of the repo. It populates two tables:
- `raw_articles` — quality-filtered GKG rows with country assignment
- `country_articles` — same rows with computed tone/count fields for relevancy scoring

The script expects `.env` file to be present in the backend folder. In should look like the following:
```
USER=youruser
PASS=yourpass
```

### Backend
```
cd backend
python3 -m venv .venv
pip install -r requirements.txt

# Runs fastapi server
fastapi dev main.py
```

### Frontend
```
cd frontend
npm i

# Runs vite dev server
npm run dev
```
