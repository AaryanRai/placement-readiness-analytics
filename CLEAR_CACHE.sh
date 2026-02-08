#!/bin/bash
# Clear Streamlit cache and Python cache

echo "Clearing Streamlit and Python caches..."

# Clear Streamlit cache
rm -rf ~/.streamlit/cache 2>/dev/null
echo "✓ Streamlit cache cleared"

# Clear Python bytecode cache in project
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
echo "✓ Python bytecode cache cleared"

echo ""
echo "Cache cleared! Please restart Streamlit:"
echo "  streamlit run src/dashboard/app.py"

