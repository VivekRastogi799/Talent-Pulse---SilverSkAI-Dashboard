from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
import json
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# =========================
# Load Data (Enhanced Sample Data)
# =========================
def load_data():
    np.random.seed(42)
    random.seed(42)
    
    n_records = 1000  # Reduced for better performance
    
    # More realistic sample data
    canonical_ids = [f"CUST_{i:04d}" for i in range(1, 201)]  # 200 unique customers
    canonical_names = [f"Company_{i}" for i in range(1, 201)]
    sectors = ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail', 'Education', 'Government', 'Consulting']
    skus = ['TP Starter', 'TP Professional', 'TP Enterprise', 'TP Premium']
    
    # Generate dates across multiple years and quarters
    base_date = datetime(2022, 1, 1)
    
    data = []
    for _ in range(n_records):
        trans_date = base_date + timedelta(days=random.randint(0, 1000))
        data.append({
            'canonical_id': random.choice(canonical_ids),
            'canonical_name': random.choice(canonical_names),
            'sector': random.choice(sectors),
            'sku': random.choice(skus),
            'trans_date': trans_date,
            'activate_on_y': trans_date + timedelta(days=random.randint(0, 30)),
            'end_date': trans_date + timedelta(days=random.randint(365, 730)),
            'daysActive': random.randint(0, 30),
            'clickCount': random.randint(0, 1000),
            'Total Revenue by TP (in Lakhs)': round(random.uniform(1, 200), 2),
            'downloads': random.randint(0, 500),
            'searches': random.randint(0, 800),
            'listing_price': round(random.uniform(50000, 500000), 2),  # in INR
            'retention_cohort': random.choice(['Y+1', 'Y+2', 'Y+3']),
            'region': random.choice(['North', 'South', 'East', 'West', 'Central'])
        })
    
    df = pd.DataFrame(data)
    
    # Process dates and create derived fields
    for col in ['trans_date', 'activate_on_y', 'end_date']:
        df[col] = pd.to_datetime(df[col])
    
    # Create FY, Quarter, Month
    df['FY'] = df['trans_date'].dt.year
    df['quarter'] = df['trans_date'].dt.quarter
    df['month'] = df['trans_date'].dt.month
    df['QTR'] = df['quarter']
    
    # Convert revenue to actual INR values
    df['revenue_inr'] = df['Total Revenue by TP (in Lakhs)'] * 100000
    
    return df

# =========================
# Helper Functions
# =========================
def inr_format(x):
    """Format numbers as INR with Lakhs/Crores."""
    if pd.isna(x) or x == 0:
        return "₹0"
    if abs(x) >= 10000000:  # 1 Crore
        return f"₹{x/10000000:.2f} Cr"
    elif abs(x) >= 100000:  # 1 Lakh
        return f"₹{x/100000:.2f} L"
    else:
        return f"₹{x:,.0f}"

def percentage_change(current, previous):
    """Calculate percentage change with proper handling of zero values."""
    if previous == 0:
        return 100 if current > 0 else 0
    return ((current - previous) / previous) * 100

def create_trend_chart(df, x_col, y_col, title, color_col=None):
    """Create a trend chart using Plotly."""
    try:
        fig = px.line(df, x=x_col, y=y_col, title=title, 
                      color=color_col if color_col else None)
        fig.update_layout(height=400)
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        return None

def create_pie_chart(df, values, names, title):
    """Create a pie chart using Plotly."""
    try:
        fig = px.pie(df, values=values, names=names, title=title)
        fig.update_layout(height=400)
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        return None

# =========================
# Load and Process Data
# =========================
try:
    df = load_data()
except Exception as e:
    print(f"Error loading data: {e}")
    df = pd.DataFrame()

