# Algorithmic Trading Bot using MetaTrader 5

This project is a Python-based algorithmic trading bot that connects to the MetaTrader 5 (MT5) trading platform via the MetaTrader 5 API. The bot automates trading strategies by continuously analyzing the market for the selected financial symbol (e.g., USDCAD) and executing buy or sell orders based on predefined conditions. It also manages open positions by setting stop-loss (SL) and take-profit (TP) limits and calculating profits after trades are closed.

## Table of Contents
1. [Project Features](#project-features)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [How It Works](#how-it-works)
5. [Usage](#usage)
6. [Dependencies](#dependencies)
7. [Contributing](#contributing)
8. [License](#license)

## Project Features

- **Automated Trading**: Places buy and sell orders based on technical market conditions such as price breaks (e.g., break of previous highs or lows).
- **Stop-Loss and Take-Profit Management**: Automatically calculates SL and TP levels for each order to manage risk and capture profits.
- **Order Placement and Closing**: Handles both opening new orders and closing existing ones when conditions are met.
- **Profit Calculation**: Tracks each deal and calculates profits upon closing positions.
- **Continuous Trading Loop**: Can execute the strategy indefinitely or for a set number of iterations.
- **Supports Multiple Financial Instruments**: The symbol being traded can be customized (e.g., USDCAD, EURUSD).
- **Configurable Parameters**: SL/TP percentages, trade quantity, and trading symbol can be customized via constants or a configuration file.

## Installation

To set up and run the trading bot, follow these steps:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/mt5-trading-bot.git
   cd mt5-trading-bot
   ```

2. **Install the Required Libraries:**

   Install the necessary Python packages listed in the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

   The main dependencies are:
   - `MetaTrader5`: Python API for MT5
   - `pandas`: For data handling and analysis
   - `pytz`: For handling time zones

3. **MetaTrader 5 Installation:**
   Ensure you have MetaTrader 5 installed on your machine and an account with a broker that supports MT5. You can download it from the [MetaTrader 5 website](https://www.metatrader5.com/en/download).

## Configuration

Before running the bot, you need to configure your account credentials and server information:

1. Create a file called `config.py` in the root directory of the project.
2. Inside `config.py`, define the following constants:

   ```python
   # config.py

   login = 'your_account_login'
   password = 'your_account_password'
   server = 'your_broker_server'
   ```

   Replace `'your_account_login'`, `'your_account_password'`, and `'your_broker_server'` with your actual MT5 account credentials.

## How It Works

The bot follows a simple strategy that operates based on the price movement of a given symbol (e.g., USDCAD):

1. **OHLC Data Generation**: The bot retrieves Open-High-Low-Close (OHLC) data for the selected symbol within a certain timeframe (e.g., 1-minute intervals).
2. **Market Analysis**: It checks if the current close price breaks the previous high or low, which triggers buy or sell conditions.
3. **Order Placement**: Depending on the conditions, the bot places buy or sell orders. SL and TP levels are calculated based on configurable percentages.
4. **Position Management**: The bot continuously monitors positions. If certain conditions are met, it closes positions and calculates the profit from the trade.
5. **Iteration Loop**: The bot runs either for a specified number of iterations or indefinitely, constantly analyzing the market and executing trades.

### Key Trading Logic:
- **Long Condition**: A buy order is placed if the current close price is higher than the previous high.
- **Short Condition**: A sell order is placed if the current close price is lower than the previous low.
- **Close Long Position**: A long position is closed if the current price falls below the previous close.
- **Close Short Position**: A short position is closed if the current price rises above the previous close.

## Usage

To run the trading bot:

1. Ensure that MetaTrader 5 is installed and running.
2. Ensure your MT5 account is configured in the `config.py` file.
3. Run the main script:

   ```bash
   python main.py
   ```

The bot will start executing trades based on the specified strategy and display information about orders placed, closed positions, and profits.

### Customization:

- **Symbol**: Modify the `SYMBOL` constant in the script to trade a different financial instrument (e.g., EURUSD, GBPUSD).
- **Quantity**: Change the `QTY` constant to adjust the volume of each trade.
- **Stop-Loss and Take-Profit**: Adjust `SL_PCT` and `TP_PCT` to change the percentage for stop-loss and take-profit levels.

## Dependencies

The project requires the following Python libraries:

- `MetaTrader5`: The official Python package for interacting with MetaTrader 5.
- `pandas`: Used for data manipulation, particularly OHLC data.
- `pytz`: For timezone and daylight saving time management.

These can be installed via:

```bash
pip install MetaTrader5 pandas pytz
```

Make sure to have a running MetaTrader 5 terminal on your machine for the bot to connect and interact with.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve the functionality or add new features to this bot.

### Guidelines:
- Ensure all contributions are well-documented and tested.
- Follow the existing code style for consistency.
- Open an issue to discuss major changes before submitting a PR.

## License

This project is licensed under the MIT License. You can freely use, modify, and distribute the code under the terms of this license.

---

Happy trading! If you encounter any issues or have suggestions for improvements, please open an issue on the GitHub repository.
