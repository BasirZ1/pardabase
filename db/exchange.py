from typing import Optional

from helpers.format_list import format_dict
from utils import flatbed
from utils.conn import connection_context


async def update_fx_rates_in_db(rates) -> bool:
    """
    Updates the fx_current_rates table with new data.
    """
    try:
        async with connection_context() as conn:
            sql_upsert = """
                    INSERT INTO fx_current_rates 
                        (base_currency, quote_currency, rate, source, fetched_at, is_manual)
                    VALUES ($1, $2, $3, $4, now(), false)
                    ON CONFLICT (base_currency, quote_currency) 
                    DO UPDATE SET 
                        rate = EXCLUDED.rate,
                        fetched_at = now(),
                        source = EXCLUDED.source,
                        is_manual = false;
                """

            base_currency = "USD"
            source = "Open Exchange Rates"

            # Prepare data for the query
            # We transform the dict into a list of tuples for batch processing
            values = [
                (base_currency, quote, float(rate), source)
                for quote, rate in rates.items()
            ]

            await conn.executemany(sql_upsert, values)

            return True
    except Exception as e:
        await flatbed('exception', f"In update_fx_rates_in_db: {e}")
        return False


async def get_fx_current_rate(
        quote_currency: str = "AFN",
        base_currency: Optional[str] = "USD"
):
    """
        Get the fx_current_rate for a currency pair from the fx_current_rates table.
    """
    try:
        async with connection_context() as conn:
            sql_query = """
                        SELECT * from fx_current_rates
                        WHERE base_currency = $1
                        AND quote_currency = $2;
                    """

            data = await conn.fetchrow(sql_query, base_currency, quote_currency)
            print(data)
            if not data:
                return None
            return format_dict(data)
    except Exception as e:
        await flatbed('exception', f"In get_fx_current_rate: {e}")
        return None
