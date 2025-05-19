import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
import plotly.express as px
import pandas as pd
import numpy as np

# ------------------- Dataset Generation (Simulated for demo) -------------------

# Sales data simulation (12 months)
df_sales = pd.DataFrame({
    "Month": pd.date_range(start="2024-01-01", periods=12, freq="M").strftime('%b'),
    "Revenue_2024": np.random.randint(40000, 70000, 12),
    "Revenue_2023": np.random.randint(30000, 60000, 12),
    "Profit": np.random.randint(10000, 30000, 12),
    "Quantity": np.random.randint(300, 600, 12),
    "Channel": np.random.choice(["Online", "Cash"], 12),
    "ProductLine": np.random.choice([
        'Virtual Assistant', 'Prototype Builder', 'Employee Experience Platform',
        'Demo Scheduler', 'AI Assist Insights', 'Analytics Dashboard'
    ], 12),
    "Salesperson": np.random.choice(["Alice", "Bob", "Charlie", "Diana"], 12)
})
df_sales["Profit %"] = round((df_sales["Profit"] / df_sales["Revenue_2024"]) * 100, 2)
df_sales["Target Revenue"] = 60000

# Web logs data simulation (1000 records)
n_records = 1000
countries = ['USA', 'UK', 'Germany', 'India', 'Canada', 'Australia', 'Botswana']
event_types = ['JobRequest', 'DemoRequest', 'AIAssistantRequest', 'SalesInquiry']
web_product_categories = [
    'Virtual Assistant', 'Prototype Builder', 'Employee Experience Platform',
    'Demo Scheduler', 'AI Assist Insights', 'Analytics Dashboard'
]

np.random.seed(0)
df_logs = pd.DataFrame({
    "Country": np.random.choice(countries, n_records),
    "EventType": np.random.choice(event_types, n_records),
    "WebTool": np.random.choice(web_product_categories, n_records),
    "Amount": np.random.choice([0, 0, 0] + list(np.round(np.random.uniform(100, 1000, 100), 2)), n_records)
})
df_logs["Amount"] = pd.to_numeric(df_logs["Amount"])

# ------------------- Simple Access Control Credentials -------------------

USER_ROLES = {
    "lead_user": {"password": "leadpass", "role": "lead"},
    "team_user": {"password": "teampass", "role": "member"},
    "marketing_user": {"password": "marketpass", "role": "marketing"},
    "log_user": {"password": "logpass", "role": "logs"}
}

# ------------------- Dash App Setup -------------------

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

def generate_kpi_card(title, value, icon):
    formatted = f"{value:,}" if isinstance(value, (int, float)) else value
    return dbc.Card([
        dbc.CardBody([
            html.H6(title, className="card-title"),
            html.H4(formatted, className="card-text"),
            html.I(className=f"bi bi-{icon}")
        ])
    ], className="m-2 shadow-sm")

# --- Sales Lead Dashboard View ---
def sales_lead_view():
    trend_fig = px.line(df_sales, x="Month", y=["Revenue_2023", "Revenue_2024"],
                        labels={"value": "Revenue", "variable": "Year"},
                        title="Revenue Comparison: 2023 vs 2024")

    profit_fig = px.bar(df_sales, x="Month", y="Profit", title="Monthly Profit with Target Line")
    profit_fig.add_scatter(x=df_sales["Month"], y=[20000]*12, mode="lines", name="Target Profit")

    df_sales["Difference"] = df_sales["Revenue_2024"] - df_sales["Revenue_2023"]
    diff_fig = px.bar(df_sales, x="Month", y="Difference", title="Revenue Difference", color="Difference")

    rev_target_fig = px.line(df_sales, x="Month", y="Revenue_2024", title="Revenue vs Target")
    rev_target_fig.add_scatter(x=df_sales["Month"], y=df_sales["Target Revenue"], mode="lines", name="Target Revenue")

    avg_profit_pct = f"{df_sales['Profit %'].mean():.2f}%"

    return html.Div([
        html.H3("Sales Lead Dashboard", className="text-center mb-4"),
        dbc.Row([
            dbc.Col(generate_kpi_card("Total Revenue (2024)", df_sales["Revenue_2024"].sum(), "bar-chart"), width=3),
            dbc.Col(generate_kpi_card("Total Profit", df_sales["Profit"].sum(), "cash-coin"), width=3),
            dbc.Col(generate_kpi_card("Total Quantity", df_sales["Quantity"].sum(), "basket"), width=3),
            dbc.Col(generate_kpi_card("Average Profit %", avg_profit_pct, "graph-up"), width=3),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=trend_fig), width=6),
            dbc.Col(dcc.Graph(figure=profit_fig), width=6),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=diff_fig), width=6),
            dbc.Col(dcc.Graph(figure=rev_target_fig), width=6),
        ]),
    ])

