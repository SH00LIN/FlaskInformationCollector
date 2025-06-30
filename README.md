# API YAML Configuration Generator

## Overview

This is a Flask-based web application that provides a user-friendly interface for generating YAML configuration files for API testing. The application allows users to define multiple APIs with their configurations (headers, methods, payloads, etc.) through a dynamic web form and generates downloadable YAML files.

## System Architecture

The application follows a simple Flask web application architecture with a clear separation between frontend and backend components:

- **Frontend**: HTML templates with Bootstrap styling and vanilla JavaScript for dynamic form management
- **Backend**: Flask application with form validation and YAML generation capabilities
- **Static Assets**: CSS and JavaScript files served directly by Flask

## Key Components

### Backend Components

1. **Flask Application (`app.py`)**
   - Main application entry point with form handling and validation logic
   - Implements validation functions for service names, URLs, and status codes
   - Configured with proxy support and session management

2. **Application Runner (`main.py`)**
   - Simple entry point that runs the Flask development server
   - Configured to run on all interfaces (0.0.0.0) on port 5000

### Frontend Components

1. **HTML Template (`templates/index.html`)**
   - Bootstrap-based responsive interface with dark theme support
   - Dynamic form structure for API configuration
   - Alert system for error handling and success messages

2. **CSS Styling (`static/css/custom.css`)**
   - Custom styles extending Bootstrap theme
   - Dark mode support with theme-aware styling
   - Enhanced visual feedback for form interactions

3. **JavaScript Form Manager (`static/js/form-manager.js`)**
   - Handles dynamic addition/removal of API configurations
   - Manages headers and extractors for each API
   - Form validation and YAML generation requests

### Validation System

The application implements comprehensive validation for:
- Service names (alphanumeric with underscores and hyphens only)
- URLs (proper HTTP/HTTPS format validation)
- Status codes (valid HTTP status code ranges)

## Data Flow

1. **User Input**: Users fill out the web form with service and API configurations
2. **Client-side Validation**: JavaScript performs initial validation and form management
3. **Server-side Processing**: Flask validates input data and generates YAML content
4. **File Generation**: Valid configurations are converted to YAML format
5. **Download**: Generated YAML files are served for download with appropriate naming

## External Dependencies

### Python Dependencies
- **Flask**: Web framework for handling HTTP requests and rendering templates
- **PyYAML**: YAML parsing and generation (implied by functionality)
- **Werkzeug**: WSGI utilities including proxy fix middleware

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme support (CDN)
- **Font Awesome 6**: Icon library (CDN)

## Deployment Strategy

The application is configured for development deployment with:
- Debug mode enabled for development
- Proxy fix middleware for deployment behind reverse proxies
- Environment-based secret key configuration
- Host binding to all interfaces (0.0.0.0) for container compatibility

**Production Considerations**:
- Debug mode should be disabled
- Secret key should be set via environment variable
- Consider using a production WSGI server (Gunicorn, uWSGI)
- Static file serving should be handled by a web server (nginx)

## Changelog

```
Changelog:
- June 29, 2025. Initial setup
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```

## Notes for Development

- The application generates YAML files with a specific structure for API testing configurations
- Form validation prevents common input errors and ensures proper file naming
- The frontend uses vanilla JavaScript to avoid additional build dependencies
- Error handling provides clear feedback to users for validation failures
- The application supports multiple APIs per service with individual configuration options