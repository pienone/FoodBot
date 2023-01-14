import telegram
import telegram.ext
from io import BytesIO
from pyzbar import pyzbar
import cv2
from telegram.ext import MessageHandler, Filters
from io import BytesIO
import numpy as np
import requests
from config import settings


# Dispatcher
updater = telegram.ext.Updater(settings.API_KEY_TELEGRAM_FOOD)
dispatcher = updater.dispatcher

# Decode barcode image
def decode(image):
    img =cv2.imdecode(np.frombuffer(image.read(), np.uint8), 1)
    try:
        decoded_objects = pyzbar.decode(img)
        for obj in decoded_objects:
            barcode=str(obj.data)[1:].strip("'")
        return(barcode)
    except:
        return(None)

# Print message for telegram chat
def make_perc_table(dictlist):
    co2_cat=list(np.array(list(dictlist.keys()))[np.array(['co2' in x for x in dictlist.keys()])])
    co2_cat.remove('co2_total')
    mess=f"Total Co2 emissions: {dictlist['co2_total']*100:.2f} gCO2/100g \n"
    for cat in co2_cat:
            mess=mess+f"{cat.split('_')[1][0].upper() + cat.split('_')[1][1:]}: {dictlist[cat]/dictlist['co2_total']*100:.2f}% \n"
    return(mess)

# Retrieve Agribalyse data from openfoodfacts API
def get_CO2(barcode):
    requestURL="https://world.openfoodfacts.org/api/v2/product/"+barcode+"&json=true"
    response=requests.get(requestURL)
    data = response.json()
    try:
        #ingr=data['product']['ingredients_text']
        #allerg=data['product']['allergens']
        #nutriscore=data['product']['nutriscore_grade']
        agrib=data['product']['ecoscore_data']['agribalyse']
        return(agrib)
    except:
        return('Food does not have emission data')

# Main photo to message
def photo(update, context):
    file = context.bot.get_file(update.message.photo[-1].file_id)
    f =  BytesIO(file.download_as_bytearray())
    result = decode(f)
    if result==None:
        response = 'No barcode found, please send a better picture'
    else:
        try:
            co2data=get_CO2(result)
            response = make_perc_table(co2data)
            #response = f'The barcode is {result}, nutriscore: {nutriscore}. \nIngredients are {ingr}. \nAllergens: {allerg}.'
        except:
            response = 'Food does not have emission data'
    context.bot.send_message(chat_id=update.message.chat_id, text=response)

# hoto message handler
photo_handler = MessageHandler(Filters.photo, photo)
dispatcher.add_handler(photo_handler)

updater.start_polling()

updater.idle()
