# Food Delivery AI Agent — Interim Report

An LLM-powered SQL agent (OpenAI + LangChain) that answers natural-language
business questions over a synthetic food-delivery SQLite database.

The deliverable is **`interim_report.ipynb`**, structured to match the course
rubric one-to-one:

| # | Section | Marks |
|---|---------|-------|
| 1 | Loading and Setting Up the LLM | 8 |
| 2 | Question Answering LLM | 10 |
| 3 | Build SQL Agent | 16 |
| 4 | Business Report Quality | 6 |

## Project layout

```
food-delivery-agent/
├── create_database.py     # generates the SQLite DB (stdlib only, deterministic)
├── data/food_delivery.db  # 5 related tables: customers, restaurants,
│                          #   delivery_agents, orders, order_items
├── interim_report.ipynb   # ← main deliverable (all 4 rubric sections)
├── requirements.txt
├── .env.example           # copy to .env and add your OPENAI_API_KEY
└── README.md
```

## Setup (already done once, repeat on a new machine)

```bash
# 1. Create + activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Register the venv as a Jupyter kernel
python -m ipykernel install --user --name food-delivery \
       --display-name "Python 3 (food-delivery)"

# 4. (Re)generate the database — optional, it's already committed
python create_database.py

# 5. Add your API key
cp .env.example .env               # then edit .env and paste your real key
```

## Running

```bash
source .venv/bin/activate
jupyter notebook interim_report.ipynb
```

In Jupyter, select the **"Python 3 (food-delivery)"** kernel, then run the
cells top to bottom.

## Notes

- **API key:** required only for Sections 1–3 (any cell that calls the LLM).
  Section 4 is a written report and needs no key.
- **Reproducibility:** the database uses a fixed random seed; the LLM is set to
  `temperature=0` with a fixed `seed`.
- **The DB is independent of the LLM** — you can run `create_database.py` and the
  direct-SQL verification cells with no API key at all.
- After running the LLM cells, replace the *"fill in after running"* commentary
  in Sections 2 and 3 with observations about the actual outputs you got — that
  commentary is exactly what the rubric grades.
