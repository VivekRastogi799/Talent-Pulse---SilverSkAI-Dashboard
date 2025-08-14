# Talent Pulse Executive Dashboard

A modern, interactive business intelligence dashboard built with Flask and Plotly, designed to run on Vercel's serverless platform.

## 🚀 Features

- **Real-time Analytics**: Live data visualization with interactive charts
- **Multi-dimensional Analysis**: Revenue, customer, and usage analytics
- **Responsive Design**: Modern UI that works on all devices
- **Interactive Filters**: Filter by time period, SKU, and industry
- **API Endpoints**: RESTful API for data access
- **Beautiful Visualizations**: Plotly charts with custom styling

## 📊 Dashboard Sections

### 1. Revenue Snapshot
- Monthly revenue trends
- Revenue by SKU distribution
- Financial performance KPIs
- Revenue insights and projections

### 2. Customer Analysis
- Customer growth trends
- Industry-wise customer distribution
- Top customers by revenue
- Customer retention metrics

### 3. Usage Activity
- User engagement metrics
- Download vs search analysis
- Usage classification
- Dormant user identification

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Plotly.js
- **Styling**: Bootstrap 5
- **Icons**: Font Awesome
- **Deployment**: Vercel

## 📦 Dependencies

- `flask==3.0.0`
- `pandas==2.1.3`
- `numpy==1.24.3`
- `plotly==5.17.0`
- `gunicorn==21.2.0`

## 🚀 Deployment on Vercel

### Prerequisites
1. Vercel account
2. Git repository
3. Python 3.8+

### Step-by-Step Deployment

1. **Clone or Upload to Vercel**
   ```bash
   # If using Vercel CLI
   vercel
   
   # Or connect your GitHub repository to Vercel
   ```

2. **Vercel Configuration**
   The `vercel.json` file is already configured with:
   - Python runtime
   - Proper routing
   - Function timeout settings

3. **Environment Variables** (if needed)
   ```bash
   # Add any environment variables in Vercel dashboard
   # Currently using sample data, no external dependencies
   ```

4. **Deploy**
   ```bash
   # Deploy to Vercel
   vercel --prod
   ```

### File Structure
```
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── vercel.json        # Vercel configuration
├── templates/
│   └── dashboard.html # HTML template
└── README.md          # This file
```

## 🔧 Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Locally**
   ```bash
   python app.py
   ```

3. **Access Dashboard**
   Open `http://localhost:5000` in your browser

## 📈 API Endpoints

### GET `/`
Main dashboard page with interactive charts and KPIs

### GET `/api/data`
Returns filtered data based on query parameters:
- `period`: Time period filter (current_year, last_year, all_time)
- `sku`: SKU filter
- `industry`: Industry filter

### GET `/api/charts`
Returns chart data:
- `type`: Chart type (revenue_trend, sku_distribution, industry_customers)

## 🎨 Customization

### Styling
- Modify CSS in `templates/dashboard.html`
- Update color schemes and gradients
- Customize chart themes

### Data Source
- Replace sample data generation in `load_data()` function
- Connect to your database or API
- Update data processing logic

### Charts
- Add new chart types in `create_trend_chart()` and `create_pie_chart()`
- Customize Plotly chart configurations
- Add new API endpoints for additional visualizations

## 🔍 Troubleshooting

### Common Issues

1. **Charts Not Loading**
   - Check browser console for JavaScript errors
   - Verify Plotly.js is loaded
   - Check API endpoint responses

2. **Deployment Errors**
   - Ensure all dependencies are in `requirements.txt`
   - Check `vercel.json` configuration
   - Verify Python version compatibility

3. **Performance Issues**
   - Optimize data processing in `load_data()`
   - Implement caching for expensive operations
   - Consider pagination for large datasets

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review Vercel deployment logs
- Open an issue in the repository

---

**Note**: This dashboard currently uses sample data. For production use, replace the data generation logic with your actual data source. 