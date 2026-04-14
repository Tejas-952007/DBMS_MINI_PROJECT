import pandas as pd
import re
from db import get_db, COLLECTION_NAME

def _build_match_stage(author_filter, content_type_filter):
    match = {}
    if author_filter:
        match["author"] = {"$in": author_filter}
    if content_type_filter:
        match["content_type"] = {"$in": content_type_filter}
    return match

def get_reaction_totals(author_filter=None, content_type_filter=None):
    db = get_db()
    pipeline = []
    
    match_stage = _build_match_stage(author_filter, content_type_filter)
    if match_stage:
        pipeline.append({"$match": match_stage})
        
    pipeline.extend([
        {"$project": {"reactions": {"$objectToArray": "$engagement.reactions"}}},
        {"$unwind": "$reactions"},
        {"$group": {"_id": "$reactions.k", "total": {"$sum": "$reactions.v"}}}
    ])
    result = list(db[COLLECTION_NAME].aggregate(pipeline))
    return pd.DataFrame(result).rename(columns={"_id": "Reaction Type", "total": "Count"})

def get_top_users(author_filter=None, content_type_filter=None):
    db = get_db()
    pipeline = []
    
    match_stage = _build_match_stage(author_filter, content_type_filter)
    if match_stage:
        pipeline.append({"$match": match_stage})
        
    pipeline.extend([
        {"$group": {"_id": "$author", 
                    "total_views": {"$sum": "$engagement.view_count"},
                    "total_shares": {"$sum": "$engagement.share_count"}}},
        {"$sort": {"total_views": -1}},
        {"$limit": 10}
    ])
    result = list(db[COLLECTION_NAME].aggregate(pipeline))
    return pd.DataFrame(result).rename(columns={"_id": "Author", "total_views": "Total Views", "total_shares": "Total Shares"})

def get_trends(author_filter=None, content_type_filter=None):
    db = get_db()
    pipeline = []
    
    match_stage = _build_match_stage(author_filter, content_type_filter)
    if match_stage:
        pipeline.append({"$match": match_stage})
        
    pipeline.extend([
        {"$project": {"date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}, "views": "$engagement.view_count"}},
        {"$group": {"_id": "$date", "total_views": {"$sum": "$views"}}},
        {"$sort": {"_id": 1}}
    ])
    result = list(db[COLLECTION_NAME].aggregate(pipeline))
    return pd.DataFrame(result).rename(columns={"_id": "Date", "total_views": "Total Views"})

def get_engagement_by_content_type(author_filter=None, content_type_filter=None):
    db = get_db()
    pipeline = []
    
    match_stage = _build_match_stage(author_filter, content_type_filter)
    if match_stage:
        pipeline.append({"$match": match_stage})
        
    pipeline.extend([
        {"$group": {"_id": "$content_type", "avg_views": {"$avg": "$engagement.view_count"}, "total": {"$sum": 1}}}
    ])
    result = list(db[COLLECTION_NAME].aggregate(pipeline))
    return pd.DataFrame(result).rename(columns={"_id": "Content Type", "avg_views": "Average Views", "total": "Total Posts"})

def get_heatmap_data(author_filter=None, content_type_filter=None):
    db = get_db()
    pipeline = []
    
    match_stage = _build_match_stage(author_filter, content_type_filter)
    if match_stage:
        pipeline.append({"$match": match_stage})
        
    pipeline.extend([
        {"$project": {
            "hour": {"$hour": "$created_at"},
            "content_type": "$content_type"
        }},
        {"$group": {
            "_id": {"hour": "$hour", "content_type": "$content_type"},
            "count": {"$sum": 1}
        }}
    ])
    result = list(db[COLLECTION_NAME].aggregate(pipeline))
    
    flat_data = []
    for r in result:
        flat_data.append({
            "Hour": r["_id"]["hour"],
            "Content Type": r["_id"]["content_type"],
            "Count": r["count"]
        })
    df = pd.DataFrame(flat_data)
    if not df.empty:
        return df.pivot(index="Hour", columns="Content Type", values="Count").fillna(0)
    return pd.DataFrame()

def get_all_posts(author_filter=None, content_type_filter=None):
    db = get_db()
    match_stage = _build_match_stage(author_filter, content_type_filter)
    cursor = db[COLLECTION_NAME].find(match_stage, {"_id": 0})
    return pd.DataFrame(list(cursor))

def get_author_hashtag_edges(author_filter=None, content_type_filter=None):
    df = get_all_posts(author_filter, content_type_filter)
    if df.empty: return pd.DataFrame()
    
    edges = []
    for _, row in df.iterrows():
        author = row.get("author")
        text = ""
        if isinstance(row.get("content"), dict):
            text = row["content"].get("text", "")
        tags = re.findall(r"(#\w+)", text)
        for tag in tags:
            edges.append({"Author": author, "Hashtag": tag})
    return pd.DataFrame(edges)
