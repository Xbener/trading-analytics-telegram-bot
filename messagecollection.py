from telethon.sync import TelegramClient
from datetime import datetime, timedelta
from pymongo import MongoClient
import requests
import json
import telethon.errors.rpcerrorlist
import time
TELEGRAM_API_ID = '20774786'
TELEGRAM_API_HASH = '9d57e018be785b18b245632f508302f2'
phone_number = '+17344305801'  # Fixed: Added quotes to make it a string
session_name = 'telegram_messages_session'
mongo_uri = "mongodb+srv://andyblake:crs19981106@messagescluster.ci599.mongodb.net/?retryWrites=true&w=majority&appName=MessagesCluster"
mongo_client = MongoClient(mongo_uri)
db = mongo_client["telegram_bot_db"]
token_collection = db["token_contracts"]
with open('channel.json', 'r') as file:
    channel_data = json.load(file)
    channel_list = channel_data['channels']

# channel_username = 'devsellinglounge'
i = 0 #message count
k = 0 #channel count
days = 10 #days to search
offset = datetime.now() - timedelta(days=days)#offset date

def extract_token_contracts(message):
    if message:
        # Split the message into parts and initialize a list for valid token contracts
        for part in message.split():
            if len(part) >= 40 and part.isalnum():
                return part
        return None

def get_token_contract_data(token_contracts):
    api_searchurl = f"https://api.dexscreener.com/latest/dex/search?q={token_contracts}"
    response = requests.get(api_searchurl, timeout=10)
    response.raise_for_status()
    data = response.json()
    pair_info = data.get('pairs', [])
    # Check if pair_info is empty
    if not pair_info:
        print("No pairs found for the provided token contracts.")
        return None  # Return None for each contract if no data is found
    data = pair_info[0]
    print("Successfully retrieved pair data")
    # Extract data with improved error handling
    def safe_get(obj, *keys, default="N/A"):
        try:
            current = obj
            for key in keys:
                current = current[key]
            return current if current is not None else default
        except (KeyError, TypeError):
            print(f"Failed to get value for keys {keys}")
            return default
    chain = safe_get(data, "chainId")
    dex_id = safe_get(data, "dexId")
    pairAddress = safe_get(data, "pairAddress")
    base_token_address = safe_get(data, "baseToken", "address")
    quote_token_address = safe_get(data, "quoteToken", "address")
    base_token_name = safe_get(data, "baseToken", "name", default="Unknown")
    quote_token_name = safe_get(data, "quoteToken", "name", default="Unknown")
    base_token_symbol = safe_get(data, "baseToken", "symbol")
    quote_token_symbol = safe_get(data, "quoteToken", "symbol")
    price_native = safe_get(data, "priceNative")
    price_usd = safe_get(data, "priceUsd")
    fdv = safe_get(data, "fdv")
    liquidity_usd = safe_get(data, "liquidity", "usd")
    liquidity_base = safe_get(data, "liquidity", "base")
    liquidity_quote = safe_get(data, "liquidity", "quote")
    volume_h24 = safe_get(data, "volume", "h24")
    volume_h6 = safe_get(data, "volume", "h6")
    volume_h1 = safe_get(data, "volume", "h1")
    volume_m5 = safe_get(data, "volume", "m5")
    price_change_h1 = safe_get(data, "priceChange", "h1")
    price_change_h24 = safe_get(data, "priceChange", "h24")
    price_change_h6 = safe_get(data, "priceChange", "h6")
    price_change_m5 = safe_get(data, "priceChange", "m5")   
    buys_number_h1 = safe_get(data, "txns", "h1", "buys")
    sells_number_h1 = safe_get(data, "txns", "h1", "sells")
    buys_number_h24 = safe_get(data, "txns", "h24", "buys")
    sells_number_h24 = safe_get(data, "txns", "h24", "sells")
    buys_number_h6 = safe_get(data, "txns", "h6", "buys")
    sells_number_h6 = safe_get(data, "txns", "h6", "sells")
    buys_number_m5 = safe_get(data, "txns", "m5", "buys")
    sells_number_m5 = safe_get(data, "txns", "m5", "sells")
    token_age = safe_get(data, "pairCreatedAt")   

    token_data = {
        "token_contracts": token_contracts,
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "chain": chain,
        "dex_id": dex_id,
        "pairAddress": pairAddress,
        "base_token_address": base_token_address,
        "quote_token_address": quote_token_address,
        "base_token_name": base_token_name,
        "quote_token_name": quote_token_name,
        "base_token_symbol": base_token_symbol,
        "quote_token_symbol": quote_token_symbol,
        "price_native": price_native,
        "price_usd": price_usd,
        "fdv": fdv,
        "liquidity": {
            "usd": liquidity_usd,
            "base": liquidity_base,
            "quote": liquidity_quote
        },
        "volume": {
            "h24": volume_h24,
            "h6": volume_h6,
            "h1": volume_h1,
            "m5": volume_m5
        },
        "price_change": {
            "h1": price_change_h1,
            "h24": price_change_h24,
            "h6": price_change_h6,
            "m5": price_change_m5
        },
        "txns": {
            "buys": {
                "h1": buys_number_h1,
                "h24": buys_number_h24,
                "h6": buys_number_h6,
                "m5": buys_number_m5
            },
            "sells": {
                "h1": sells_number_h1,
                "h24": sells_number_h24,
                "h6": sells_number_h6,
                "m5": sells_number_m5
            }
        },
        "token_age": token_age
    }
    return token_data