# --- Sales Team Member View ---
def sales_team_member_view():
    team_perf = df_sales.groupby("Salesperson")["Revenue_2024"].sum().reset_index()
    team_fig = px.bar(team_perf, x="Salesperson", y="Revenue_2024", title="Team Revenue Performance")

    sales_trend_fig = px.line(df_sales, x="Month", y="Revenue_2024", color="Salesperson",
                              title="Salesperson Revenue Trends")
    sales_trend_fig.add_scatter(x=df_sales["Month"].unique(), y=[60000]*len(df_sales["Month"].unique()),
                                mode="lines", name="Target Revenue", line=dict(dash='dash'))

    return html.Div([
        html.H3("Sales Team Member Dashboard", className="text-center mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=team_fig), width=6),
            dbc.Col(dcc.Graph(figure=sales_trend_fig), width=6),
        ]),
    ])

# --- Marketing Analyst View ---
def marketing_view():
    channel_fig = px.pie(df_sales, names="Channel", values="Revenue_2024", title="Revenue by Payment Channel")
    product_line_fig = px.bar(df_sales, x="ProductLine", y="Revenue_2024", title="Revenue by Product Line")

    return html.Div([
        html.H3("Marketing Analytics Dashboard", className="text-center mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=channel_fig), width=6),
            dbc.Col(dcc.Graph(figure=product_line_fig), width=6),
        ]),
    ])

# --- Web Log Analyst View ---
def web_log_view():
    # Validate df_logs columns
    required_columns = {"Country", "EventType", "Amount", "WebTool"}
    if not required_columns.issubset(df_logs.columns):
        return html.Div("Invalid or incomplete web logs dataset.")

    total_logs = len(df_logs)
    job_requests = (df_logs["EventType"] == "JobRequest").sum()
    demo_requests = (df_logs["EventType"] == "DemoRequest").sum()
    assistant_requests = (df_logs["EventType"] == "AIAssistantRequest").sum()
    total_sales = df_logs["Amount"].sum()

    kpis = dbc.Row([
        dbc.Col(generate_kpi_card("Total Logs", total_logs, "file-earmark-bar-graph"), width=2),
        dbc.Col(generate_kpi_card("Job Requests", job_requests, "briefcase"), width=2),
        dbc.Col(generate_kpi_card("Demo Requests", demo_requests, "calendar-event"), width=2),
        dbc.Col(generate_kpi_card("AI Assistant Requests", assistant_requests, "robot"), width=3),
        dbc.Col(generate_kpi_card("Total Sales ($)", total_sales, "currency-dollar"), width=3),
    ])

    by_country_fig = px.pie(df_logs, names="Country", title="Requests by Country")

    event_counts = df_logs["EventType"].value_counts().reset_index()
    event_counts.columns = ["EventType", "Count"]
    by_event_fig = px.bar(event_counts, x="EventType", y="Count", title="Requests by Event Type")

    sales_by_webtool = df_logs[df_logs["Amount"] > 0].groupby("WebTool")["Amount"].sum().reset_index()
    sales_fig = px.bar(sales_by_webtool, x="WebTool", y="Amount", title="Sales by Web Tool")

    return html.Div([
        html.H3("Web Log Analysis Dashboard", className="text-center mb-4"),
        kpis,
        dbc.Row([
            dbc.Col(dcc.Graph(figure=by_country_fig), width=6),
            dbc.Col(dcc.Graph(figure=by_event_fig), width=6),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=sales_fig), width=12),
        ]),
    ])

# ------------------- App Layout -------------------

app.layout = dbc.Container([
    dbc.Row([
        # Sidebar for Login (fixed width)
        dbc.Col([
            html.H3("Login", className="text-center my-3"),
            dbc.Input(id="username", placeholder="Enter username", type="text", className="mb-2"),
            dbc.Input(id="password", placeholder="Enter password", type="password", className="mb-2"),
            dbc.Button("Login", id="login-btn", color="primary", className="mb-3", style={"width": "100%"}),
            html.Div(id="login-message", className="text-danger"),
        ], width=3, style={
            "position": "fixed",
            "height": "100vh",
            "backgroundColor": "#f8f9fa",
            "padding": "20px",
            "boxShadow": "2px 0 5px rgba(0,0,0,0.1)",
            "overflowY": "auto",
        }),

        # Main content area (dashboard views)
        dbc.Col([
            html.H1("AI-Solutions Web KPI Dashboard", className="text-center my-3"),
            html.Hr(),
            html.Div(id="user-view")
        ], width={"size": 9, "offset": 3})  # offset to avoid sidebar overlay
    ])
], fluid=True)


# ------------------- Access Control Callback -------------------

@app.callback(
    Output("user-view", "children"),
    Output("login-message", "children"),
    Input("login-btn", "n_clicks"),
    State("username", "value"),
    State("password", "value")
)
def handle_login(n_clicks, username, password):
    if not n_clicks:
        # No login attempt yet
        return dash.no_update, ""
    if not username or not password:
        return dash.no_update, "❌ Please enter both username and password."

    user = USER_ROLES.get(username)
    if user and user["password"] == password:
        role = user["role"]
        if role == "lead":
            return sales_lead_view(), ""
        elif role == "member":
            return sales_team_member_view(), ""
        elif role == "marketing":
            return marketing_view(), ""
        elif role == "logs":
            return web_log_view(), ""
        else:
            return html.Div("Unknown role."), ""
    return html.Div(), "❌ Invalid credentials"

# ------------------- Run Server -------------------

if __name__ == "__main__":
    app.run(debug=True)