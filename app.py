from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/coins")
def get_coins():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": "false"
    }
    try:
        response = requests.get(url, params=params,timeout=5)
        response.raise_for_status()
        data = response.json()
        #stable coinleri filtrele
        filtered = [coin for coin in data if coin['symbol'].lower() not in ["usdt","usdc","usd","dai","dusd","steth","wsteth"]]
        # sadece ilk 10 taneyi döndür
        return jsonify(filtered[:10])
    except Exception as e:
        return jsonify({"error": "Veri Çekilemedi","details": str(e)}),500
if __name__ == "__main__":
    app.run(debug=True)
