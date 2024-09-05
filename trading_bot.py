import MetaTrader5 as mt
import pandas as pd
import time
from datetime import datetime, time as dt_time, timedelta
from pytz import timezone
from config import login, password, server

# Initialize and login to MetaTrader 5
if not mt.initialize():
    print("Error: Failed to initialize MetaTrader.")
    quit()

if not mt.login(login, password, server):
    print("Error: Failed to login.")
    quit()

# Retrieve and display account information
account_info = mt.account_info()
if account_info:
    print(f"\nLogin Number: {account_info.login}")
    print(f"Balance: {account_info.balance}")
    print(f"Equity: {account_info.equity}\n")
else:
    print("Error: Account not found.")
    quit()

# Constants
SYMBOL = "USDCAD"
QTY = 0.01
FOREVER = True
ITERATIONS = 10
SL_PCT = 0.05
TP_PCT = 0.1
BUY_ORDER_TYPE = mt.ORDER_TYPE_BUY
SELL_ORDER_TYPE = mt.ORDER_TYPE_SELL

def order_type_to_str(order_type):
    """Converts numeric order type to its string representation."""
    return "BUY" if order_type == BUY_ORDER_TYPE else "SELL"

def close_type_to_str(order_type):
    """Converts numeric close type to its string representation."""
    return "SELL" if order_type == BUY_ORDER_TYPE else "BUY"

def get_current_market_times():
    """Handles timezone for market times, including DST adjustment."""
    UTC_TIMEZONE = timezone("Etc/UTC")
    NYC_TIMEZONE = timezone("America/New_York")
    
    now_date = datetime.now(UTC_TIMEZONE).replace(second=0, microsecond=0)
    nyc_time = datetime.now(NYC_TIMEZONE)
    
    current_gmt = now_date + nyc_time.dst() + timedelta(hours=2)
    today_start_utc = datetime.combine(now_date.date(), dt_time.min).replace(tzinfo=UTC_TIMEZONE)
    today_gmt_start = today_start_utc + nyc_time.dst() + timedelta(hours=2)
    
    return today_gmt_start, current_gmt

def generate_ohlc(symbol):
    """Generates OHLC data for the given symbol and timeframe."""
    start_time, now = get_current_market_times()
    ohlc = pd.DataFrame(mt.copy_rates_range(symbol, mt.TIMEFRAME_M1, start_time, now))
    ohlc['time'] = pd.to_datetime(ohlc['time'], unit='s')
    return ohlc

def create_order_request(symbol, qty, order_type, price, sl, tp):
    """Creates a request dictionary for sending an order."""
    return {
        "action": mt.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": qty,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "comment": "Position Opened.",
        "type_time": mt.ORDER_TIME_GTC,
        "type_filling": mt.ORDER_FILLING_FOK,
    }

def create_close_request(symbol, qty, order_type, price):
    """Creates a request dictionary for closing an order."""
    positions = mt.positions_get()
    if positions:
        position_id = positions[0]._asdict()['ticket']
        return {
            "action": mt.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": qty,
            "type": order_type,
            "price": price,
            "position": position_id,
            "comment": "Position Closed.",
            "type_time": mt.ORDER_TIME_GTC,
            "type_filling": mt.ORDER_FILLING_FOK,
        }
    return None

def place_order(symbol, qty, order_type, price, sl, tp):
    """Places a market order."""
    request = create_order_request(symbol, qty, order_type, price, sl, tp)
    return mt.order_send(request)

def close_order(symbol, qty, close_type, price):
    """Closes an existing position."""
    request = create_close_request(symbol, qty, close_type, price)
    if request:
        return mt.order_send(request)
    print("No open position to close.")
    return None

def add_deal(deals, order_type, price, qty):
    """Adds a deal to the list of deals."""
    deals.append({
        "type": order_type,
        "profit": None,
        "price": price,
        "qty": qty,
    })
    return deals

def calculate_deal_profit(deals, close_price, qty):
    """Calculates and updates the profit for the last deal."""
    last_deal = deals[-1]
    price_diff = close_price - last_deal['price']
    if last_deal['type'] == SELL_ORDER_TYPE:
        price_diff *= -1  # reverse for sell orders
    
    profit = qty * price_diff
    last_deal['profit'] = round(profit, 2)  # round profit to 2 decimal places
    return deals

def initialize_conditions(ohlc):
    """Extracts the current, last close, high, and low prices for conditions."""
    current_close = ohlc['close'].iloc[-1]
    last_close = ohlc['close'].iloc[-2]
    last_high = ohlc['high'].iloc[-2]
    last_low = ohlc['low'].iloc[-2]
    
    return current_close, last_close, last_high, last_low

def get_price_info():
    """Gets the current buy and sell prices and calculates stop-loss and take-profit."""
    buy_price = mt.symbol_info_tick(SYMBOL).ask
    sell_price = mt.symbol_info_tick(SYMBOL).bid

    buy_sl = buy_price * (1 - SL_PCT)
    buy_tp = buy_price * (1 + TP_PCT)
    sell_sl = sell_price * (1 + SL_PCT)
    sell_tp = sell_price * (1 - TP_PCT)
    
    return buy_price, sell_price, buy_sl, buy_tp, sell_sl, sell_tp

def open_position(deals, order_type, price, sl, tp):
    """Handles placing orders, updating deal information."""
    order_type_str = order_type_to_str(order_type)
    order_total = round(QTY * price, 2)
    
    result = place_order(SYMBOL, QTY, order_type, price, sl, tp)
    if result and result.retcode == mt.TRADE_RETCODE_DONE:
        print(f"{order_type_str} Order Placed - {QTY} @ {price}; Total: {order_total}.")
        deals = add_deal(deals, order_type, price, QTY)
    else:
        print(f"Failed to place {order_type_str} order.")
    
    return deals

def close_position(deals, close_type, price):
    """Handles placing and closing orders, updating deal information."""
    close_type_str = close_type_to_str(close_type)
    close_total = round(QTY * price, 2)
    
    result = close_order(SYMBOL, QTY, close_type, price)
    if result and result.retcode == mt.TRADE_RETCODE_DONE:
        print(f"{close_type_str} Position Closed - {QTY} @ {price}; Total: {close_total}.")
        deals = calculate_deal_profit(deals, price, QTY)
        print(f"Profit Made From {close_type_str} Position: {deals[-1]['profit']}")
    else:
        print(f"Failed to close {close_type_str} position.")
    
    return deals

def execute_strategy(deals):
    """Executes the trading strategy for each iteration."""
    i = ITERATIONS
    while FOREVER or i > 0:
        print(f"Iteration: {ITERATIONS - i + 1}")
        
        ohlc = generate_ohlc(SYMBOL)
        current_close, last_close, last_high, last_low = initialize_conditions(ohlc)
        buy_price, sell_price, buy_sl, buy_tp, sell_sl, sell_tp = get_price_info()

        long_condition = current_close > last_high
        short_condition = current_close < last_low
        closelong_condition = current_close < last_close
        closeshort_condition = current_close > last_close

        positions = mt.positions_get()
        no_positions = len(positions) == 0
        already_buy = already_sell = False
        if positions:
            pos_type = positions[0]._asdict()['type']
            already_buy = pos_type == BUY_ORDER_TYPE
            already_sell = pos_type == SELL_ORDER_TYPE

        if long_condition and no_positions:
            deals = open_position(deals, BUY_ORDER_TYPE, buy_price, buy_sl, buy_tp)
        elif long_condition and already_sell:
            deals = close_position(deals, BUY_ORDER_TYPE, buy_price)
            deals = open_position(deals, BUY_ORDER_TYPE, buy_price, buy
