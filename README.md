
# Create and activate a virtual environment (recommended)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
 
# To suppress any warnings
$env:PYTHONWARNINGS="ignore"

# Start (dev)
uvicorn app.main:app --reload --port 8000