# Falcon 9 capstone analysis

Run the six executed notebooks from this directory in numeric order. Supporting
Python sources, datasets and validation records are under capstone-checks/.
The final report is capstone-complete-analysis-v2.pdf (40 slides); the PPTX is
editable. Install pandas, numpy, matplotlib, seaborn, ipython-sql, sqlalchemy,
scikit-learn, folium, plotly, dash, nbformat, nbclient, ipykernel, requests and
beautifulsoup4 as needed.

The retained data cover separate cohorts: 90 API/reference launches, 101 SQL
records, and 56 map/dashboard records. Class 1 includes True Ocean outcomes,
which do not establish physical recovery for reuse. A live metadata lookup
failed; the collection notebook documents its historical snapshot fallback.
The additional Falcon9_WebScraping_Verified.ipynb completes the required
Wikipedia HTML request, header extraction, 121-row record parsing and CSV export
on the real 9 June 2021 revision (HTTP 200, no synthetic fixture). Its outputs
and provenance checks are saved; spacex_web_scraped.csv and
webscraping-validation.json contain the data and checks. Run this standalone
notebook from this directory. Five unavailable/classified payload masses remain
missing. Its 121-row cohort is separate from the other analyses above.

Local Folium HTML preview was
blocked by browser policy; the map source and generated HTML are retained.

The notebooks and reports are actual saved computations, not a claim that the
protected final Coursera assessment has been submitted or graded.
