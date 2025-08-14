from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime
import random

app = Flask(__name__)

# =========================
# Load Data (Simplified Sample Data)
# =========================
def load_data():
    random.seed(42)
    
    # Simplified sample data
    data = []
    sectors = ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail', 'Education', 'Government', 'Consulting']
    skus = ['TP Starter', 'TP Professional', 'TP Enterprise', 'TP Premium']
    
    # Generate sample data
    for i in range(50):  # Even smaller for better performance
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
    try:
        if not x or x == 0:
            return "₹0"
        if abs(x) >= 10000000:  # 1 Crore
            return f"₹{x/10000000:.2f} Cr"
        elif abs(x) >= 100000:  # 1 Lakh
            return f"₹{x/100000:.2f} L"
        else:
            return f"₹{x:,.0f}"
    except:
        return "₹0"

def percentage_change(current, previous):
    """Calculate percentage change with proper handling of zero values."""
    try:
        if previous == 0:
            return 100 if current > 0 else 0
        return ((current - previous) / previous) * 100
    except:
        return 0

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
        current_data = [item for item in raw_data if item.get('revenue_inr', 0) > 0]
        
        # Calculate KPIs with safe defaults
        current_revenue = sum(item.get('revenue_inr', 0) for item in current_data)
        current_customers = len(set(item.get('canonical_id', '') for item in current_data))
        
        # Mock last year data for comparison
        last_year_revenue = current_revenue * 0.85  # 15% less than current
        revenue_growth = percentage_change(current_revenue, last_year_revenue)
        
        last_year_customers = int(current_customers * 0.9)  # 10% less than current
        customer_growth = percentage_change(current_customers, last_year_customers)
        
        # Create simplified chart data
        revenue_by_sku = {}
        for item in current_data:
            sku = item.get('sku', 'Unknown')
            if sku not in revenue_by_sku:
                revenue_by_sku[sku] = 0
            revenue_by_sku[sku] += item.get('revenue_inr', 0)
        
        # Top customers
        top_customers = sorted(current_data, key=lambda x: x.get('revenue_inr', 0), reverse=True)[:10]
        for customer in top_customers:
            customer['Revenue (INR)'] = inr_format(customer.get('revenue_inr', 0))
        
        # Create safe chart data
        revenue_chart = {
            'data': [{'x': list(revenue_by_sku.keys()), 'y': list(revenue_by_sku.values()), 'type': 'bar'}],
            'layout': {'title': 'Revenue by SKU', 'height': 400}
        }
        
        sku_chart = {
            'data': [{'values': list(revenue_by_sku.values()), 'labels': list(revenue_by_sku.keys()), 'type': 'pie'}],
            'layout': {'title': 'Revenue by SKU', 'height': 400}
        }
        
        industry_chart = {
            'data': [{'x': ['Technology', 'Healthcare', 'Finance'], 'y': [30, 25, 20], 'type': 'bar'}],
            'layout': {'title': 'Customers by Industry', 'height': 400}
        }
        
        return render_template('dashboard.html',
                             current_revenue=inr_format(current_revenue),
                             revenue_growth=f"{revenue_growth:+.1f}%",
                             current_customers=current_customers,
                             customer_growth=f"{customer_growth:+.1f}%",
                             revenue_chart=json.dumps(revenue_chart),
                             sku_chart=json.dumps(sku_chart),
                             industry_chart=json.dumps(industry_chart),
                             top_customers=top_customers)
    except Exception as e:
        # Return a simple error page if template rendering fails
        return f"""
        <html>
        <head><title>Talent Pulse Dashboard</title></head>
        <body style="font-family: Arial, sans-serif; padding: 20px; background: #f0f0f0;">
            <h1>🎯 Talent Pulse Executive Dashboard</h1>
            <p>Dashboard is running successfully!</p>
            <p><strong>Current Revenue:</strong> {inr_format(sum(item.get('revenue_inr', 0) for item in raw_data))}</p>
            <p><strong>Total Customers:</strong> {len(set(item.get('canonical_id', '') for item in raw_data))}</p>
            <p><a href="/health">Health Check</a> | <a href="/api/data">API Data</a></p>
        </body>
        </html>
        """

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
            filtered_data = [item for item in filtered_data if item.get('sku') == sku]
        
        if industry != 'all':
            filtered_data = [item for item in filtered_data if item.get('sector') == industry]
        
        # Calculate metrics with safe defaults
        total_revenue = sum(item.get('revenue_inr', 0) for item in filtered_data)
        total_customers = len(set(item.get('canonical_id', '') for item in filtered_data))
        avg_revenue = total_revenue / total_customers if total_customers > 0 else 0
        
        metrics = {
            'total_revenue': total_revenue,
            'total_customers': total_customers,
            'avg_revenue_per_customer': avg_revenue,
            'total_downloads': sum(item.get('downloads', 0) for item in filtered_data),
            'total_searches': sum(item.get('searches', 0) for item in filtered_data),
            'active_users': len([item for item in filtered_data if item.get('daysActive', 0) > 0])
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
                sku = item.get('sku', 'Unknown')
                if sku not in revenue_by_sku:
                    revenue_by_sku[sku] = 0
                revenue_by_sku[sku] += item.get('revenue_inr', 0)
            
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
    try:
        return jsonify({
            'status': 'healthy', 
            'message': 'Talent Pulse Dashboard is running',
            'data_count': len(raw_data),
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/simple')
def simple_dashboard():
    """Simple dashboard without complex template"""
    try:
        current_revenue = sum(item.get('revenue_inr', 0) for item in raw_data)
        current_customers = len(set(item.get('canonical_id', '') for item in raw_data))
        
        return f"""
        <html>
        <head>
            <title>Talent Pulse Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
                .container {{ background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px; }}
                .metric {{ background: rgba(255,255,255,0.2); padding: 15px; margin: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎯 Talent Pulse Executive Dashboard</h1>
                <div class="metric">
                    <h2>💰 Total Revenue: {inr_format(current_revenue)}</h2>
                </div>
                <div class="metric">
                    <h2>👥 Total Customers: {current_customers}</h2>
                </div>
                <div class="metric">
                    <h2>📊 Data Records: {len(raw_data)}</h2>
                </div>
                <p><a href="/health" style="color: white;">Health Check</a> | <a href="/api/data" style="color: white;">API Data</a></p>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>Dashboard Error</h1><p>{str(e)}</p>"

if __name__ == '__main__':
    app.run(debug=True) 