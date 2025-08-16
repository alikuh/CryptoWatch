from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__ , template_folder='frontend')


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/coins")
def get_coins():
    """Top 10 gerçek kripto parayı getir (stablecoin'ler hariç)"""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,  # Daha fazla çek ki filtrele
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Filtrelenecek stablecoin'ler ve wrapped token'lar
        excluded_symbols = {
            'usdt', 'usdc', 'busd', 'dai', 'frax', 'tusd', 'usdp', 'gusd',
            'steth', 'weth', 'wbtc', 'cbeth', 'reth', 'sfrxeth'
        }

        excluded_ids = {
            'tether', 'usd-coin', 'binance-usd', 'dai', 'terrausd', 'frax',
            'trueusd', 'paxos-standard', 'gemini-dollar', 'lido-staked-ether',
            'wrapped-bitcoin', 'steth', 'weth', 'rocket-pool-eth', 'cbeth'
        }

        # Filtreleme
        filtered_coins = []
        for coin in data:
            coin_id = coin.get('id', '').lower()
            symbol = coin.get('symbol', '').lower()
            name = coin.get('name', '').lower()

            # Filtreleme koşulları
            if (coin_id not in excluded_ids and
                    symbol not in excluded_symbols and
                    'usd' not in symbol and
                    'wrapped' not in name and
                    'staked' not in name and
                    not (symbol.startswith('w') and len(symbol) <= 4) or symbol in ['woo', 'waves', 'wax']):

                filtered_coins.append(coin)

                if len(filtered_coins) >= 10:
                    break

        return jsonify(filtered_coins)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "API bağlantı hatası", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Beklenmeyen hata", "details": str(e)}), 500


@app.route("/api/search_coin/<query>")
def search_coin(query):
    """Kripto para ara"""
    try:
        # Önce arama yap
        search_url = "https://api.coingecko.com/api/v3/search"
        search_params = {'query': query}

        search_response = requests.get(search_url, params=search_params, timeout=10)
        search_response.raise_for_status()
        search_data = search_response.json()

        if not search_data.get('coins'):
            return jsonify({"success": False, "message": f"'{query}' için sonuç bulunamadı."})

        # İlk sonucu al
        coin_id = search_data['coins'][0]['id']

        # Coin detaylarını al
        details_url = "https://api.coingecko.com/api/v3/coins/markets"
        details_params = {
            "vs_currency": "usd",
            "ids": coin_id,
            "price_change_percentage": "24h,7d"
        }

        details_response = requests.get(details_url, params=details_params, timeout=10)
        details_response.raise_for_status()
        coin_data = details_response.json()

        if coin_data:
            return jsonify({"success": True, "coin": coin_data[0]})
        else:
            return jsonify({"success": False, "message": "Coin detayları alınamadı."})

    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": "API bağlantı hatası", "details": str(e)})
    except Exception as e:
        return jsonify({"success": False, "message": "Beklenmeyen hata", "details": str(e)})


@app.route("/api/chart_data")
def get_chart_data():
    """Grafik için top 10 coin verisi"""
    try:
        response = requests.get("http://localhost:5000/api/coins", timeout=10)
        data = response.json()

        chart_data = {
            "labels": [coin['symbol'].upper() for coin in data[:10]],
            "prices": [coin['current_price'] for coin in data[:10]],
            "changes": [coin.get('price_change_percentage_24h', 0) for coin in data[:10]]
        }

        return jsonify(chart_data)

    except Exception as e:
        return jsonify({"error": "Grafik verisi alınamadı", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)