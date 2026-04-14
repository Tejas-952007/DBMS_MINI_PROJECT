import streamlit as st
import pandas as pd
from db import insert_dummy_data, get_db, COLLECTION_NAME
from analysis import get_all_posts, get_top_users, get_reaction_totals, get_engagement_by_content_type
from charts import (
    plot_reaction_bar, plot_trends_line, plot_top_users_bar, 
    plot_engagement_bubble, plot_sentiment_heatmap, plot_users_network
)

st.set_page_config(page_title="Social Media Analyzer", layout="wide", page_icon="📊")

# --- INITIAL DB CHECK ---
db_online = False
db = None
count = 0
try:
    db = get_db()
    db.command('ping')
    count = db[COLLECTION_NAME].count_documents({})
    db_online = True
except Exception as e:
    pass

all_authors = []
all_content_types = []
if db_online and count > 0:
    all_authors = db[COLLECTION_NAME].distinct("author")
    all_content_types = db[COLLECTION_NAME].distinct("content_type")

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to:", ["Home", "EDA & Data Insights", "Project Summary"])
    st.markdown("---")

if page == "Home":
    st.title("🚀 Social Media Analyzer - DBMS Project")
    st.header("Project Details")
    st.markdown("""
    **Topic:** Social Media Analysis using MongoDB  
    """)
    
    st.subheader("❓ Problem Statement")
    st.markdown("""
    Modern social media platforms generate massive volumes of unstructured and semi-structured data. Traditional relational databases struggle to efficiently store, query, and analyze this varied data (text, arrays of media, complex engagement metrics). 
    
    The problem is to design a NoSQL schema and build a real-time analytics dashboard to prove MongoDB's capability in handling large-scale social media data processing efficiently.
    """)
    
    st.subheader("⚙️ Project Workflow")
    st.markdown("""
    1. **Data Ingestion**: Insert and manage unstructured social media payloads into MongoDB `social_media_db`.
    2. **NoSQL Aggregations**: Utilize native MongoDB `$match`, `$group`, and `$project` aggregation pipelines for efficient data processing.
    3. **Data Analysis**: Extract key metrics like view counts, top authors, content types, and time-based trends.
    4. **Visualization**: Connect Python Streamlit to present dynamic insights via Plotly charts in real time.
    """)
    
    if not db_online or count == 0:
        st.warning("⚠️ No data found in MongoDB or server offline.")
    st.subheader("🛠️ Database Admin")
    if st.button("🔄 Reload 30+ Posts Dummy Data"):
        with st.spinner("Inserting dummy social media JSON into MongoDB..."):
            try:
                insert_dummy_data()
                st.success("Dummy Data successfully loaded!")
                st.rerun()
            except Exception as e:
                st.error(f"Make sure MongoDB is running. Error: {e}")