with TelegramClient(session_name, TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
    for channel_username in channel_list:
       
        k += 1
        print("🎁🎁🎁🎁", k,"/",len(channel_list), channel_username)
        try:
            for message in client.iter_messages(channel_username):
                if message.date.date() >= offset.date():  # Only output messages from the previous day
                    token_contracts = extract_token_contracts(message.text)
                    if token_contracts:
                        i += 1    
                        print("🎁", i, message.date,"🎈",token_contracts)
                        message_dict = {
                            "token_contracts": token_contracts,
                            "last_mention_date": message.date,
                        }
                        
                        token_contract_data = get_token_contract_data(token_contracts)
                        existing_entry = token_collection.find_one({"token_contracts": {"$in": [message_dict["token_contracts"]]}})
                        
                        if not existing_entry:
                            print("🧨")
                            token_collection.insert_one({
                                **message_dict, 
                                "num_times_mentioned": 1,
                                "last_mention_date": message.date,
                                "all_data":{
                                "token_contract_data(0)": token_contract_data,
                                "message_date(0)": message.date,
                                "num_times_mentioned(0)": 1
                                }
                                })
                        elif existing_entry["last_mention_date"].strftime("%Y-%m-%d %H:%M:%S") != message.date.strftime("%Y-%m-%d %H:%M:%S"):
                            print("🧨🧨")
                            print(existing_entry["last_mention_date"], message.date.strftime("%Y-%m-%d %H:%M:%S"))
                            print("⌚",datetime.now().hour)
                            num_times_mentioned = existing_entry["num_times_mentioned"] + 1
                            
                            order_token_contract_data = datetime.now().hour
                            token_collection.update_one(
                                {"_id": existing_entry["_id"]},
                                {"$set": {
                                    "num_times_mentioned": num_times_mentioned,  
                                    "last_mention_date": message.date,
                                  
                                }}
                            )
                            token_collection.update_one(
                                {"_id": existing_entry["_id"]},
                                {"$set": {
                                    "all_data": {
                                        **existing_entry["all_data"],  # Preserve previous data
                                        f"token_contract_data({order_token_contract_data})": token_contract_data,
                                        f"num_times_mentioned({order_token_contract_data})": num_times_mentioned,  
                                        f"message_date({order_token_contract_data})": message.date,
                                       
                                    }
                                }}
                            )
                            print("Successfully updated token data")
                    else:
                        None
                else:
                    break
        except telethon.errors.rpcerrorlist.FloodWaitError as e:
            print(f'Have to sleep', e.seconds, 'seconds')
            time.sleep(e.seconds)
        except telethon.errors.rpcerrorlist.ChannelPrivateError:
            with open('channel.json', 'r+') as file:
                channel_data = json.load(file)
                channel_list = channel_data['channels']
                if channel_username in channel_list:
                    channel_list.remove(channel_username)
                    file.seek(0)
                    json.dump(channel_data, file, indent=4)
                    file.truncate()
            print(f"Access denied to channel: {channel_username}. It may be private or you lack permissions.")
        except Exception as e:
            print(f"An error occurred: {e}")

print("🎁", offset)
print("🎁", datetime.now())

