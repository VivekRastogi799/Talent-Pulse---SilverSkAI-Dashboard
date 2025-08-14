from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# =========================
# Load Data (Simplified Sample Data)
# =========================
def load_data():
    random.seed(42)
    
    # Simplified sample data without pandas
    data = []
    sectors = ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail', 'Education', 'Government', 'Consulting']
    skus = ['TP Starter', 'TP Professional', 'TP Enterprise', 'TP Premium']
    
    # Generate sample data
    for i in range(100):  # Reduced for performance
        revenue = round(random.uniform(100000, 5000000), 2)
        data.append({
            'canonical_id': f"CUST_{i:04d}",
            'canonical_name': f"Company_{i}",
            'sector': random.choice(sectors),
            'sku': random.choice(skus),
            'revenue_inr': revenue,
            'daysActive': random.randint(0, 30),
            'downloads': random.randint(0, 500),
            'searches': random.randint(0, 800),
            'region': random.choice(['North', 'South', 'East', 'West', 'Central'])
        })
    
    return data

# =========================
# Helper Functions
# =========================
def inr_format(x):
    """Format numbers as INR with Lakhs/Crores."""
    if not x or x == 0:
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

# =========================
# Load and Process Data
# =========================
try:
    raw_data = load_data()
except Exception as e:
    print(f"Error loading data: {e}")
    raw_data = []

@app.route('/')
def dashboard():
    try:
        # Calculate current metrics
        current_year = datetime.now().year
        
        # Filter data for current period (simplified)
        current_data = [item for item in raw_data if item['revenue_inr'] > 0]
        
        # Calculate KPIs
        current_revenue = sum(item['revenue_inr'] for item in current_data)
        current_customers = len(set(item['canonical_id'] for item in current_data))
        
        # Mock last year data for comparison
        last_year_revenue = current_revenue * 0.85  # 15% less than current
        revenue_growth = percentage_change(current_revenue, last_year_revenue)
        
        last_year_customers = int(current_customers * 0.9)  # 10% less than current
        customer_growth = percentage_change(current_customers, last_year_customers)
        
        # Create simplified chart data
        revenue_by_sku = {}
        for item in current_data:
            sku = item['sku']
            if sku not in revenue_by_sku:
                revenue_by_sku[sku] = 0
            revenue_by_sku[sku] += item['revenue_inr']
        
        # Top customers
        top_customers = sorted(current_data, key=lambda x: x['revenue_inr'], reverse=True)[:10]
        for customer in top_customers:
            customer['Revenue (INR)'] = inr_format(customer['revenue_inr'])
        
        return render_template('dashboard.html',
                             current_revenue=inr_format(current_revenue),
                             revenue_growth=f"{revenue_growth:+.1f}%",
                             current_customers=current_customers,
                             customer_growth=f"{customer_growth:+.1f}%",
                             revenue_chart=json.dumps({
                                 'data': [{'x': list(revenue_by_sku.keys()), 'y': list(revenue_by_sku.values()), 'type': 'bar'}],
                                 'layout': {'title': 'Revenue by SKU', 'height': 400}
                             }),
                             sku_chart=json.dumps({
                                 'data': [{'values': list(revenue_by_sku.values()), 'labels': list(revenue_by_sku.keys()), 'type': 'pie'}],
                                 'layout': {'title': 'Revenue by SKU', 'height': 400}
                             }),
                             industry_chart=json.dumps({
                                 'data': [{'x': ['Technology', 'Healthcare', 'Finance'], 'y': [30, 25, 20], 'type': 'bar'}],
                                 'layout': {'title': 'Customers by Industry', 'height': 400}
                             }),
                             top_customers=top_customers)
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
        filtered_data = raw_data.copy()
        
        if sku != 'all':
            filtered_data = [item for item in filtered_data if item['sku'] == sku]
        
        if industry != 'all':
            filtered_data = [item for item in filtered_data if item['sector'] == industry]
        
        # Calculate metrics
        metrics = {
            'total_revenue': sum(item['revenue_inr'] for item in filtered_data),
            'total_customers': len(set(item['canonical_id'] for item in filtered_data)),
            'avg_revenue_per_customer': sum(item['revenue_inr'] for item in filtered_data) / len(set(item['canonical_id'] for item in filtered_data)) if filtered_data else 0,
            'total_downloads': sum(item['downloads'] for item in filtered_data),
            'total_searches': sum(item['searches'] for item in filtered_data),
            'active_users': len([item for item in filtered_data if item['daysActive'] > 0])
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
            # Simplified monthly data
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            revenue_data = [random.randint(1000000, 5000000) for _ in months]
            chart_data = {
                'data': [{'x': months, 'y': revenue_data, 'type': 'line'}],
                'layout': {'title': 'Revenue Trend', 'height': 400}
            }
        
        elif chart_type == 'sku_distribution':
            revenue_by_sku = {}
            for item in raw_data:
                sku = item['sku']
                if sku not in revenue_by_sku:
                    revenue_by_sku[sku] = 0
                revenue_by_sku[sku] += item['revenue_inr']
            
            chart_data = {
                'data': [{'values': list(revenue_by_sku.values()), 'labels': list(revenue_by_sku.keys()), 'type': 'pie'}],
                'layout': {'title': 'Revenue by SKU', 'height': 400}
            }
        
        else:
            chart_data = None
        
        return jsonify({'chart_data': json.dumps(chart_data)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Vercel"""
    return jsonify({
        'status': 'healthy', 
        'message': 'Talent Pulse Dashboard is running',
        'data_count': len(raw_data),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True) 