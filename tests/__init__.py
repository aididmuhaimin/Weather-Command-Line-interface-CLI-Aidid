"""
Test configuration and shared fixtures for Weather CLI tests.
"""

import pytest
import logging

# Test configuration
TEST_API_KEY = "test_api_key_1234567890"
TEST_CITY = "Puchong"
TEST_COUNTRY = "MY"
TEST_COORDINATES = (3.0, 101.5)

# Sample API responses for testing
SAMPLE_GEO_RESPONSE = [
    {
        'name': 'Puchong',
        'lat': 3.0,
        'lon': 101.5,
        'country': 'MY',
        'state': 'Selangor'
    }
]

SAMPLE_WEATHER_RESPONSE = {
    'coord': {'lon': 101.5, 'lat': 3.0},
    'weather': [
        {
            'id': 803,
            'main': 'Clouds',
            'description': 'broken clouds',
            'icon': '04d'
        }
    ],
    'main': {
        'temp': 28.5,
        'feels_like': 32.1,
        'temp_min': 26.0,
        'temp_max': 30.0,
        'pressure': 1012,
        'humidity': 75
    },
    'wind': {
        'speed': 2.57,
        'deg': 310
    },
    'name': 'Puchong',
    'sys': {
        'country': 'MY'
    }
}

SAMPLE_FORECAST_RESPONSE = {
    'list': [
        {
            'dt': 1705312800,
            'main': {
                'temp': 28.5,
                'temp_min': 25.0,
                'temp_max': 30.0,
                'pressure': 1012,
                'humidity': 75
            },
            'weather': [
                {
                    'id': 803,
                    'main': 'Clouds',
                    'description': 'broken clouds',
                    'icon': '04d'
                }
            ],
            'dt_txt': '2024-01-15 12:00:00'
        },
        {
            'dt': 1705323600,
            'main': {
                'temp': 27.0,
                'temp_min': 24.0,
                'temp_max': 29.0,
                'pressure': 1013,
                'humidity': 80
            },
            'weather': [
                {
                    'id': 500,
                    'main': 'Rain',
                    'description': 'light rain',
                    'icon': '10d'
                }
            ],
            'dt_txt': '2024-01-15 15:00:00'
        }
    ]
}

# Configure test logging
logging.basicConfig(level=logging.WARNING)