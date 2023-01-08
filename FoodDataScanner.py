
#%%
import telegram
import telegram.ext
from io import BytesIO
from pyzbar import pyzbar
import cv2
from telegram.ext import MessageHandler, Filters
from io import BytesIO
import numpy as np
import requests
from .config import settings


# Dispatcher
updater = telegram.ext.Updater(settings.API_KEY_TELEGRAM_FOOD)
dispatcher = updater.dispatcher

# decode barcode image
def decode(image):
    img =cv2.imdecode(np.frombuffer(image.read(), np.uint8), 1)
    try:
        decoded_objects = pyzbar.decode(img)
        for obj in decoded_objects:
            barcode=str(obj.data)[1:].strip("'")
        return(barcode)
    except:
        return(None)

# use openfoodfacts API
def get_categories_names(barcode):
    requestURL="https://world.openfoodfacts.org/api/v2/product/"+barcode+"&json=true"
    response=requests.get(requestURL)
    data = response.json()
    try:
        ingr=data['product']['ingredients_text']
        allerg=data['product']['allergens']
        nutriscore=data['product']['nutriscore_grade']
        print(ingr,allerg,nutriscore)
        return(ingr,allerg,nutriscore)
    except:
        return('Food not found')

# use Openfoodfacts API
def photo(update, context):
    file = context.bot.get_file(update.message.photo[-1].file_id)
    print('ok')
    f =  BytesIO(file.download_as_bytearray())
    result = decode(f)
    if result==None:
        response = 'No barcode found, please send a better picture'
    else:
        try:
            ingr,allerg,nutriscore=get_categories_names(result)
            response = f'The barcode is {result}, nutriscore: {nutriscore}. \nIngredients are {ingr}. \nAllergens: {allerg}.'
        except:
            response = 'Food not found'
    context.bot.send_message(chat_id=update.message.chat_id, text=response)

# photo handler
photo_handler = MessageHandler(Filters.photo, photo)
dispatcher.add_handler(photo_handler)

# start polling for updates from Telegram
updater.start_polling()

# block until a signal (like one sent by CTRL+C) is sent
updater.idle()

