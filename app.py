#!/usr/bin/env python3
"""
Feature.fm API Test Dashboard
A Flask application for testing and monitoring Feature.fm API endpoints
"""

import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Feature.fm API Configuration from environment variables
API_KEY = os.getenv('FEATUREFM_API_KEY', '3890d422-882b-486d-9de6-c106d9951094')
ISS = os.getenv('FEATUREFM_ISS', 'sandbox-precise.digital')
SECRET_KEY = os.getenv('FEATUREFM_SECRET_KEY', 'mf1x4y13dgnqmcm3v9x7t9fucg7nozil')
BASE_URL = os.getenv('FEATUREFM_BASE_URL', 'https://api.feature.fm')

# Test results storage
test_results = []
test_history = []

@app.route('/')
def index():
    """Serve the dashboard HTML"""
    return render_template('dashboard.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current API configuration (masked)"""
    return jsonify({
        'api_key': API_KEY[:8] + '...' if API_KEY else None,
        'iss': ISS,
        'base_url': BASE_URL,
        'configured': bool(API_KEY and ISS and SECRET_KEY)
    })

@app.route('/api/proxy/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_api(endpoint):
    """
    Proxy API requests to Feature.fm to bypass CORS
    Handles all HTTP methods and forwards headers appropriately
    """
    
    # Build headers for Feature.fm API
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
        'X-ISS': ISS,
        'X-Secret-Key': SECRET_KEY
    }
    
    # Get any additional headers from the request
    access_id = request.headers.get('X-Access-Id')
    auth_token = request.headers.get('Authorization')
    
    if access_id:
        headers['X-Access-Id'] = access_id
    if auth_token:
        headers['Authorization'] = auth_token
    
    # Debug logging
    app.logger.debug(f"Proxying {request.method} request to: {endpoint}")
    app.logger.debug(f"Headers: {headers}")
    
    # Construct full URL
    url = f"{BASE_URL}/{endpoint}"
    
    # Add query parameters if present
    if request.args:
        from urllib.parse import urlencode
        url += '?' + urlencode(request.args)
    
    try:
        # Make the request based on method
        if request.method == 'GET':
            response = requests.get(url, headers=headers, timeout=30)
        elif request.method == 'POST':
            response = requests.post(url, headers=headers, json=request.json, timeout=30)
        elif request.method == 'PUT':
            response = requests.put(url, headers=headers, json=request.json, timeout=30)
        elif request.method == 'PATCH':
            response = requests.patch(url, headers=headers, json=request.json, timeout=30)
        elif request.method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=30)
        
        # Log response
        app.logger.debug(f"Response Status: {response.status_code}")
        
        # Return response
        try:
            return response.json(), response.status_code
        except json.JSONDecodeError:
            return response.text, response.status_code
            
    except requests.exceptions.Timeout:
        return {'error': 'Request timeout'}, 504
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Proxy error: {str(e)}")
        return {'error': str(e)}, 500

@app.route('/api/run-tests', methods=['POST'])
def run_tests():
    """Run all Feature.fm API tests"""
    global test_results, test_history
    test_results = []
    
    # Get test configuration from request
    test_config = request.json or {}
    selected_tests = test_config.get('tests', 'all')
    
    # Define comprehensive test cases
    all_test_cases = [
        {
            'id': 'auth',
            'name': 'Authentication Test',
            'description': 'Verify API authentication with credentials',
            'endpoint': 'auth/verify',
            'method': 'GET',
            'category': 'Authentication',
            'data': None
        },
        {
            'id': 'links_list',
            'name': 'List Smart Links',
            'description': 'Retrieve all smart links',
            'endpoint': 'links',
            'method': 'GET',
            'category': 'Links',
            'data': None
        },
        {
            'id': 'links_create',
            'name': 'Create Smart Link',
            'description': 'Create a new smart link',
            'endpoint': 'links',
            'method': 'POST',
            'category': 'Links',
            'data': {
                'url': 'https://open.spotify.com/track/4PTG3Z6ehGkBFwjybzWkR8',
                'title': f'Test Link {datetime.now().strftime("%Y%m%d%H%M%S")}',
                'artist': 'Test Artist',
                'custom_domain': None
            }
        },
        {
            'id': 'analytics_overview',
            'name': 'Analytics Overview',
            'description': 'Get analytics overview data',
            'endpoint': 'analytics/overview',
            'method': 'GET',
            'category': 'Analytics',
            'params': {
                'period': '7d'
            },
            'data': None
        },
        {
            'id': 'analytics_clicks',
            'name': 'Click Analytics',
            'description': 'Get detailed click analytics',
            'endpoint': 'analytics/clicks',
            'method': 'GET',
            'category': 'Analytics',
            'params': {
                'period': '30d',
                'group_by': 'day'
            },
            'data': None
        },
        {
            'id': 'artists_list',
            'name': 'List Artists',
            'description': 'Retrieve all artists',
            'endpoint': 'artists',
            'method': 'GET',
            'category': 'Artists',
            'data': None
        },
        {
            'id': 'releases_list',
            'name': 'List Releases',
            'description': 'Retrieve all releases',
            'endpoint': 'releases',
            'method': 'GET',
            'category': 'Releases',
            'data': None
        },
        {
            'id': 'campaigns_list',
            'name': 'List Campaigns',
            'description': 'Retrieve all marketing campaigns',
            'endpoint': 'campaigns',
            'method': 'GET',
            'category': 'Campaigns',
            'data': None
        },
        {
            'id': 'pixels_list',
            'name': 'List Tracking Pixels',
            'description': 'Retrieve all tracking pixels',
            'endpoint': 'pixels',
            'method': 'GET',
            'category': 'Tracking',
            'data': None
        },
        {
            'id': 'webhooks_list',
            'name': 'List Webhooks',
            'description': 'Retrieve configured webhooks',
            'endpoint': 'webhooks',
            'method': 'GET',
            'category': 'Webhooks',
            'data': None
        }
    ]
    
    # Filter tests based on selection
    if selected_tests == 'all':
        test_cases = all_test_cases
    elif isinstance(selected_tests, list):
        test_cases = [t for t in all_test_cases if t['id'] in selected_tests]
    else:
        test_cases = all_test_cases
    
    # Run each test
    for test in test_cases:
        result = run_single_test(test)
        test_results.append(result)
    
    # Calculate statistics
    total = len(test_results)
    passed = sum(1 for r in test_results if r['status'] == 'passed')
    failed = sum(1 for r in test_results if r['status'] == 'failed')
    
    # Store in history
    test_run = {
        'timestamp': datetime.now().isoformat(),
        'total': total,
        'passed': passed,
        'failed': failed,
        'results': test_results
    }
    test_history.append(test_run)
    
    # Keep only last 10 runs in history
    if len(test_history) > 10:
        test_history = test_history[-10:]
    
    return jsonify(test_run)

