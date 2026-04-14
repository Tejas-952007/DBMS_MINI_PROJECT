# Social Media Analyzer 🚀
**DBMS Mini Project **

A full-stack Mini DBMS project using Python, Streamlit, and MongoDB to query and visualize social media engagement data in real-time.

## Project Structure
- `app.py`: Streamlit one-page interactive dashboard.
- `db.py`: Database connection and script to load dummy JSON data into MongoDB.
- `dummy_data.json`: Static dataset matching our custom schema.
- `analysis.py`: Data aggregations using native MongoDB queries (`db.collection.aggregate()`).
- `charts.py`: Plotly charts configurations directly connected to data analysis.

## Setup Instructions
1. Ensure **MongoDB** is running locally on port 27017, OR you can change the connection URI in `db.py` to point to a MongoDB Atlas cluster.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the dashboard:
   ```bash
   streamlit run app.py
   ```
4. Click the "Reload 30+ Posts Dummy Data" button in the sidebar to populate the database and view the charts!

## Database Details
- **Database**: `social_media_db`
- **Collection**: `posts`
- **Schema**:
   ```json
   {
       "author": "string",
       "created_at": "ISODate",
       "content_type": "string",
       "content": {
           "text": "string",
           "media": [{"type": "string", "url": "string"}]
       },
       "engagement": {
           "reactions": { "like": "int", "love": "int" },
           "share_count": "int",
           "view_count": "int"
       }
   }
   ```
