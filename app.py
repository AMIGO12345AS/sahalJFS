from flask import Flask, render_template, request, jsonify
import requests
import json
from datetime import datetime
from zoho_token_manager_serverless import get_headers, get_api_domain

app = Flask(__name__)

# Configuration
# ORGANIZATION_ID is now fetched from environment by token manager
API_DOMAIN = get_api_domain()

@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')

@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    """Fetch invoices from Zoho Books."""
    try:
        headers = get_headers()
        url = f"{API_DOMAIN}/books/v3/invoices"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        # Simplify response for frontend
        invoices = data.get('invoices', [])
        return jsonify({
            'invoices': invoices,
            'count': len(invoices)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/items', methods=['GET'])
def get_items():
    """Fetch items from Zoho Books."""
    try:
        headers = get_headers()
        url = f"{API_DOMAIN}/books/v3/items"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        items = data.get('items', [])
        return jsonify({
            'items': items,
            'count': len(items)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """Fetch customers from Zoho Books."""
    try:
        headers = get_headers()
        url = f"{API_DOMAIN}/books/v3/customers"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        customers = data.get('customers', [])
        return jsonify({
            'customers': customers,
            'count': len(customers)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/invoices', methods=['POST'])
def create_invoice():
    """Create a new invoice in Zoho Books."""
    try:
        invoice_data = request.get_json()
        # Validate required fields
        required = ['customer_id', 'date', 'due_date', 'currency_code', 'line_items']
        for field in required:
            if field not in invoice_data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Prepare payload for Zoho
        payload = {
            'customer_id': invoice_data['customer_id'],
            'date': invoice_data['date'],
            'due_date': invoice_data['due_date'],
            'currency_code': invoice_data['currency_code'],
            'line_items': invoice_data['line_items']
        }
        if 'notes' in invoice_data:
            payload['notes'] = invoice_data['notes']
        
        headers = get_headers()
        url = f"{API_DOMAIN}/books/v3/invoices"
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # Extract relevant info for frontend
        invoice = result.get('invoice', {})
        return jsonify({
            'invoice_id': invoice.get('invoice_id'),
            'invoice_number': invoice.get('invoice_number'),
            'message': 'Invoice created successfully'
        })
    except requests.exceptions.RequestException as e:
        # Try to get error details from response
        if e.response is not None:
            error_detail = e.response.text
        else:
            error_detail = str(e)
        return jsonify({'error': 'Failed to create invoice', 'details': error_detail}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)