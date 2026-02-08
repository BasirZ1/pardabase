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

            await flatbed("info", f"Successfully updated {len(values)} currency rates in DB.")
            return True
    except Exception as e:
        await flatbed('exception', f"In add_payment_to_supplier: {e}")
        return False
