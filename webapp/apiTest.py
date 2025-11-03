import finnhub


API_KEY  = "d3i8h5hr01qr304gs2igd3i8h5hr01qr304gs2j0"
client = finnhub.Client(api_key=API_KEY)

def get_stock_info(symbol):
    try:
    
        profile = client.company_profile2(symbol=symbol)

        if not profile or "name" not in profile:
            print(f" '{symbol}' is not a valid ticker symbol.")
            return
        
        quote = client.quote(symbol)

        print("\nStock Information")
        print("-" * 40)
        print(f"Company: {profile.get('name', 'N/A')}")
        print(f"Ticker: {symbol.upper()}")
        print(f"Current Price: ${quote.get('c', 0):,.2f}")
        print(f"Open: ${quote.get('o', 0):,.2f}")
        print(f"High: ${quote.get('h', 0):,.2f}")
        print(f"Low: ${quote.get('l', 0):,.2f}")
        print(f"Previous Close: ${quote.get('pc', 0):,.2f}")
        print("-" * 40)

    except Exception as e:
        print(f"Error fetching data: {e}")

def main():
    while True:
        ticker = input("Enter a stock ticker (or 'q' to quit): ").strip().upper()
        if ticker == 'Q':
            break
        get_stock_info(ticker)

if __name__ == "__main__":
    main()