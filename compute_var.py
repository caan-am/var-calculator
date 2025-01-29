import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# ### Inputs
# shares = ["CRESY", "AAPL", "NVDA"] VET, MOH
# quintet_portfolio_value = 600000
# num_shares = [1000.0, 500.0, 200.0]
# price_shares = [12.5, 229.0, 118.0]
# confidence_level = 0.05
# currency_shares = ["EUR", "USD", "EUR"]
#TODO - Si no encuentra serie tener alguna precargadad desde Investing pro

def calculate_var(
    shares,
    num_shares,
    price_shares,
    currency_shares,
    quintet_portfolio_value,
    confidence_level,
):

    fx_shares = []
    for currency in currency_shares:
        pair = f"EUR{currency}=X"  # Formar el ticker del par de divisas
        try:
            # Descargar el precio actual del par
            ticker = yf.Ticker(pair)
            current_price = ticker.history(period="1d")["Close"].iloc[-1]
            fx_shares.append(current_price)  # Agregar el tipo de cambio a la lista
        except Exception as e:
            # En caso de error, agregar None o algún valor por defecto
            fx_shares.append(None)
            print(f"Error obteniendo tipo de cambio para {currency}: {e}")

    todays_date = datetime.today().strftime("%Y-%m-%d")
    first_date = (datetime.today() - timedelta(days=365 * 2)).strftime("%Y-%m-%d")

    historical_prices = pd.DataFrame(columns=shares)

    for share in shares:
        # Descargar datos
        historical_prices[share] = yf.download(
            share, start=first_date, end=todays_date
        )["Close"]

    historical_return = np.log(historical_prices / historical_prices.shift(1))
    shares_amount = [a * b for a, b in zip(num_shares, price_shares)]
    shares_amount_fx = [a * b for a, b in zip(shares_amount, fx_shares)]
    cash_amount = quintet_portfolio_value - sum(shares_amount_fx)
    shares_amount_fx.append(cash_amount)
    weights = [(num / sum(shares_amount_fx)) for num in shares_amount_fx]
    historical_return["Cash"] = 0

    portfolio_return = historical_return.dot(weights)
    var_percentile = portfolio_return.quantile(confidence_level)
    var = abs(var_percentile * quintet_portfolio_value)

    portfolio_return.to_excel("output/portfolio_return.xlsx")
    historical_return.to_excel("output/historical_return.xlsx")

    return var
