import os
import sqlite3

import requests
import streamlit as st

import database


ANALYSIS_API_URL = os.getenv(
	"ANALYSIS_API_URL",
	"http://127.0.0.1:8000/analyze",
)

st.set_page_config(page_title="Customer feedback analyzer", page_icon=":material/rate_review:")
st.title("Customer feedback analyzer")
database.init_db()

if "analysis_results" not in st.session_state:
	st.session_state.analysis_results = []
st.session_state.setdefault("results_source", "analysis")
st.session_state.setdefault("results_saved", False)

with st.form("feedback_analysis_form"):
	reviews_text = st.text_area(
		"Customer reviews",
		height=240,
		help="Enter one customer review per line.",
		placeholder="The delivery was quick and the packaging was great.\nThe product quality was disappointing.",
	)
	submitted = st.form_submit_button(
		"Analyze reviews",
		type="primary",
		icon=":material/analytics:",
	)

if submitted:
	reviews = [line.strip() for line in reviews_text.splitlines() if line.strip()]

	if not reviews:
		st.session_state.analysis_results = []
		st.session_state.results_saved = False
		st.warning("Enter at least one customer review to analyze.")
	else:
		results = []
		with st.spinner(f"Analyzing {len(reviews)} review(s)..."):
			for review in reviews:
				try:
					response = requests.post(
						ANALYSIS_API_URL,
						json={"text": review},
						timeout=30,
					)
					response.raise_for_status()
					analysis = response.json()
					if not isinstance(analysis, dict):
						raise ValueError("The analysis API returned an invalid response.")

					results.append(
						{
							"Review": review,
							"Label": analysis.get("label", ""),
							"Score": analysis.get("score"),
							"Theme": analysis.get("theme", ""),
							"Error": "",
						}
					)
				except (requests.RequestException, ValueError) as error:
					results.append(
						{
							"Review": review,
							"Label": "",
							"Score": None,
							"Theme": "",
							"Error": str(error),
						}
					)

		st.session_state.analysis_results = results
		st.session_state.results_source = "analysis"
		st.session_state.results_saved = False

saveable_results = [
	result for result in st.session_state.analysis_results if not result["Error"]
]
with st.container(horizontal=True):
	save_clicked = st.button(
		"Save results",
		key="save_results",
		icon=":material/save:",
		disabled=not saveable_results or st.session_state.results_saved,
	)
	load_clicked = st.button(
		"Load history",
		key="load_history",
		icon=":material/history:",
	)

if save_clicked:
	try:
		database.save_results(
			[
				{
					"review": result["Review"],
					"label": result["Label"],
					"score": result["Score"],
					"theme": result["Theme"],
				}
				for result in saveable_results
			]
		)
	except sqlite3.Error as error:
		st.error(f"Could not save history: {error}")
	else:
		st.session_state.results_saved = True
		st.success(f"Saved {len(saveable_results)} review(s) to history.")

if load_clicked:
	try:
		history = database.load_history()
	except sqlite3.Error as error:
		st.error(f"Could not load history: {error}")
	else:
		st.session_state.analysis_results = [
			{
				"Review": review,
				"Label": label,
				"Score": score,
				"Theme": theme,
				"Error": "",
			}
			for review, label, score, theme in history
		]
		st.session_state.results_source = "history"
		st.session_state.results_saved = True
		if history:
			st.success(f"Loaded {len(history)} saved review(s).")

if st.session_state.analysis_results:
	st.subheader(
		"Saved history"
		if st.session_state.results_source == "history"
		else "Analysis results"
	)
	st.dataframe(
		st.session_state.analysis_results,
		alt="Customer review analysis results",
		hide_index=True,
	)

elif st.session_state.results_source == "history" and load_clicked:
	st.info("No saved history yet.")
