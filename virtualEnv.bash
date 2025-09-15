python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

python site_searcher.py --url "https://example.com" --selector "a" --attr "href" --output out.csv