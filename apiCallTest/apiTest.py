from flask import Flask, request, render_template_string
import finnhub

API_KEY  = "d3i8h5hr01qr304gs2igd3i8h5hr01qr304gs2j0"
client = finnhub.Client(api_key=API_KEY)

app = Flask(__name__)

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Stock Info Viewer</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body { font-family: system-ui, Arial; background: #0b1020; color: #e8ebf1; margin: 0; padding: 24px; }
    .container { max-width: 900px; margin: 0 auto; }
    h1 { margin-bottom: 20px; }
    form { display: flex; gap: 10px; margin-bottom: 20px; }
    input[type=text] {
      flex: 1; padding: 10px 12px; border-radius: 8px;
      border: 1px solid #333; background: #11182e; color: #e8ebf1;
    }
    button {
      padding: 10px 16px; border: none; border-radius: 8px;
      background: #2b7cff; color: white; font-weight: bold; cursor: pointer;
    }
    .card {
      background: #0e1530; border: 1px solid #1c2a4a; border-radius: 10px;
      padding: 16px; box-shadow: 0 0 20px rgba(0,0,0,0.3); margin-bottom: 20px;
    }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    td { padding: 8px 4px; border-bottom: 1px solid #27365d; }
    .error { color: #ff8a8a; margin-top: 10px; }
    #tvchart { height: 520px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Stock Info Viewer</h1>
    <form method="get">
      <input type="text" name="ticker" placeholder="Enter ticker symbol (e.g. AAPL)" value="{{ ticker|e }}" required>
      <button type="submit">Search</button>
    </form>

    {% if error %}
      <div class="error">{{ error }}</div>
    {% elif data %}
      <div class="card">
        <h2>{{ data.name }} ({{ data.symbol }})</h2>
        <table>
          <tr><td><strong>Current Price:</strong></td><td>${{ "%.2f"|format(data.c) }}</td></tr>
          <tr><td><strong>Open:</strong></td><td>${{ "%.2f"|format(data.o) }}</td></tr>
          <tr><td><strong>High:</strong></td><td>${{ "%.2f"|format(data.h) }}</td></tr>
          <tr><td><strong>Low:</strong></td><td>${{ "%.2f"|format(data.l) }}</td></tr>
          <tr><td><strong>Previous Close:</strong></td><td>${{ "%.2f"|format(data.pc) }}</td></tr>
        </table>
      </div>

      <!-- TradingView live chart (replaces old Chart.js) -->
      <div class="card">
        <h3 style="margin:0 0 10px 0;">Live Chart</h3>
        <div id="tvchart"></div>
      </div>

      <!-- TradingView widget loader -->
      <script src="https://s3.tradingview.com/tv.js"></script>
      <script>
        (function () {
          const symbol = "{{ data.symbol }}";
          if (!symbol) return;

          // If you know the exchange, you can prefix (e.g., "NASDAQ:AAPL").
          new TradingView.widget({
            container_id: "tvchart",
            symbol: symbol,
            interval: "1",
            timezone: "Etc/UTC",
            theme: "dark",
            style: "1",
            locale: "en",
            autosize: true,
            withdateranges: true,
            allow_symbol_change: true,
            hide_side_toolbar: false,
            hide_top_toolbar: false,
            details: true,
            studies: []
          });
        })();
      </script>
    {% endif %}
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    ticker = request.args.get("ticker", "").strip().upper()
    data, error = None, None

    if ticker:
        try:
            profile = client.company_profile2(symbol=ticker)
            if not profile or "name" not in profile:
                error = f"'{ticker}' is not a valid ticker symbol."
            else:
                quote = client.quote(ticker)
                data = {
                    "name": profile.get("name", "N/A"),
                    "symbol": ticker,
                    "c": quote.get("c", 0.0),
                    "o": quote.get("o", 0.0),
                    "h": quote.get("h", 0.0),
                    "l": quote.get("l", 0.0),
                    "pc": quote.get("pc", 0.0),
                }
        except Exception as e:
            error = f"Error fetching data: {e}"

    return render_template_string(PAGE, ticker=ticker, data=data, error=error)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
