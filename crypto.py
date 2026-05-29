import requests
import sys

COIN_MAP = {
    "btc": "bitcoin", "eth": "ethereum", "bnb": "binancecoin",
    "sol": "solana", "xrp": "ripple", "usdc": "usd-coin",
    "ada": "cardano", "avax": "avalanche-2", "doge": "dogecoin",
    "trx": "tron", "link": "chainlink", "dot": "polkadot",
    "matic": "matic-network", "shib": "shiba-inu", "ltc": "litecoin",
    "uni": "uniswap", "atom": "cosmos", "xlm": "stellar",
    "okb": "okb", "etc": "ethereum-classic", "hbar": "hedera-hashgraph",
    "fil": "filecoin", "apt": "aptos", "arb": "arbitrum",
    "op": "optimism", "sui": "sui", "near": "near",
    "inj": "injective-protocol", "hype": "hyperliquid",
    "aave": "aave", "sand": "the-sandbox", "mana": "decentraland",
    "axs": "axie-infinity", "crv": "curve-dao-token", "mkr": "maker",
    "snx": "havven", "comp": "compound-governance-token", "ldo": "lido-dao",
    "imx": "immutable-x", "algo": "algorand", "icp": "internet-computer",
    "egld": "elrond-erd-2", "theta": "theta-token", "ftm": "fantom",
    "vet": "vechain", "mina": "mina-protocol", "flow": "flow",
    "xtz": "tezos", "eos": "eos", "grt": "the-graph",
    "1inch": "1inch", "enj": "enjincoin", "chz": "chiliz",
    "bat": "basic-attention-token", "zec": "zcash", "dash": "dash",
    "neo": "neo", "waves": "waves", "hot": "holotoken",
    "zil": "zilliqa", "rvn": "ravencoin", "sc": "siacoin",
    "dcr": "decred", "xem": "nem", "ont": "ontology",
    "nano": "nano", "icx": "icon", "zen": "zencash",
    "lrc": "loopring", "audio": "audius", "celr": "celer-network",
    "skl": "skale", "storj": "storj", "ankr": "ankr",
    "cvc": "civic", "oxt": "orchid-protocol", "req": "request-network",
    "trb": "tellor", "band": "band-protocol", "uma": "uma",
    "bal": "balancer", "yfi": "yearn-finance", "sushi": "sushi",
    "rune": "thorchain", "kava": "kava", "xvs": "venus",
    "alpha": "alpha-finance", "dydx": "dydx", "perp": "perpetual-protocol",
    "tlm": "alien-worlds", "alice": "my-neighbor-alice", "chr": "chromia",
    "reef": "reef-finance", "dent": "dent", "win": "wink",
    "sun": "sun-token", "sys": "syscoin", "stx": "blockstack",
    "hnt": "helium", "iotx": "iotex", "xdc": "xdce-crowd-sale"
}

def get_coin(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    response = requests.get(url)
    
    if response.status_code == 404:
        print(f"Coin '{coin_id}' not found")
        return
    
    data = response.json()
    
    name = data["name"]
    symbol = data["symbol"].upper()
    price = data["market_data"]["current_price"]["usd"]
    change_24h = data["market_data"]["price_change_percentage_24h"]
    market_cap = data["market_data"]["market_cap"]["usd"]
    rank = data["market_cap_rank"]
    
    print(f"\n{name} ({symbol})")
    print(f"Rank: #{rank}")
    print(f"Price: ${price:,.2f}")
    print(f"24h Change: {change_24h:.2f}%")
    print(f"Market Cap: ${market_cap:,.0f}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = sys.argv[1].lower()
        coin_id = COIN_MAP.get(query, query)
        get_coin(coin_id)
    else:
        print("Usage: crypto <ticker or coin-id>")
        print("Examples: btc, eth, sol, hype, bitcoin")
