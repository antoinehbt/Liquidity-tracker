import requests
from prettytable import PrettyTable

def search_pairs(token1, token2, min_liquidity, filter_chain=None, filter_dex=None):
    base_url = "https://api.dexscreener.com/latest/dex/search"
    params = {'q': f"{token1} {token2}"}
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if 'pairs' in data:
            pairs = []
            for pair in data['pairs']:
                if ('priceUsd' in pair and 'liquidity' in pair and 'usd' in pair['liquidity'] and 
                    'priceNative' in pair and 
                    ((pair['baseToken']['symbol'] == token1 and pair['quoteToken']['symbol'] == token2) or 
                     (pair['baseToken']['symbol'] == token2 and pair['quoteToken']['symbol'] == token1))):
                    if (filter_chain and pair['chainId'] != filter_chain) or \
                       (filter_dex and pair.get('dexId', 'Non disponible') != filter_dex):
                        continue

                    price_usd = float(pair['priceUsd'])
                    price_native = float(pair['priceNative'])
                    liquidity_usd = float(pair['liquidity']['usd'])
                    if pair['baseToken']['symbol'] == token2 and pair['quoteToken']['symbol'] == token1 and price_native != 0:
                        price_usd = price_usd / price_native
                    if liquidity_usd >= min_liquidity:
                        pairs.append(
                            (
                                pair['pairAddress'],
                                pair['chainId'],
                                pair.get('dexId', 'Non disponible'),
                                price_usd,
                                liquidity_usd
                            )
                        )
            return pairs
        else:
            return None
    else:
        return None

token1 = input("Entrez le premier symbole de token (par exemple, 'AAVE') : ")
token2 = input("Entrez le second symbole de token (par exemple, 'UNI') : ")
min_liquidity = float(input("Entrez le seuil de liquidité minimum (en USD) : "))
filter_chain_input = input("Voulez-vous filtrer par chaîne? (oui/non) : ")
filter_chain = input("Entrez le nom de la chaîne (par exemple, 'ethereum') : ") if filter_chain_input.lower() == 'oui' else None
filter_dex_input = input("Voulez-vous filtrer par DEX? (oui/non) : ")
filter_dex = input("Entrez le nom du DEX (par exemple, 'uniswap') : ") if filter_dex_input.lower() == 'oui' else None

pairs_prices = search_pairs(token1, token2, min_liquidity, filter_chain, filter_dex)

if pairs_prices:
    table = PrettyTable()
    table.field_names = ["Adresse de la Paire", "Chaîne", "DEX", "Prix", "Liquidité"]
    for address, chain_id, dex_id, price, liquidity in pairs_prices:
        table.add_row([address, chain_id, dex_id, f"{price:.6f}", f"{liquidity:.2f}"])
    print(table)
else:
    print("Impossible de récupérer les informations ou aucune paire correspondante trouvée.")