elif page == "EDA & Data Insights":
    st.title("📈 EDA & Data Insights")
    if not db_online or count == 0:
        st.error("Please load data from the Home page first.")
        st.stop()
        
    with st.sidebar:
        st.header("Control Panel")
        st.info("Changes here instantly update all charts & queries!")
        selected_authors = st.multiselect("Filter by Authors", all_authors, default=[])
        selected_content_types = st.multiselect("Filter by Content Type", all_content_types, default=[])
        
        st.markdown("---")
        st.subheader("Filter Output (Live Query Demo)")
        query_selector = st.selectbox(
            "Select insight to view raw data:",
            ("Top Users", "Reaction Totals", "Views by Content Type", "All Raw Posts")
        )

    # Pass global filters strictly to all analytical functions
    af = selected_authors if selected_authors else None
    cf = selected_content_types if selected_content_types else None
    
    tab1, tab2, tab3 = st.tabs(["👁️ Overview Visualizations", "📈 Detailed Analytics", "🔍 Live Database Query"])
    
    with tab1:
        st.header("Dashboard Overview")
        st.markdown("Welcome to the Exploratory Data Analysis section. Here we break down patterns that help explain what drives social media engagement on our platform.")
        
        # Heatmap
        st.markdown("### 🔍 Activity Heatmap (Hour vs Content Type)")
        st.plotly_chart(plot_sentiment_heatmap(af, cf), use_container_width=True)
        with st.expander("📝 Insight (Click to expand)"):
            st.markdown("""
            **Insight:**
            
            **What We Analyzed:**
            We created a heatmap to map out posting activity times across the hours of the day according to the content type.
            
            **Key Observations:**
            - **Concentration:** Both image and video (media) tend to have concentrated peaks in specific active hours (usually evening).
            - **Distribution:** Text content is more uniformly distributed throughout the day.
            
            **Business Implications:**
            - Content Schedulers should time high-effort media posts during these core peak hours for maximum ROI.
            - Algorithm teams can prioritize scaling server bandwidth for heavy media precisely during peak zones.
            """)

        # Trends Line
        st.markdown("### 🔍 Total Views Over Time")
        st.plotly_chart(plot_trends_line(af, cf), use_container_width=True)
        with st.expander("📝 Insight (Click to expand)"):
            st.markdown("""
            **Insight:**
            
            **What We Analyzed:**
            A time-series plot comparing the total volume of daily views network-wide against publication dates.
            
            **Key Observations:**
            - Spikes occur on particular dates, representing sudden virality.
            - The baseline is highly variable, mirroring organic and unpredictable network engagement.
            
            **Business Implications:**
            - Provides crucial data to connect real-world events to user behaviors.
            - Moderation teams can anticipate traffic load and scale servers when the initial trend curve starts pointing steeply upwards.
            """)
            
        # Network
        st.markdown("### 🔍 Author-Hashtag Network Topology")
        st.plotly_chart(plot_users_network(af, cf), use_container_width=True)
        with st.expander("📝 Insight (Click to expand)"):
            st.markdown("""
            **Insight:**
            
            **What We Analyzed:**
            A force-directed graph illustrating the complex web of which authors use which hashtags.
            
            **Key Observations:**
            - Several "hub" hashtags (e.g., #gaming, #pizza) connect vastly different user groups.
            - Certain authors are highly isolated, utilizing niche tags, while others sit in the center of the community graph.
            
            **Business Implications:**
            - **Targeting:** Marketing teams can use high-centrality hashtags to reach entirely distinct user demographics simultaneously.
            - **Recommendation Engine:** A&R/Algorithms can recommend users to one another if they share a structural path to the same tag.
            """)
            
        # Bubble
        st.markdown("### 🔍 Engagement by Content Type")
        st.plotly_chart(plot_engagement_bubble(af, cf), use_container_width=True)
        with st.expander("📝 Insight (Click to expand)"):
            st.markdown("""
            **Insight:**
            
            **What We Analyzed:**
            We plotted average views against content types. The bubble size represents the total volume of that type of post.
            
            **Key Observations:**
            - **Skewed Distribution:** Although Text may represent a high volume of posts, `Media` overwhelmingly drives higher average views.
            - This mirrors the "winner-takes-most" trend observed widely on digital platforms.
            
            **Business Implications:**
            - Creators should be strongly incentivized to use rich media over simple link sharing.
            - Platform UI should be re-optimized to display media elements prominently to maximize global watch time.
            """)
            
    with tab2:
        st.header("Detailed Analytics")
        
        # Reaction Bar
        st.markdown("### 🔍 Distribution of Reaction Types")
        st.plotly_chart(plot_reaction_bar(af, cf), use_container_width=True)
        with st.expander("📝 Insight (Click to expand)"):
            st.markdown("""
            **Insight:**
            
            **What We Analyzed:**
            A breakdown of raw sentiment (reactions) aggregated natively in MongoDB using `$objectToArray`.
            
            **Key Observations:**
            - `Like` and `Love` reactions heavily outnumber negative sentiments (`Sad`, `Angry`).
            - The distribution is right-skewed, showing generic positive affirmation is easier to earn than complex engagement.
            
            **Business Implications:**
            - Models predicting "viral potential" should apply heavier weights on rare reactions (like `Wow` or `Share`) over simple likes, as they indicate a much stronger breakout signal.
            """)
            
        # Top Users Bar
        st.markdown("### 🔍 Top Influencers by Network Views")
        st.plotly_chart(plot_top_users_bar(af, cf), use_container_width=True)
        with st.expander("📝 Insight (Click to expand)"):
            st.markdown("""
            **Insight:**
            
            **What We Analyzed:**
            We grouped the database by user to find the ultimate drivers of traffic. Color depth represents raw Share volume.
            
            **Key Observations:**
            - Highly concentrated Power-Law curve: A tiny fraction of users generates the vast majority of network traffic.
            - High Views don't strictly correlate with High Shares; some creators are highly viewed but rarely shared.
            
            **Business Implications:**
            - **Monetization:** These exact power users should be the immediate targets for ad-revenue sharing or creator-fund programs.
            - Focus early retention strategies on acquiring these specific demographics.
            """)
            
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

elif page == "Project Summary":
    st.title("📝 Project Summary")
    st.markdown("""
    ### Summary of Findings
    Through our exploratory data analysis, we observed that:
    - **Media Content** consistently drives higher engagement (views and reactions) compared to simple text posts.
    - User networks form clusters based on prominent hashtags, with a few top users acting as major hubs of influence.
    - Engagement metrics fluctuate significantly based on the hour of posting.
    
    ### Technologies Used
    - **Database:** MongoDB (NoSQL) for flexible schema storage and aggregation pipelines.
    - **Backend/Analysis:** Python, Pandas.
    - **Frontend:** Streamlit for functional multi-page web layout.
    - **Visualizations:** Plotly Interactive Charts.
    
    ### Future Scope
    - Implementing Natural Language Processing (NLP) models to automatically classify sentiment of text inputs.
    - Expanding the MongoDB architecture to span multiple related collections (Users, Comments, Stores, Reels) mimicking enterprise schemas.
    - Building a live dashboard via Apache Kafka streaming to analyze posts in ultra-real-time.
    """)

st.sidebar.markdown("---")
st.sidebar.caption("DBMS Project")
