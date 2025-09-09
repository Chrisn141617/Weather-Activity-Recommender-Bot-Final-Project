
# weather_data.py
from abc import ABC, abstractmethod
import requests

class WeatherFetcher(ABC):
    """
    Abstract class for fetching weather data.
    """
    @abstractmethod
    def fetch_weather(self, city: str):
        pass

class WeatherStackFetcher(WeatherFetcher):
    """
    Concrete implementation for Weatherstack API.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.weatherstack.com/current"

    def fetch_weather(self, city: str):
        """
        Fetch weather data for a given city from the Weatherstack API.
        """
        params = {
            'access_key': self.api_key,
            'query': city,
            'units': 'f'
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                raise ValueError(f"Error: {data['error']['info']}")
            return data
        else:
            raise ConnectionError("Error fetching data. Please check the API endpoint and try again.")



# activity_recommender.py
from abc import ABC, abstractmethod
import random

class ActivityRecommender(ABC):
    """
    Abstract class for recommending activities based on weather data.
    """
    @abstractmethod
    def recommend(self, weather_data):
        pass

class SimpleActivityRecommender(ActivityRecommender):
    """
    Concrete implementation of activity recommendation.
    """
    def recommend(self, weather_data):
        temp = weather_data['current']['temperature']
        weather_condition = weather_data['current']['weather_descriptions'][0]
        precipitation = weather_data['current']['precip']

        activities = []
        if temp > 86:
            activities = [
                "Go for a swim",
                "Stay indoors and enjoy some cold drinks",
                "Visit an air-conditioned museum"
            ]
        elif 68 <= temp <= 86:
            activities = [
                "Go for a run",
                "Enjoy a picnic in the park",
                "Have a refreshing lemonade outdoors"
            ]
        elif 50 <= temp < 68:
            activities = [
                "Grab a warm drink and read a book",
                "Visit a local cafe",
                "Take a brisk walk in the fresh air"
            ]
        else:
            activities = [
                "Stay inside with hot chocolate",
                "Build a snowman (if snowy)",
                "Watch a movie under a blanket"
            ]

        recommendation = random.choice(activities)
        return {
            "temperature": temp,
            "weather_condition": weather_condition,
            "precipitation": precipitation,
            "activity": recommendation
        }


# main.py
def main():
    """
    Main program to fetch weather data and recommend activities.
    """
    api_key = "0eeba9d44a7ebb58188097b20843451c"  # Replace with your Weatherstack API key
    weather_fetcher = WeatherStackFetcher(api_key)
    recommender = SimpleActivityRecommender()

    print("Welcome to the Weather Activity Recommender!")
    city = input("Please enter the city you'd like to see the weather for: ")
    region = input("Please also enter the state or country (to avoid confusion with duplicate city names):")

    location = f"{city}, {region}"

    try:
        print(f"Fetching weather information for {location}...")
        weather_data = weather_fetcher.fetch_weather(location)
        recommendation = recommender.recommend(weather_data)

        print("\nWeather Report:")
        print(f"Temperature: {recommendation['temperature']} °F")
        print(f"Weather Condition: {recommendation['weather_condition']}")
        print(f"Precipitation: {recommendation['precipitation']} inches")
        print("\nRecommended Activity:")
        print(recommendation['activity'])
    except Exception as e:
        print(f"An error occurred: {e}")

    print("Thank You For Using Our Program! Have A Great Day!")

# Run the program
if __name__ == "__main__":
    main()


import unittest
from unittest.mock import patch

class TestWeatherStackFetcher(unittest.TestCase):
    """
    Tests for the WeatherStackFetcher class.
    """
    @patch('requests.get')
    def test_fetch_weather_success(self, mock_get):
        """
        Test successful weather data fetch from the API.
        """
        # Mock API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'current': {
                'temperature': 75,
                'weather_descriptions': ['Partly Cloudy'],
                'precip': 0
            }
        }

        # Create instance of WeatherStackFetcher
        fetcher = WeatherStackFetcher(api_key="fake_api_key")
        result = fetcher.fetch_weather("Paris, France")

        # Assert fetched data
        self.assertEqual(result['current']['temperature'], 75)
        self.assertEqual(result['current']['weather_descriptions'][0], 'Partly Cloudy')
        self.assertEqual(result['current']['precip'], 0)

    @patch('requests.get')
    def test_fetch_weather_error(self, mock_get):
        """
        Test error response from the API.
        """
        # Mock API response with error
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'error': {'info': 'Invalid API key.'}
        }

        fetcher = WeatherStackFetcher(api_key="fake_api_key")

        # Assert that a ValueError is raised
        with self.assertRaises(ValueError) as context:
            fetcher.fetch_weather("TestCity")

        self.assertIn('Invalid API key.', str(context.exception))


class TestSimpleActivityRecommender(unittest.TestCase):
    """
    Tests for the SimpleActivityRecommender class.
    """
    def test_recommend_activity_hot_weather(self):
        """
        Test activity recommendation for hot weather (>86°F).
        """
        recommender = SimpleActivityRecommender()
        weather_data = {
            'current': {
                'temperature': 90,
                'weather_descriptions': ['Sunny'],
                'precip': 0
            }
        }

        # Get recommendation
        recommendation = recommender.recommend(weather_data)

        # Assert recommendation is from the hot weather list
        self.assertIn(recommendation['activity'], [
            "Go for a swim",
            "Stay indoors and enjoy some cold drinks",
            "Visit an air-conditioned museum"
        ])

    def test_recommend_activity_warm_weather(self):
        """
        Test activity recommendation for warm weather (68-86°F).
        """
        recommender = SimpleActivityRecommender()
        weather_data = {
            'current': {
                'temperature': 75,
                'weather_descriptions': ['Partly Cloudy'],
                'precip': 0
            }
        }

        # Get recommendation
        recommendation = recommender.recommend(weather_data)

        # Assert recommendation is from the warm weather list
        self.assertIn(recommendation['activity'], [
            "Go for a run",
            "Enjoy a picnic in the park",
            "Have a refreshing lemonade outdoors"
        ])

    def test_recommend_activity_cold_weather(self):
        """
        Test activity recommendation for cold weather (<50°F).
        """
        recommender = SimpleActivityRecommender()
        weather_data = {
            'current': {
                'temperature': 30,
                'weather_descriptions': ['Snowy'],
                'precip': 2
            }
        }

        recommendation = recommender.recommend(weather_data)

        self.assertIn(recommendation['activity'], [
            "Stay inside with hot choclate",
            "Build a snowman (if snowy)",
            "Watch a movie under a blanket"
        ])

        
if __name__ == "__main__":
    # Use verbosity to ensure test results are printed in Colab
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWeatherStackFetcher)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestSimpleActivityRecommender)
    unittest.TextTestRunner(verbosity=2).run(suite)

# If given 2 OK's then all test ran good