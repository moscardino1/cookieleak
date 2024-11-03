COOKIE_CATEGORIES = {
    'essential': {
        'patterns': ['csrf', 'session', 'token', 'auth', 'security', 'xsrf', 'cookie_consent', 'gdpr'],
        'icon': '🔧',
        'description': 'Required for the website to work'
    },
    'tracking': {
        'patterns': ['ga', 'analytics', 'track', 'visitor', '_gid', '_gat', 'utm_', 'pixel', 'beacon'],
        'icon': '👀',
        'description': 'Monitor your behavior'
    },
    'marketing': {
        'patterns': ['ad', 'campaign', 'promo', 'marketing', 'doubleclick', 'facebook', 'fb', 'twitter', 'linkedin'],
        'icon': '🎯',
        'description': 'Used for advertisements'
    }
}

COOKIE_PURPOSES = {
    'essential': {
        'csrf': 'Protects against cyber attacks',
        'session': 'Keeps you logged in',
        'token': 'Maintains your secure session',
        'security': 'Protects your browsing session',
        'default': 'Helps the website function properly'
    },
    'tracking': {
        'ga': 'Tracks how you use the website',
        'analytics': 'Monitors visitor behavior',
        'default': 'Monitors your activity on the site'
    },
    'marketing': {
        'ad': 'Helps show relevant advertisements',
        'campaign': 'Tracks marketing effectiveness',
        'default': 'Used for marketing purposes'
    }
} 