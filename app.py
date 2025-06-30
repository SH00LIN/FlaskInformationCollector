import os
import logging
import yaml
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from io import StringIO, BytesIO
import json
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback-secret-key-for-development")

def validate_service_name(service_name):
    """Validate service name - should be non-empty and contain only valid characters"""
    if not service_name or not service_name.strip():
        return False, "Service name is required"
    
    # Check for valid filename characters
    if not re.match(r'^[a-zA-Z0-9_-]+$', service_name.strip()):
        return False, "Service name can only contain letters, numbers, underscores, and hyphens"
    
    return True, ""

def validate_url(url):
    """Basic URL validation"""
    if not url or not url.strip():
        return False, "URL is required"
    
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url.strip()):
        return False, "Please enter a valid URL (must start with http:// or https://)"
    
    return True, ""

def validate_status_code(status_code):
    """Validate HTTP status code"""
    try:
        code = int(status_code)
        if 100 <= code <= 599:
            return True, ""
        else:
            return False, "Status code must be between 100 and 599"
    except (ValueError, TypeError):
        return False, "Status code must be a valid number"

def validate_repeat(repeat):
    """Validate repeat count"""
    try:
        count = int(repeat)
        if count >= 1:
            return True, ""
        else:
            return False, "Repeat count must be at least 1"
    except (ValueError, TypeError):
        return False, "Repeat count must be a valid number"

def validate_payload(payload, method):
    """Validate payload format if provided"""
    if not payload or not payload.strip():
        return True, ""  # Empty payload is allowed
    
    # For GET and DELETE methods, payload should typically be empty
    if method.upper() in ['GET', 'DELETE'] and payload.strip():
        return False, f"Payload is not typically used with {method.upper()} method"
    
    # Try to validate JSON if it looks like JSON
    payload = payload.strip()
    if payload.startswith('{') or payload.startswith('['):
        try:
            json.loads(payload)
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON format: {str(e)}"
    
    return True, ""

def validate_form_data(form_data):
    """Validate the entire form data"""
    errors = []
    
    # Validate service name
    service_name = form_data.get('service_name', '').strip()
    is_valid, error = validate_service_name(service_name)
    if not is_valid:
        errors.append(error)
    
    # Validate APIs
    apis = form_data.get('apis', [])
    if not apis:
        errors.append("At least one API is required")
    
    for i, api in enumerate(apis):
        api_prefix = f"API {i+1}: "
        
        # Validate API name
        if not api.get('name', '').strip():
            errors.append(f"{api_prefix}API name is required")
        
        # Validate URL
        is_valid, error = validate_url(api.get('url', ''))
        if not is_valid:
            errors.append(f"{api_prefix}{error}")
        
        # Validate method
        method = api.get('method', '')
        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        if method not in valid_methods:
            errors.append(f"{api_prefix}Invalid HTTP method")
        
        # Validate status code
        is_valid, error = validate_status_code(api.get('status_code', '200'))
        if not is_valid:
            errors.append(f"{api_prefix}{error}")
        
        # Validate repeat
        is_valid, error = validate_repeat(api.get('repeat', '1'))
        if not is_valid:
            errors.append(f"{api_prefix}{error}")
        
        # Validate payload
        is_valid, error = validate_payload(api.get('payload', ''), method)
        if not is_valid:
            errors.append(f"{api_prefix}{error}")
        
        # Validate headers
        headers = api.get('headers', [])
        for j, header in enumerate(headers):
            if not header.get('key', '').strip():
                errors.append(f"{api_prefix}Header {j+1}: Key is required")
            if not header.get('value', '').strip():
                errors.append(f"{api_prefix}Header {j+1}: Value is required")
        
        # Validate extractors
        extractors = api.get('extractors', [])
        for j, extractor in enumerate(extractors):
            if not extractor.get('key', '').strip():
                errors.append(f"{api_prefix}Extractor {j+1}: Key is required")
            if not extractor.get('value', '').strip():
                errors.append(f"{api_prefix}Extractor {j+1}: Value is required")
            if extractor.get('type', '') not in ['header', 'body']:
                errors.append(f"{api_prefix}Extractor {j+1}: Type must be either 'header' or 'body'")
    
    return errors

