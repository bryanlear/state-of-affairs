#!/usr/bin/env python3
"""
Custom Schwab API Quotes Fetcher

Fetches current quotes for specific symbols including Auto Manufacturers and S&P 500.
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# European Auto Manufacturer stocks
SYMBOLS = {
    "VWAGY": "Volkswagen AG",
    "MBGYY": "Mercedes-Benz Group AG",
    "BMWYY": "BMW AG",
    "RACE": "Ferrari N.V.",
    "POAHY": "Porsche Automobil Holding SE",
    "STLA": "Stellantis N.V.",

    "^GSPC": "S&P 500 Index",

    "CARZ": "First Trust NASDAQ Transportation ETF",
    "IDRV": "iShares Self-Driving EV and Tech ETF"
}

BASE_URL = "https://api.schwabapi.com/marketdata/v1"


def load_access_token(token_path: str = "tokens.json") -> str:
    """Load access token from tokens file."""
    try:
        with open(token_path, 'r') as f:
            tokens = json.load(f)
        
        if 'access_token' not in tokens:
            raise ValueError("No access_token found in tokens file")
        
        return tokens['access_token']
    
    except FileNotFoundError:
        logger.error(f"Token file {token_path} not found. Run schwab.py first to authenticate.")
        raise
    except Exception as e:
        logger.error(f"Error loading access token: {e}")
        raise


def get_quotes(symbols_list):
    """Get current quotes for specified symbols."""
    
    access_token = load_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    symbols_str = ",".join(symbols_list)
    
    logger.info(f"Fetching quotes for {len(symbols_list)} symbols...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/quotes",
            params={"symbols": symbols_str},
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"API request failed: {response.status_code} - {response.text}")
            return None
        
        data = response.json()
        results = []
        
        for symbol in symbols_list:
            if symbol in data:
                quote_data = data[symbol]["quote"]
                
                last_price = quote_data.get("lastPrice", 0)
                close_price = quote_data.get("closePrice", last_price)
                
                pct_change = ((last_price / close_price) - 1) * 100 if close_price != 0 else 0
                
                volume = quote_data.get("totalVolume", 0)
                high_52w = quote_data.get("52WeekHigh", 0)
                low_52w = quote_data.get("52WeekLow", 0)
                market_cap = quote_data.get("marketCap", 0)
                
                results.append({
                    "Symbol": symbol,
                    "Company": SYMBOLS.get(symbol, "Unknown"),
                    "Last_Price": round(last_price, 2),
                    "Prev_Close": round(close_price, 2),
                    "Change_%": round(pct_change, 2),
                    "Volume": f"{volume:,}",
                    "52W_High": round(high_52w, 2),
                    "52W_Low": round(low_52w, 2),
                    "Market_Cap": f"{market_cap:,}" if market_cap > 0 else "N/A"
                })
            else:
                logger.warning(f"No data returned for {symbol}")
        
        return pd.DataFrame(results)
        
    except Exception as e:
        logger.error(f"Error fetching quotes: {e}")
        return None


def display_results(df):
    """Display formatted results."""
    if df is None or df.empty:
        print("No data to display")
        return

    auto_stocks = df[~df['Symbol'].isin(['^GSPC', 'CARZ', 'IDRV'])].copy()
    indices_etfs = df[df['Symbol'].isin(['^GSPC', 'CARZ', 'IDRV'])].copy()
    
    print("\n" + "="*120)
    print("EUROPEAN AUTO MANUFACTURERS & MARKET INDICES - CURRENT SESSION")
    print("="*120)
    print(f"Data as of: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*120)

    if not indices_etfs.empty:
        print("\nMARKET INDICES & AUTO ETFs:")
        print("-"*120)
        indices_sorted = indices_etfs.sort_values('Change_%', ascending=False)
        
        print(f"{'Symbol':<8} {'Name':<35} {'Price':<10} {'Change%':<10} {'Volume':<15} {'52W High':<10} {'52W Low':<10}")
        print("-"*120)
        
        for _, row in indices_sorted.iterrows():
            change_str = f"{row['Change_%']:+.2f}%"
            print(f"{row['Symbol']:<8} {row['Company'][:34]:<35} "
                  f"${row['Last_Price']:<9.2f} {change_str:<10} "
                  f"{row['Volume']:<15} ${row['52W_High']:<9.2f} ${row['52W_Low']:<9.2f}")

    if not auto_stocks.empty:
        print(f"\nEUROPEAN AUTO MANUFACTURERS:")
        print("-"*120)
        auto_sorted = auto_stocks.sort_values('Change_%', ascending=False)
        
        print(f"{'Symbol':<8} {'Company':<35} {'Price':<10} {'Change%':<10} {'Volume':<15} {'52W High':<10} {'52W Low':<10}")
        print("-"*120)
        
        for _, row in auto_sorted.iterrows():
            change_str = f"{row['Change_%']:+.2f}%"
            print(f"{row['Symbol']:<8} {row['Company'][:34]:<35} "
                  f"${row['Last_Price']:<9.2f} {change_str:<10} "
                  f"{row['Volume']:<15} ${row['52W_High']:<9.2f} ${row['52W_Low']:<9.2f}")
    
    print("-"*120)

    if not auto_stocks.empty:
        avg_change = auto_stocks['Change_%'].mean()
        best = auto_sorted.iloc[0]
        worst = auto_sorted.iloc[-1]
        
        print(f"\nEUROPEAN AUTO MANUFACTURERS SUMMARY:")
        print(f"Best performer: {best['Symbol']} ({best['Company'][:30]}) {best['Change_%']:+.2f}%")
        print(f"Worst performer: {worst['Symbol']} ({worst['Company'][:30]}) {worst['Change_%']:+.2f}%")
        print(f"Average change: {avg_change:+.2f}%")

        positive = len(auto_stocks[auto_stocks['Change_%'] > 0])
        negative = len(auto_stocks[auto_stocks['Change_%'] < 0])
        unchanged = len(auto_stocks[auto_stocks['Change_%'] == 0])

        print(f"European auto stocks: {positive} up, {negative} down, {unchanged} unchanged")


def main():
    """Main function."""
    try:
        print("Schwab API - European Auto Manufacturers & Market Indices")
        print("=========================================================")

        symbols_list = list(SYMBOLS.keys())

        df = get_quotes(symbols_list)
        
        if df is not None:
            display_results(df)
            
            save = input("\nSave to CSV? (y/N): ").strip().lower()
            if save in ['y', 'yes']:
                filename = f"eu_auto_quotes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False)
                print(f"Data saved to {filename}")
        else:
            print("Failed to retrieve quotes")
            
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
