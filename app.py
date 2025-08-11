import streamlit as st
from src.helper import extract_text_from_pdf
from src.job_api import fetch_linkedin_jobs
from src.llm_gemini import get_llm, chain_summary, chain_gaps, chain_keywords, chain_roadmap

st.set_page_config(page_title="Job Recommender", layout="wide")
st.title("📄 AI Job Recommender (LangChain + Gemini)")
st.markdown("Upload your resume and get job recommendations based on your skills and experience from LinkedIn.")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
if not uploaded_file:
    st.info("Please upload a PDF resume to begin.")
    st.stop()

# Extract
with st.spinner("Extracting text from your resume..."):
    try:
        resume_text = extract_text_from_pdf(uploaded_file)
    except Exception as e:
        st.error("Failed to read PDF."); st.exception(e); st.stop()

# LLM & chains
llm = get_llm()
summary_chain  = chain_summary(llm)
gaps_chain     = chain_gaps(llm)
keywords_chain = chain_keywords(llm)
roadmap_chain  = chain_roadmap(llm)

# Summarize
with st.spinner("Summarizing your resume..."):
    try:
        summary = summary_chain.invoke({"resume_text": resume_text})
    except Exception as e:
        st.error("Failed to summarize resume."); st.exception(e); st.stop()

# Gaps
with st.spinner("Finding skill gaps..."):
    try:
        gaps = gaps_chain.invoke({"resume_text": resume_text})
    except Exception as e:
        st.error("Failed to analyze gaps."); st.exception(e); gaps = ""

# Roadmap
with st.spinner("Creating future roadmap..."):
    try:
        roadmap = roadmap_chain.invoke({"resume_text": resume_text})
    except Exception as e:
        st.error("Failed to create roadmap."); st.exception(e); roadmap = ""

# Display
st.markdown("---"); st.header("📑 Resume Summary")
st.markdown(f"<div style='background:#000;padding:15px;border-radius:10px;color:#fff'>{summary}</div>", unsafe_allow_html=True)
st.markdown("---"); st.header("🛠️ Skill Gaps & Missing Areas")
st.markdown(f"<div style='background:#000;padding:15px;border-radius:10px;color:#fff'>{gaps}</div>", unsafe_allow_html=True)
st.markdown("---"); st.header("🚀 Future Roadmap & Preparation Strategy")
st.markdown(f"<div style='background:#000;padding:15px;border-radius:10px;color:#fff'>{roadmap}</div>", unsafe_allow_html=True)
st.success("✅ Analysis Completed Successfully!")

# --- Jobs ---
st.markdown("---")
st.subheader("🔎 Job Recommendations")
location = st.text_input("Location", value="India")
rows = st.slider("Number of jobs", 10, 100, 60, 10)
show_debug = st.checkbox("Show debug info", value=False)

if st.button("Get LinkedIn Jobs"):
    # 1) Generate keywords
    with st.spinner("Generating search keywords..."):
        try:
            keywords = keywords_chain.invoke({"summary": summary})  # comma-separated string
        except Exception as e:
            st.error("Failed to generate keywords."); st.exception(e)
            keywords = ""

    # 2) Clean & pick a few queries (avoid sending the whole comma list as one query)
    raw = [k.strip() for k in (keywords or "").split(",") if k.strip()]
    # keep short, role-like phrases; drop dupes while preserving order
    seen = set()
    cleaned = []
    for k in raw:
        if 2 <= len(k) <= 40 and k.lower() not in seen:
            seen.add(k.lower())
            cleaned.append(k)
    queries = cleaned[:3] or ["Data Analyst"]  # fallback

    if show_debug:
        st.write("Raw keywords:", raw)
        st.write("Queries to run:", queries)

    # 3) Fetch for each query and merge
    with st.spinner(f"Fetching jobs from LinkedIn for: {', '.join(queries)}"):
        all_jobs = []
        for q in queries:
            try:
                jobs = fetch_linkedin_jobs(q, location=location, rows=int(rows))
                if show_debug: st.write(f"Query '{q}' -> {len(jobs)} jobs")
                all_jobs.extend(jobs or [])
            except Exception as e:
                st.warning(f"Query '{q}' failed: {e}")

    # 4) De-duplicate by link (or title+company fallback)
    uniq = []
    seen_keys = set()
    for j in all_jobs:
        key = j.get("link") or j.get("url") or (j.get("title",""), j.get("company") or j.get("companyName") or j.get("company_name"))
        if key in seen_keys: 
            continue
        seen_keys.add(key)
        uniq.append(j)

    linkedin_jobs = uniq

    # 5) Display
    st.markdown("---")
    st.header("💼 Top LinkedIn Jobs")
    st.caption(f"Found {len(linkedin_jobs)} unique jobs across {len(queries)} queries.")

    if linkedin_jobs:
        for job in linkedin_jobs:
            title = job.get("title", "")
            company = job.get("company") or job.get("company_name") or job.get("companyName", "")
            loc = job.get("location", "")
            link = job.get("link") or job.get("url")
            st.markdown(f"**{title}** at *{company}*")
            if loc:  st.markdown(f"- 📍 {loc}")
            if link: st.markdown(f"- 🔗 [View Job]({link})")
            st.markdown("---")
    else:
        st.warning("No LinkedIn jobs found. Try a simpler title (e.g., ‘Data Analyst’) or a different location.")