def generate_yaml_content(form_data):
    """Generate YAML content from form data"""
    service_name = form_data.get('service_name', '').strip()
    apis = form_data.get('apis', [])
    
    yaml_data = {'api_taste': []}
    
    for api in apis:
        api_config = {
            'api_name': api.get('name', '').strip(),
            'method': api.get('method', 'GET'),
            'url': api.get('url', '').strip(),
            'status_code': int(api.get('status_code', 200)),
            'repeat': int(api.get('repeat', 1))
        }
        
        # Add headers if present
        headers = api.get('headers', [])
        if headers:
            api_config['headers'] = {}
            for header in headers:
                key = header.get('key', '').strip()
                value = header.get('value', '').strip()
                if key and value:
                    api_config['headers'][key] = value
        
        # Add payload if present
        payload = api.get('payload', '').strip()
        if payload:
            api_config['payload'] = payload
        
        # Add extractors if present
        extractors = api.get('extractors', [])
        if extractors:
            extract_config = {'header': {}, 'body': {}}
            has_extractors = False
            
            for extractor in extractors:
                key = extractor.get('key', '').strip()
                value = extractor.get('value', '').strip()
                extractor_type = extractor.get('type', '').strip()
                
                if key and value and extractor_type in ['header', 'body']:
                    extract_config[extractor_type][key] = value
                    has_extractors = True
            
            # Only add extract section if there are actual extractors
            if has_extractors:
                api_config['extract'] = {}
                if extract_config['header']:
                    api_config['extract']['header'] = extract_config['header']
                if extract_config['body']:
                    api_config['extract']['body'] = extract_config['body']
        
        yaml_data['api_taste'].append(api_config)
    
    # Convert to YAML string
    yaml_string = yaml.dump(yaml_data, default_flow_style=False, sort_keys=False)
    return yaml_string

@app.route('/')
def index():
    """Main page with the form"""
    return render_template('index.html')

@app.route('/generate_yaml', methods=['POST'])
def generate_yaml():
    """Generate and download YAML file"""
    try:
        # Get JSON data from request
        form_data = request.get_json()
        
        if not form_data:
            return jsonify({'success': False, 'errors': ['No data received']})
        
        # Validate form data
        errors = validate_form_data(form_data)
        if errors:
            return jsonify({'success': False, 'errors': errors})
        
        # Generate YAML content
        yaml_content = generate_yaml_content(form_data)
        service_name = form_data.get('service_name', '').strip()
        filename = f"{service_name}.yaml"
        
        # Create BytesIO object for file download
        yaml_bytes = BytesIO()
        yaml_bytes.write(yaml_content.encode('utf-8'))
        yaml_bytes.seek(0)
        
        # Return success with YAML content for download
        return jsonify({
            'success': True, 
            'yaml_content': yaml_content,
            'filename': filename
        })
        
    except Exception as e:
        app.logger.error(f"Error generating YAML: {str(e)}")
        return jsonify({'success': False, 'errors': [f'Server error: {str(e)}']})

@app.route('/download_yaml', methods=['POST'])
def download_yaml():
    """Download YAML file"""
    try:
        data = request.get_json()
        yaml_content = data.get('yaml_content', '')
        filename = data.get('filename', 'service.yaml')
        
        # Create BytesIO object
        yaml_bytes = BytesIO()
        yaml_bytes.write(yaml_content.encode('utf-8'))
        yaml_bytes.seek(0)
        
        return send_file(
            yaml_bytes,
            mimetype='application/x-yaml',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        app.logger.error(f"Error downloading YAML: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)