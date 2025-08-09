# boting/keyboard.py
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    """
    Returns the main reply keyboard markup for the Telegram bot
    with predefined buttons for user interaction.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(        
        KeyboardButton("💰 Account Balance"),
        KeyboardButton("🚀 Start Trading")            
    )
    keyboard.add(   
        KeyboardButton("💰 Real-time Balance"),
        KeyboardButton("ℹ️ Trading Status")                 
    )   
    keyboard.add(   
        KeyboardButton("🗓️ Daily Report"),        
        KeyboardButton("🛑 Stop Trading")                  
    )    
    keyboard.add(   
        KeyboardButton("⚙️ Edit Variables"),
        KeyboardButton("⚡️ Trading Variables")        
    )  
    keyboard.add(         
        KeyboardButton("🛑 Stop Bot")                  
    )     
    return keyboard
