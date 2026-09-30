"""
Shared theme constants for the dashboard.
"""

# Semantic risk colors — used across pages for consistency.
RISK_COLORS = {
    "LOW": "#2ECC71",  # green
    "MEDIUM": "#F1C40F",  # yellow
    "HIGH": "#E67E22",  # orange
    "CRITICAL": "#E74C3C",  # red
}

# Continuous color scale for risk scores (low → high).
RISK_CONTINUOUS_SCALE = "RdYlGn_r"

# Navigation registry — kept in one place so sidebar and landing
# cards stay in sync.
PAGES = [
    ("app.py", "Home", "🏠"),
    ("pages/Overview.py", "Executive Overview", "📊"),
    ("pages/Routes.py", "Route Analytics", "🚛"),
    ("pages/Risk.py", "Delivery Risk", "⚠️"),
    ("pages/Warehouses.py", "Warehouse Analytics", "🏭"),
    ("pages/Customers.py", "Customer Analytics", "👥"),
]
