import os

import requests
from dotenv import load_dotenv

from celery_app import celery_app
from db import update_fx_rates_in_db
from helpers import run_async
from utils import set_current_db, flatbed


load_dotenv(override=True)
APP_ID = os.getenv('APP_ID')


@celery_app.task
def scheduled_fetch_current_rates():
    run_async(fetch_current_rates_and_update_db())


async def fetch_current_rates_and_update_db():
    main_db = "pardaaf_main"
    set_current_db(main_db)

    rates = await fetch_current_rates()
    if rates:
        await update_fx_rates_in_db(rates)


async def fetch_current_rates():
    """
    Get the latest exchange rates from the api and return them
    """
    url = "https://openexchangerates.org/api/latest.json"
    # Only app_id is required; others are optional filters
    query_params = {
        "app_id": APP_ID,
        "base": "USD",  # Optional: Default is USD
        # "symbols": "EUR,GBP,JPY",  # Optional: Limits results to these currencies
        "prettyprint": "false",  # Optional: Reduces response size
        "show_alternative": "false"  # Optional: Excludes black market/digital rates
    }
    try:
        response = requests.get(url, params=query_params)

        if response.status_code == 200:
            data = response.json()
            print(f"Base Currency: {data['base']}")
            print(f"Rates: {data['rates']}")
            await flatbed("info", f"Rates: {data['rates']}")
            return data['rates']
        else:
            await flatbed("500", f"Error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        await flatbed("exception", f"Failed to return latest exchange rates from {url}: {e}")
        return None
