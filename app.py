import streamlit as st
import pandas as pd
from db import insert_dummy_data, get_db, COLLECTION_NAME
from analysis import get_all_posts, get_top_users, get_reaction_totals, get_engagement_by_content_type
from charts import (
    plot_reaction_bar, plot_trends_line, plot_top_users_bar, 
    plot_engagement_bubble, plot_sentiment_heatmap, plot_users_network
)

st.set_page_config(page_title="Social Media Analyzer", layout="wide", page_icon="📊")

st.title("🚀 Social Media Analyzer - SPPU DBMS Mini Project")

# --- INITIAL DB CHECK ---
db_online = False
db = None
try:
    db = get_db()
    db.command('ping')
    count = db[COLLECTION_NAME].count_documents({})
    if count == 0:
        st.warning("⚠️ No data found in MongoDB. Hit the 'Reload Static Dummy Data' button in the sidebar.")
    db_online = True
except Exception as e:
    st.error(f"⚠️ Cannot connect to MongoDB. Is the Daemon running? (Error: {e})")
    st.info("Check `db.py` to configure your MongoDB connection cluster.")

# Fetch distinct values if DB is online
all_authors = []
all_content_types = []
if db_online and count > 0:
    all_authors = db[COLLECTION_NAME].distinct("author")
    all_content_types = db[COLLECTION_NAME].distinct("content_type")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Control Pannel")
    
    st.info("Changes here instantly update all charts & queries!")
    selected_authors = st.multiselect("Filter by Authors", all_authors, default=[])
    selected_content_types = st.multiselect("Filter by Content Type", all_content_types, default=[])

    st.markdown("---")
    st.subheader("🛠️ Database Admin")
    if st.button("🔄 Reload 30+ Posts Dummy Data"):
        with st.spinner("Inserting dummy social media JSON into MongoDB..."):
            try:
                insert_dummy_data()
                st.success("Dummy Data successfully loaded!")
                st.rerun()
            except Exception as e:
                st.error(f"Make sure MongoDB is running. Error: {e}")
                
    st.markdown("---")
    st.subheader("Filter Output (Live Query Demo)")
    query_selector = st.selectbox(
        "Select insight to view raw data:",
        ("Top Users", "Reaction Totals", "Views by Content Type", "All Raw Posts")
    )
    
    st.markdown("---")
    st.write("DBMS Project")

if not db_online or count == 0:
    st.stop()

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["👁️ Overview", "📈 Analytics", "🔍 Live Query"])

# Pass global filters strictly to all analytical functions
af = selected_authors if selected_authors else None
cf = selected_content_types if selected_content_types else None

with tab1:
    st.header("Dashboard Overview")
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_sentiment_heatmap(af, cf), use_container_width=True)
        st.plotly_chart(plot_trends_line(af, cf), use_container_width=True)
        
    with col2:
        st.plotly_chart(plot_users_network(af, cf), use_container_width=True)
        st.plotly_chart(plot_engagement_bubble(af, cf), use_container_width=True)

with tab2:
    st.header("Detailed Analytics")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_reaction_bar(af, cf), use_container_width=True)
    with col2:
        st.plotly_chart(plot_top_users_bar(af, cf), use_container_width=True)

with tab3:
    st.header("Live Database Queries")
    st.markdown(f"**Selected Query:** `{query_selector}`")
    st.markdown(f"*Applying Global Filters -> Authors: {af or 'All'}, Content Tools: {cf or 'All'}*")
    
    if query_selector == "All Raw Posts":
        st.dataframe(get_all_posts(af, cf), use_container_width=True)
    elif query_selector == "Top Users":
        st.dataframe(get_top_users(af, cf), use_container_width=True)
    elif query_selector == "Reaction Totals":
        st.dataframe(get_reaction_totals(af, cf), use_container_width=True)
    elif query_selector == "Views by Content Type":
        st.dataframe(get_engagement_by_content_type(af, cf), use_container_width=True)
        
st.markdown("---")
st.caption("DBMS Project")
