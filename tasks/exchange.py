import os

import requests
from dotenv import load_dotenv

from celery_app import celery_app
from db import update_fx_rates_in_db
from helpers import run_async
from utils import set_current_db, flatbed
from utils.config import AFN_ADJUSTMENT

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
    Get the latest exchange rates from Open Exchange Rates
    and apply a local adjustment to AFN only.
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

        if response.status_code != 200:
            await flatbed("500", f"Error: {response.status_code} - {response.text}")
            return None

        data = response.json()
        rates = data.get("rates", {})

        if "AFN" in rates:
            original_afn = rates["AFN"]
            adjusted_afn = round(original_afn * (1 - AFN_ADJUSTMENT), 4)
            rates["AFN"] = adjusted_afn
        else:
            await flatbed("missing", f"Error: AFN not in rates: {rates}")

        return rates

    except Exception as e:
        await flatbed("exception", f"Failed to return latest exchange rates from {url}: {e}")
        return None