def run_single_test(test):
    """Run a single API test with comprehensive error handling"""
    start_time = time.time()
    
    headers = {
        'X-API-Key': API_KEY,
        'X-ISS': ISS,
        'X-Secret-Key': SECRET_KEY,
        'Content-Type': 'application/json'
    }
    
    url = f"{BASE_URL}/{test['endpoint']}"
    
    # Add query parameters if present
    params = test.get('params', None)
    
    try:
        # Make the request
        if test['method'] == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=10)
        elif test['method'] == 'POST':
            response = requests.post(url, headers=headers, json=test['data'], timeout=10)
        elif test['method'] == 'PUT':
            response = requests.put(url, headers=headers, json=test['data'], timeout=10)
        elif test['method'] == 'PATCH':
            response = requests.patch(url, headers=headers, json=test['data'], timeout=10)
        elif test['method'] == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=10)
        
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Determine test status
        if 200 <= response.status_code < 400:
            status = 'passed'
        else:
            status = 'failed'
        
        # Parse response body
        try:
            response_data = response.json()
        except:
            response_data = response.text[:500] if response.text else None
        
        return {
            'id': test.get('id', ''),
            'name': test['name'],
            'description': test['description'],
            'category': test.get('category', 'General'),
            'endpoint': test['endpoint'],
            'method': test['method'],
            'status': status,
            'statusCode': response.status_code,
            'duration': round(duration, 2),
            'timestamp': datetime.now().isoformat(),
            'response': response_data,
            'request': {
                'headers': {k: v[:20] + '...' if len(v) > 20 else v for k, v in headers.items()},
                'data': test.get('data'),
                'params': params
            }
        }
        
    except requests.exceptions.Timeout:
        return create_error_result(test, 'Timeout', time.time() - start_time)
    except requests.exceptions.ConnectionError:
        return create_error_result(test, 'Connection Error', time.time() - start_time)
    except Exception as e:
        return create_error_result(test, str(e), time.time() - start_time)

def create_error_result(test, error_message, duration):
    """Create a standardized error result"""
    return {
        'id': test.get('id', ''),
        'name': test['name'],
        'description': test['description'],
        'category': test.get('category', 'General'),
        'endpoint': test['endpoint'],
        'method': test['method'],
        'status': 'failed',
        'statusCode': 0,
        'duration': round(duration * 1000, 2),
        'timestamp': datetime.now().isoformat(),
        'error': error_message
    }

@app.route('/api/test-results', methods=['GET'])
def get_test_results():
    """Get the latest test results"""
    if not test_results:
        return jsonify({'message': 'No tests have been run yet'}), 404
    return jsonify(test_results)

@app.route('/api/test-history', methods=['GET'])
def get_test_history():
    """Get test run history"""
    return jsonify(test_history)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with API connectivity test"""
    api_status = 'unknown'
    
    # Try to verify API connectivity
    try:
        headers = {
            'X-API-Key': API_KEY,
            'X-ISS': ISS,
            'X-Secret-Key': SECRET_KEY
        }
        response = requests.get(f"{BASE_URL}/health", headers=headers, timeout=5)
        api_status = 'connected' if response.status_code < 500 else 'error'
    except:
        api_status = 'disconnected'
    
    return jsonify({
        'status': 'healthy',
        'service': 'Feature.fm API Test Dashboard',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'api_status': api_status,
        'environment': os.getenv('FLASK_ENV', 'production')
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"""
    ╔══════════════════════════════════════════════╗
    ║     Feature.fm API Test Dashboard            ║
    ║                                              ║
    ║     Running on: http://localhost:{port}      ║
    ║     Debug mode: {debug}                      ║
    ╚══════════════════════════════════════════════╝
    """)
    
    app.run(debug=debug, port=port, host='0.0.0.0')