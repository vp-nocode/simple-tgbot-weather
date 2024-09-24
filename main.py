import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message
from config import TOKEN, TOKEN_WEATHERSTACK, TOKEN_OWM
import requests

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    await dp.start_polling(bot)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Hi, I'm a weather forecast bot! \n To get a weather forecast, enter the command /report {city}, for example, /report Rome")

@dp.message(Command('help'))
async def help(message: Message):
    await message.answer("To get a weather forecast, enter the command /report {city}, for example, /report Rome")

@dp.message(Command('report'))
async def report(message: Message, command: CommandObject):
    params = command.args
    if params:
        param_list = params.split()
        city = param_list[0]
        # weather = get_weather_owm(city)
        weather = get_weather_weatherstack(city)
        if weather:
            if weather['status']:
                forecast_text = weather['forecast']
            else:
                forecast_text = f"Failed to retrieve weather data for city {city}"
        else:
            forecast_text = "Failed to retrieve weather data"

        await message.answer(forecast_text)
    else:
        await message.answer("no city specified for command /report")

# unknown command and text handler
@dp.message(F.text)
async def unknown_command(message: Message):
    await message.answer("Sorry, I didn't understand that command or message. Please try again.")

def get_weather_owm(city):
   api_key = TOKEN_OWM
   url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
   response = requests.get(url)
   if response.status_code == 200:
       return {'status': True, 'forecast': response.json()}
   else:
       print("Error while receiving data:", response.status_code)
       return {'status': False, 'forecast': None}

def get_weather_weatherstack(city):
   api_key =  TOKEN_WEATHERSTACK
   url = f"https://api.weatherstack.com/current?access_key={api_key}"

   querystring = {"query": f"{city}"}
   response = requests.get(url, params=querystring)

   if response.status_code == 200:
       # print(response.json())
       if 'request' in response.json():
           cur_location = response.json()['location']
           cur_report = response.json()['current']
           forecast_text = f'city: {cur_location['name']}, country: {cur_location['country']}, localtime: {cur_location['localtime']}\n'
           forecast_text += f'T: {cur_report['temperature']}°C, wind_speed: {cur_report['wind_speed']} m/s, pressure: {cur_report['pressure']} kPa\n'
           forecast_text += f'description: {cur_report['weather_descriptions']}'
           return {'status': True, 'forecast': forecast_text}
       else:
           return {'status': False, 'forecast': None}
   else:
       # print("Error while receiving data:", response.status_code)
       return {'status': False, 'forecast': None}


if __name__ == "__main__":
    asyncio.run(main())
