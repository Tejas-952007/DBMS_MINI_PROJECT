import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import pandas as pd
from analysis import (
    get_reaction_totals, get_top_users, get_trends, 
    get_engagement_by_content_type, get_heatmap_data, get_author_hashtag_edges
)

def _empty_fig(title="Chart"):
    fig = go.Figure()
    fig.add_annotation(
        text="No data available for selected filters.",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=14, color="gray")
    )
    fig.update_layout(title=title, xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig

def _get_title(base_title, author_filter, content_type_filter):
    filters = []
    if author_filter: filters.append("Authors Filtered")
    if content_type_filter: filters.append("Types Filtered")
    return f"{base_title} ({', '.join(filters)})" if filters else base_title

def plot_reaction_bar(author_filter=None, content_type_filter=None):
    title = _get_title("Total Reactions Network-Wide", author_filter, content_type_filter)
    df = get_reaction_totals(author_filter, content_type_filter)
    if df.empty: return _empty_fig(title)
        
    fig = px.bar(df, x="Reaction Type", y="Count", color="Reaction Type", title=title)
    return fig

def plot_trends_line(author_filter=None, content_type_filter=None):
    title = _get_title("Total Views Over Time", author_filter, content_type_filter)
    df = get_trends(author_filter, content_type_filter)
    if df.empty: return _empty_fig(title)
        
    fig = px.line(df, x="Date", y="Total Views", title=title)
    return fig

def plot_top_users_bar(author_filter=None, content_type_filter=None):
    title = _get_title("Top Users by Network Views", author_filter, content_type_filter)
    df = get_top_users(author_filter, content_type_filter)
    if df.empty: return _empty_fig(title)
        
    fig = px.bar(df, x="Author", y="Total Views", title=title, color="Total Shares", color_continuous_scale="Viridis")
    return fig

def plot_engagement_bubble(author_filter=None, content_type_filter=None):
    title = _get_title("Engagement by Content Type (Size = Posts Volume)", author_filter, content_type_filter)
    df = get_engagement_by_content_type(author_filter, content_type_filter)
    if df.empty: return _empty_fig(title)
        
    fig = px.scatter(df, x="Content Type", y="Average Views", size="Total Posts", color="Content Type",
                     title=title, size_max=60)
    return fig

def plot_sentiment_heatmap(author_filter=None, content_type_filter=None):
    title = _get_title("Activity Heatmap (Hour vs Content Type)", author_filter, content_type_filter)
    df = get_heatmap_data(author_filter, content_type_filter)
    if df.empty: return _empty_fig(title)
        
    fig = px.imshow(df, labels=dict(x="Content Type", y="Hour of Day", color="Post Count"),
                    title=title, aspect="auto", color_continuous_scale="YlOrRd")
    return fig

def plot_users_network(author_filter=None, content_type_filter=None):
    title = _get_title("Author-Hashtag Network Topology", author_filter, content_type_filter)
    df_edges = get_author_hashtag_edges(author_filter, content_type_filter)
    if df_edges.empty: return _empty_fig(title)
    
    G = nx.Graph()
    for _, row in df_edges.iterrows():
        G.add_edge(row['Author'], row['Hashtag'])
            
    pos = nx.spring_layout(G, seed=42)
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            color='lightblue',
            size=20,
            line_width=2),
        text=[str(node) for node in G.nodes()],
        textposition="bottom center")

    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title=title,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    return fig
