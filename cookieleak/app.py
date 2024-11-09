from flask import Flask, render_template, request, jsonify
import json
import requests
from constants import COOKIE_CATEGORIES, COOKIE_PURPOSES

app = Flask(__name__)

def categorize_cookie(name):
    """Categorize cookie based on its name"""
    name = name.lower()
    for category, info in COOKIE_CATEGORIES.items():
        if any(pattern in name for pattern in info['patterns']):
            return category, info['icon'], info['description']
    # Return a friendly label for cookies that don't match any pattern
    return 'Others', '🔸', 'Miscellaneous purposes'

def analyze_cookie_purpose(name, category):
    """Get cookie purpose based on its name and category"""
    name = name.lower()
    if category in COOKIE_PURPOSES:
        for pattern, purpose in COOKIE_PURPOSES[category].items():
            if pattern in name and pattern != 'default':
                return purpose
        return COOKIE_PURPOSES[category]['default']
    return 'General website functionality'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        url = request.form.get('url', '')
        url = f'https://{url.strip().lower().replace("http://", "").replace("https://", "").split("/")[0]}'
        session = requests.Session()
        response = session.get(url, timeout=5,
                               headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'},
                               allow_redirects=True)

        cookies_data = []
        all_cookies = {**session.cookies.get_dict(), **response.cookies.get_dict()}
        
        for name, value in all_cookies.items():
            category, icon, description = categorize_cookie(name)
            cookie_info = {
                'name': name,
                'value': value,
                'category': category,
                'category_icon': icon,
                'category_description': description,
                'risk_level': analyze_cookie_risk(name, value),
                'purpose': analyze_cookie_purpose(name, category),
                'data_collected': analyze_cookie_content(name, value)
            }
            cookies_data.append(cookie_info)

        return jsonify({
            'cookies': cookies_data,
            'stats': {
                'total_cookies': len(cookies_data),
                'high_risk': len([c for c in cookies_data if c['risk_level'] == 'High']),
                'medium_risk': len([c for c in cookies_data if c['risk_level'] == 'Medium']),
                'low_risk': len([c for c in cookies_data if c['risk_level'] == 'Low'])
            }
        })
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'})

def analyze_cookie_risk(name, value):
    name = name.lower()
    high_risk_indicators = ['id', 'uid', 'guid', 'track', 'analytic', 'visitor']
    medium_risk_indicators = ['pref', 'session', 'login', 'auth']
    if any(indicator in name for indicator in high_risk_indicators):
        return 'High'
    if any(indicator in name for indicator in medium_risk_indicators):
        return 'Medium'
    return 'Low'

def analyze_cookie_content(name, value):
    collected_data = []
    if len(value) > 100:
        collected_data.append(f"Large data string ({len(value)} characters)")
    try:
        json_data = json.loads(value)
        collected_data.append(f"Structured data: {list(json_data.keys())}")
    except:
        if value.isdigit():
            collected_data.append(f"Numeric identifier: {value}")
        elif '.' in value and all(part.isdigit() for part in value.split('.')):
            collected_data.append(f"Version or ID: {value}")
        elif len(value) in [32, 64]:
            collected_data.append(f"Hashed identifier ({len(value)} characters)")
        elif 'true' in value.lower() or 'false' in value.lower():
            collected_data.append(f"Boolean setting: {value}")
        else:
            preview = value[:50] + '...' if len(value) > 50 else value
            collected_data.append(f"Value: {preview}")
    return collected_data

if __name__ == '__main__':
    app.run(debug=True)
