# Weather-Command-Line-interface-CLI-Aidid
WEATHER CLI TOOL - README
==========================

A simple command-line weather application that fetches current weather and 
3-day forecast from OpenWeatherMap API.

QUICK START
-----------
1. Get API key: Visit openweathermap.org/api, sign up (free), copy your key

2. Install and run:
   git clone <your-repo-url>
   cd weather-cli
   pip install -r requirements.txt
   export OPENWEATHER_API_KEY="your-key-here"
   python -m weather_cli.cli --city "Puchong" --country "MY"

3. That's it! You'll see current weather and 3-day forecast.

USAGE EXAMPLES
--------------
Basic usage:
python -m weather_cli.cli --city "Puchong" --country "MY"

Different cities:
python -m weather_cli.cli --city "New York" --country "US"
python -m weather_cli.cli --city "London" --country "GB"

Debug mode (see API calls):
python -m weather_cli.cli --city "Puchong" --country "MY" --debug

Fahrenheit instead of Celsius:
python -m weather_cli.cli --city "Chicago" --country "US" --units imperial

Save debug log:
python -m weather_cli.cli --city "Tokyo" --country "JP" --debug --log-file weather.log

INSTALLATION
------------
Quick install:
git clone <repo-url>
cd weather-cli
pip install -r requirements.txt

Clean install (recommended):
python -m venv weather-env
source weather-env/bin/activate  # Windows: weather-env\Scripts\activate
pip install -r requirements.txt

TROUBLESHOOTING
---------------
"API key not found":
- Set your API key: export OPENWEATHER_API_KEY="your-key"
- Or use: python -m weather_cli.cli --api-key "your-key" ...

"City not found":
- Use country codes (2 letters): --country "MY" not --country "Malaysia"
- Try: --city "New York" --country "US"

"Module not found":
- Make sure you're in weather-cli folder
- Set Python path: export PYTHONPATH=/path/to/weather-cli:$PYTHONPATH

Windows users:
set OPENWEATHER_API_KEY=your-key-here
python -m weather_cli.cli --city "Puchong" --country "MY"

COMMON COMMANDS
---------------
Daily weather check:
python -m weather_cli.cli --city "Puchong" --country "MY"

Before travel:
python -m weather_cli.cli --city "Paris" --country "FR"

Test your API key:
python -m weather_cli.cli test-api

Quick minimal output:
python -m weather_cli.cli quick --city "London" --country "GB"

COUNTRY CODES
-------------
Malaysia: MY
United States: US
United Kingdom: GB
Japan: JP
Australia: AU
Singapore: SG

Find your code: Google "ISO country code for [your country]"

RUNNING TESTS
-------------
Run all tests:
pytest -v

Run specific test:
pytest tests/test_weather_api.py -v

Run with coverage:
pytest --cov=weather_cli tests/

PROJECT STRUCTURE
-----------------
weather-cli/
├── weather_cli/          # Main package
│   ├── __init__.py     # Package setup
│   ├── cli.py          # Command-line interface
│   ├── weather_api.py  # API communication
│   ├── formatter.py    # Output formatting
│   └── exceptions.py   # Custom errors
├── tests/              # Unit tests
└── requirements.txt  # Dependencies

FEATURES
--------
- Current weather (temperature, conditions, humidity, wind)
- 3-day forecast (daily min/max temperatures)
- Works with any city worldwide
- Multiple output formats (simple, detailed, JSON)
- Debug mode with full logging
- Comprehensive error handling
- Unit tests with mocking
- Metric/imperial units
- Color-coded output (terminal dependent)

DEPENDENCIES
------------
requests          - HTTP API calls
click             - Command-line interface
python-dotenv     - Environment variables
colorlog          - Colored logging (optional)
pytest            - Testing framework

ENVIRONMENT VARIABLES
-------------------
OPENWEATHER_API_KEY - Your API key (required)
PYTHONPATH         - Path to weather-cli directory (if needed)

NEXT STEPS
----------
Users:
- Create aliases for frequent cities
- Set up daily weather checks
- Integrate into morning routine

Developers:
- Add new features (alerts, different units)
- Improve output formatting
- Add more weather APIs
- Build GUI version

SUPPORT
-------
1. Check troubleshooting section above
2. Run with --debug for detailed logs
3. Verify API key is set correctly
4. Ensure internet connection works
5. Try examples exactly as written

For issues: Check debug logs, verify inputs, test API key validity

ABOUT
-----
Made for developers who want quick weather info without opening apps or browsers. Simple, reliable, fast.

Version: 1.0.0
License: MIT
