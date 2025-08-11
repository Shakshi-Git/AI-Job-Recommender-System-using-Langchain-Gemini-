# AI-Job-Recommender-System-using-Langchain-Gemini-

A Streamlit app that:

📄➡️📝 Extracts text from a PDF resume

🧠✨ Uses Gemini (via LangChain) to summarize, find skill gaps, suggest a roadmap, and generate job-search keywords

🔍🌐 (Optional) Fetches LinkedIn jobs via Apify using those keywords


**Features**

--PDF → Text with PyMuPDF (fitz) helper. 

--Gemini + LangChain chains for: Summary, Gaps, Roadmap, and Keywords (single LLM, reusable chains). 

--Streamlit UI: upload resume, view results, then query LinkedIn jobs. 

--LinkedIn jobs via Apify with sensible defaults (title, location, rows).


**Project Structure**
.
├─ app.py
├─ .gitignore
├─ .env                  # not committed (see .gitignore)
├─ src/
│  ├─ __init__.py
│  ├─ helper.py          # PDF → text
│  ├─ llm_gemini.py      # LangChain + Gemini chains
│  └─ job_api.py         # Apify LinkedIn fetch

--app.py – Streamlit UI: loads PDF, runs chains, displays results, and fetches jobs. 

--src/helper.py – extract_text_from_pdf(uploaded_file). 

--src/llm_gemini.py – cached Gemini LLM + chains (chain_summary, chain_gaps, chain_keywords, chain_roadmap). 

--src/job_api.py – fetch_linkedin_jobs(search_query, location, rows) calling an Apify actor. \


**Requirements**

--Python 3.10+ (recommended)

--Packages: streamlit, PyMuPDF, python-dotenv, apify-client, langchain, langchain-core, langchain-google-genai, google generativeai.


**Configuration**

Create .env in the project root (do not commit this file):

--GOOGLE_API_KEY=your_gemini_key_here

--APIFY_API_TOKEN=your_apify_token_here

--APIFY_LINKEDIN_ACTOR_ID=BHzefUZlZRKWxkTck

.gitignore already excludes .env and related secret files. 


**Notes**

--Gemini key is required for the LLM chains. The app loads the key and builds a cached Gemini client. 

--Apify token is required only if you want to fetch LinkedIn jobs. The call will raise a clear error if it’s missing.


**Run the App**

From your project folder (venv active):

python -m streamlit run app.py


**How It Works**

--Upload PDF → Extract text

--extract_text_from_pdf(uploaded_file) uses PyMuPDF to read the PDF stream. 


**Gemini (LangChain) analysis**

The app builds a single get_llm() instance and composes prompt chains to produce summary, gaps, and roadmap. 

 
 **Generate keywords → Fetch jobs**
 
--The keywords chain returns a comma-separated list; the app cleans it and runs the first few queries to avoid a single   overly long search term. 

--Each query is sent to fetch_linkedin_jobs(title, location, rows) and results are merged & de-duplicated. 

 --Jobs are then rendered with title, company, location, and link. 


**Apify actor input**

--The job fetcher builds a run_input with title, location, rows, sortby, freshness, and experience, then runs the actor and returns items from the dataset. 


**Security**

--Never commit .env (ignored by .gitignore). 

--Consider committing a safe template like .env.example with variable names only.


**Scripts & Commands**

# Create venv (Windows)

py -3 -m venv .venv

.\.venv\Scripts\Activate.ps1


# Install deps
pip install -U streamlit PyMuPDF python-dotenv apify-client \

  langchain langchain-core langchain-google-genai google-generativeai


# Run app

python -m streamlit run app.py