@app.route('/')
def dashboard():
    try:
        # Calculate current metrics
        current_date = pd.Timestamp.now()
        current_quarter = current_date.quarter
        current_year = current_date.year
        current_month = current_date.strftime('%Y-%m')
        
        # Filter data for current period
        current_data = df[df['FY'] == current_year]
        last_year_data = df[df['FY'] == (current_year - 1)]
        
        # Calculate KPIs
        current_revenue = current_data['revenue_inr'].sum()
        last_year_revenue = last_year_data['revenue_inr'].sum()
        revenue_growth = percentage_change(current_revenue, last_year_revenue)
        
        current_customers = current_data['canonical_id'].nunique()
        last_year_customers = last_year_data['canonical_id'].nunique()
        customer_growth = percentage_change(current_customers, last_year_customers)
        
        # Create charts
        monthly_revenue = current_data.groupby([current_data['trans_date'].dt.to_period('M')])['revenue_inr'].sum().reset_index()
        monthly_revenue['period'] = monthly_revenue['trans_date'].astype(str)
        revenue_chart = create_trend_chart(monthly_revenue, 'period', 'revenue_inr', 'Monthly Revenue Trend')
        
        sku_revenue = current_data.groupby('sku')['revenue_inr'].sum().reset_index()
        sku_chart = create_pie_chart(sku_revenue, 'revenue_inr', 'sku', 'Revenue by SKU')
        
        industry_customers = current_data.groupby('sector')['canonical_id'].nunique().reset_index()
        industry_chart = create_trend_chart(industry_customers, 'sector', 'canonical_id', 'Customers by Industry')
        
        # Top customers
        top_customers = (current_data.groupby(['canonical_name', 'sector'])
                        .agg({
                            'revenue_inr': 'sum',
                            'daysActive': 'mean',
                            'sku': 'first',
                            'region': 'first'
                        }).reset_index()
                        .sort_values('revenue_inr', ascending=False)
                        .head(10))
        
        top_customers['Revenue (INR)'] = top_customers['revenue_inr'].apply(inr_format)
        
        return render_template('dashboard.html',
                             current_revenue=inr_format(current_revenue),
                             revenue_growth=f"{revenue_growth:+.1f}%",
                             current_customers=current_customers,
                             customer_growth=f"{customer_growth:+.1f}%",
                             revenue_chart=revenue_chart,
                             sku_chart=sku_chart,
                             industry_chart=industry_chart,
                             top_customers=top_customers.to_dict('records'))
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/api/data')
def get_data():
    """API endpoint to get filtered data"""
    try:
        period = request.args.get('period', 'current_year')
        sku = request.args.get('sku', 'all')
        industry = request.args.get('industry', 'all')
        
        # Apply filters
        filtered_df = df.copy()
        
        if period == 'current_year':
            filtered_df = filtered_df[filtered_df['FY'] == datetime.now().year]
        elif period == 'last_year':
            filtered_df = filtered_df[filtered_df['FY'] == datetime.now().year - 1]
        
        if sku != 'all':
            filtered_df = filtered_df[filtered_df['sku'] == sku]
        
        if industry != 'all':
            filtered_df = filtered_df[filtered_df['sector'] == industry]
        
        # Calculate metrics
        metrics = {
            'total_revenue': filtered_df['revenue_inr'].sum(),
            'total_customers': filtered_df['canonical_id'].nunique(),
            'avg_revenue_per_customer': filtered_df['revenue_inr'].sum() / filtered_df['canonical_id'].nunique() if filtered_df['canonical_id'].nunique() > 0 else 0,
            'total_downloads': filtered_df['downloads'].sum(),
            'total_searches': filtered_df['searches'].sum(),
            'active_users': len(filtered_df[filtered_df['daysActive'] > 0])
        }
        
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts')
def get_charts():
    """API endpoint to get chart data"""
    try:
        chart_type = request.args.get('type', 'revenue_trend')
        
        if chart_type == 'revenue_trend':
            monthly_data = df.groupby([df['trans_date'].dt.to_period('M')])['revenue_inr'].sum().reset_index()
            monthly_data['period'] = monthly_data['trans_date'].astype(str)
            chart_data = create_trend_chart(monthly_data, 'period', 'revenue_inr', 'Revenue Trend')
        
        elif chart_type == 'sku_distribution':
            sku_data = df.groupby('sku')['revenue_inr'].sum().reset_index()
            chart_data = create_pie_chart(sku_data, 'revenue_inr', 'sku', 'Revenue by SKU')
        
        elif chart_type == 'industry_customers':
            industry_data = df.groupby('sector')['canonical_id'].nunique().reset_index()
            chart_data = create_trend_chart(industry_data, 'sector', 'canonical_id', 'Customers by Industry')
        
        else:
            chart_data = None
        
        return jsonify({'chart_data': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Vercel"""
    return jsonify({'status': 'healthy', 'message': 'Talent Pulse Dashboard is running'})

if __name__ == '__main__':
    app.run(debug=True) 