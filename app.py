import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import matplotlib.pyplot as plt

# ==================================
# PAGE CONFIG
# ==================================

st.set_page_config(
    page_title="Organizational Intelligence Engine",
    page_icon="🧠",
    layout="wide"
)

# ==================================
# LOAD DATA
# ==================================

docs = pd.read_csv("documents.csv")
entities = pd.read_csv("entities.csv")
relationships = pd.read_csv("relationships.csv")

# ==================================
# HEADER
# ==================================

st.title("🧠 Organizational Intelligence Engine")

st.markdown("""
Transform organizational knowledge into actionable intelligence.

### Features
✅ Document Catalog  
✅ Entity Repository  
✅ Relationship Discovery  
✅ Knowledge Graph  
✅ Organizational Insights  
✅ Knowledge Search
""")

st.divider()

# ==================================
# KPI SECTION
# ==================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Documents",
        len(docs)
    )

with col2:
    st.metric(
        "Entities",
        len(entities)
    )

with col3:
    st.metric(
        "Relationships",
        len(relationships)
    )

st.divider()

# ==================================
# DOCUMENT REPOSITORY
# ==================================

st.subheader("📄 Document Repository")

st.dataframe(
    docs,
    use_container_width=True
)

# ==================================
# ENTITY DISTRIBUTION
# ==================================

st.subheader("🏷 Entity Distribution")

entity_count = (
    entities.groupby("type")
    .size()
    .reset_index(name="count")
)

fig_entity = px.bar(
    entity_count,
    x="type",
    y="count",
    color="type",
    title="Entity Type Distribution"
)

st.plotly_chart(
    fig_entity,
    use_container_width=True
)

# ==================================
# RELATIONSHIPS
# ==================================

st.subheader("🔗 Relationship Repository")

st.dataframe(
    relationships,
    use_container_width=True
)

# ==================================
# BUILD KNOWLEDGE GRAPH
# ==================================

G = nx.Graph()

for _, row in relationships.iterrows():

    relationship_name = ""

    if "relationship" in relationships.columns:
        relationship_name = row["relationship"]

    G.add_edge(
        row["source"],
        row["target"],
        relationship=relationship_name
    )

# ==================================
# KNOWLEDGE GRAPH VISUALIZATION
# ==================================

st.subheader("🕸 Interactive Knowledge Graph")

pos = nx.spring_layout(
    G,
    seed=42
)

edge_x = []
edge_y = []

for edge in G.edges():

    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]

    edge_x.extend(
        [x0, x1, None]
    )

    edge_y.extend(
        [y0, y1, None]
    )

edge_trace = go.Scatter(
    x=edge_x,
    y=edge_y,
    mode="lines",
    line=dict(
        width=1,
        color="gray"
    ),
    hoverinfo="none"
)

node_x = []
node_y = []
node_text = []

for node in G.nodes():

    x, y = pos[node]

    node_x.append(x)
    node_y.append(y)
    node_text.append(node)

node_trace = go.Scatter(
    x=node_x,
    y=node_y,
    mode="markers+text",
    text=node_text,
    textposition="top center",
    hovertext=node_text,
    hoverinfo="text",
    marker=dict(
        size=30,
        color="skyblue",
        line=dict(width=2)
    )
)

graph_fig = go.Figure(
    data=[edge_trace, node_trace]
)

graph_fig.update_layout(
    height=600,
    showlegend=False,
    margin=dict(
        l=10,
        r=10,
        t=10,
        b=10
    )
)

st.plotly_chart(
    graph_fig,
    use_container_width=True
)

# ==================================
# KNOWLEDGE SEARCH
# ==================================

st.subheader("🔍 Knowledge Search")

all_entities = sorted(
    list(
        set(
            list(G.nodes())
        )
    )
)

selected_entity = st.selectbox(
    "Select Entity",
    [""] + all_entities
)

search_text = st.text_input(
    "Or search by keyword",
    placeholder="Azure, Business, HR, Finance..."
)

search_term = ""

if selected_entity:
    search_term = selected_entity

if search_text:
    search_term = search_text

if search_term:

    matches = []

    for _, row in relationships.iterrows():

        source = str(row["source"])
        target = str(row["target"])

        rel = ""

        if "relationship" in relationships.columns:
            rel = row["relationship"]

        if (
            search_term.lower() in source.lower()
            or
            search_term.lower() in target.lower()
        ):
            matches.append(
                {
                    "source": source,
                    "target": target,
                    "relationship": rel
                }
            )

    if len(matches) > 0:

        st.success(
            f"Found {len(matches)} matching relationships."
        )

        st.dataframe(
            pd.DataFrame(matches),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            f"No relationships found for '{search_term}'."
        )

# ==================================
# ORGANIZATIONAL INSIGHTS
# ==================================

st.subheader("📊 Organizational Insights")

if G.number_of_nodes() > 0:

    degree_df = pd.DataFrame(
        [
            {
                "Entity": node,
                "Connections": degree
            }
            for node, degree in G.degree()
        ]
    ).sort_values(
        "Connections",
        ascending=False
    )

    most_connected = degree_df.iloc[0]

    st.success(
        f"Most connected entity: "
        f"{most_connected['Entity']} "
        f"({most_connected['Connections']} connections)"
    )

    st.info(
        f"Knowledge network contains "
        f"{G.number_of_nodes()} entities and "
        f"{G.number_of_edges()} relationships."
    )

    st.subheader("🔥 Top Connected Entities")

    top_entities = degree_df.head(10)

    fig_top = px.bar(
        top_entities,
        x="Entity",
        y="Connections",
        color="Connections",
        title="Top Knowledge Hubs"
    )

    st.plotly_chart(
        fig_top,
        use_container_width=True
    )

# ==================================
# DEBUG PANEL
# ==================================

with st.expander("⚙ Debug Information"):

    st.write(
        "Graph Nodes:",
        G.number_of_nodes()
    )

    st.write(
        "Graph Edges:",
        G.number_of_edges()
    )

    st.write(
        "Available Entities:"
    )

    st.write(
        sorted(list(G.nodes()))
    )

    st.write(
        "Relationships Data"
    )

    st.dataframe(
        relationships,
        use_container_width=True
    )