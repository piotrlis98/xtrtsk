import os
from datetime import datetime, timedelta
import logging

import discord
from discord.ext import tasks, commands
from discord.ui import Select, View

import pandas as pd
from ta.momentum import RSIIndicator
from pybit.unified_trading import HTTP

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set matplotlib style
plt.style.use('ggplot')

# Load environment variables
load_dotenv()


class XtrBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_channel = None
        self.interval = '1M'
        self.alert_mode = 'alert'
        self.last_timestamp = None
        self.session = HTTP(
            testnet=False,
            api_key=os.getenv('BYBIT_API_KEY'),
            api_secret=os.getenv('BYBIT_API_SECRET'),
        )

    async def fetch_rsi_data(self):
        """Fetch RSI data from Bybit API."""
        try:
            change = False
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = int(
                (datetime.now() - timedelta(days={'1d': 1, '1w': 7, '1M': 30}[self.interval])).timestamp() * 1000)

            response = self.session.get_kline(
                category="linear",
                symbol="SOLUSDT",
                interval=60,  # 24 klines per day
                start=start_time,
                end=end_time,
                limit=744  # value from [0-1000]. 744 klines = data from 31 days with timeframe (interval) of 1H
            )

            # Check if the response contains the expected data
            if 'result' not in response or 'list' not in response['result']:
                raise ValueError("Unexpected response format from Bybit API")

            klines = response['result']['list']

            if not klines:
                raise ValueError("No data received from Bybit API")

            if self.last_timestamp is None:
                self.last_timestamp = klines[0][0]
            elif self.last_timestamp < klines[0][0]:
                self.last_timestamp = klines[0][0]
                change = True
                
            closing_prices = list(map(float, [kline[4] for kline in klines]))

            data = pd.DataFrame(closing_prices, columns=['close'])
            data['RSI'] = RSIIndicator(data['close'], window=14).rsi()

            timestamps = [int(kline[0]) for kline in klines]
            data['Time'] = pd.to_datetime(timestamps[::-1], unit='ms')

            return data, change

        except Exception as e:
            logger.error(f"Failed to fetch RSI data: {e}")
            return None

    async def plot_rsi(self, data):
        """Plot RSI data and save to a file."""
        plt.figure(figsize=(12, 6))
        plt.plot(data[0]['Time'], data[0]['RSI'], color='blue', label='RSI (14)')

        ax = plt.gca()

        plt.xlabel('Date')
        locator, date_format = {
            '1d': (mdates.HourLocator(), '%Y-%m-%d %H:%M'),
            '1w': (mdates.DayLocator(), '%Y-%m-%d'),
            '1M': (mdates.WeekdayLocator(), '%Y-%m-%d')
        }[self.interval]

        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
        plt.title(
            f'Calculation of Relative Strength Index (RSI) for SOL/Tether (SOLUSDT) for period of {self.interval}')
        plt.ylabel('RSI Value')
        plt.axhline(y=70, color='r', linestyle='--', label='Overbought (>70)')
        plt.axhline(y=30, color='g', linestyle='--', label='Oversold (<30)')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        plt.savefig('rsi_plot.png')
        plt.close()

    async def send_rsi_alert(self, interaction: discord.Interaction = None, channel=None, current_rsi=None,
                             checkMode=False):
        """Send RSI alert to the specified channel."""
        await self.plot_rsi(await self.fetch_rsi_data())

        if self.alert_mode == 'on' or (
                self.alert_mode == 'alert' and (current_rsi > 70 or current_rsi < 30)) or checkMode:
            if current_rsi > 70:
                title = "RSI Alert - SELL NOW ⚠️"
                color = discord.Color.red()
            elif current_rsi < 30:
                title = "RSI Alert - BUY NOW 📈"
                color = discord.Color.green()
            else:
                title = "RSI Alert"
                color = discord.Color.blue()

            embed = discord.Embed(title=title, description=f"Current RSI: **{current_rsi:.2f}**", color=color)
            file = discord.File("rsi_plot.png", filename="rsi_plot.png")
            embed.set_image(url="attachment://rsi_plot.png")

            if interaction:
                await interaction.followup.send(embed=embed, file=file)  # Send the response using followup.send()
            else:
                await channel.send(embed=embed, file=file)  # Send the response directly to the channel


intents = discord.Intents.all()
intents.messages = True
bot = XtrBot(command_prefix='!', intents=intents)


@bot.tree.command(name='start', description="Start sending updates to this channel.")
async def start(interaction: discord.Interaction):
    bot.selected_channel = interaction.channel
    embed = discord.Embed(description=f"Selected this channel for updates: {interaction.channel.name}",
                          color=discord.Color.green())
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='stop', description="Stop notifications on this channel.")
async def stop(interaction: discord.Interaction):
    bot.selected_channel = None
    embed = discord.Embed(description="Notifications have been stopped for this channel.", color=discord.Color.red())
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='check', description="Check the current RSI.")
async def check(interaction: discord.Interaction):
    await interaction.response.defer()
    data = await bot.fetch_rsi_data()
    current_rsi = data[0]['RSI'].iloc[-1]
    await bot.send_rsi_alert(interaction, interaction.channel, current_rsi, True)


async def generic_callback(interaction, attribute_name, description):
    setattr(bot, attribute_name, interaction.data['values'][0])
    embed = discord.Embed(description=f"{description}: {getattr(bot, attribute_name)}", color=discord.Color.green())
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='mode', description="Set the mode for RSI alerts.")
async def set_mode(interaction: discord.Interaction):
    select = Select(placeholder='Select the mode', options=[
        discord.SelectOption(label='Off', value='off', emoji='🚫', description='Turn off any alerts and reports'),
        discord.SelectOption(label='On', value='on', emoji='✅', description='Turn on hourly reports'),
        discord.SelectOption(label='Alert', value='alert', emoji='🚨', description='Set to alert mode')
    ])

    select.callback = lambda interaction: generic_callback(interaction, 'alert_mode', 'Alert mode set to')
    view = View()
    view.add_item(select)

    await interaction.response.send_message("Choose a mode in the menu below.", view=view)


@bot.tree.command(name='interval', description="Set the interval for RSI calculation.", )
async def set_interval(interaction: discord.Interaction):
    select = Select(placeholder='Select the data range you wish to calculate RSI from', options=[
        discord.SelectOption(label='One day', value='1d', emoji='🕙', description='Last 24 hours'),
        discord.SelectOption(label='One week', value='1w', emoji='📅', description='Last week'),
        discord.SelectOption(label='One month', value='1M', emoji='⌛', description='Last month')
    ])

    select.callback = lambda interaction: generic_callback(interaction, 'interval', 'You chose')
    view = View()
    view.add_item(select)

    await interaction.response.send_message("Choose a date range in the menu below.", view=view)


@bot.tree.command(name='summary', description='Display the current configuration summary.')
async def summary(interaction: discord.Interaction):
    mode_description = {
        'off': 'No alerts or reports will be sent.',
        'on': 'Hourly reports will be sent.',
        'alert': 'Reports will be sent based on RSI thresholds.'
    }.get(bot.alert_mode, 'Unknown')

    interval_description = {
        '1d': 'Last 24 hours.',
        '1w': 'Last week.',
        '1M': 'Last month.'
    }.get(bot.interval, 'Unknown')

    channel_description = bot.selected_channel.name if bot.selected_channel else 'None selected'

    embed = discord.Embed(title="Current Configuration Summary", color=discord.Color.blue())
    embed.add_field(name="Alert Mode", value=f"{bot.alert_mode.capitalize()} ({mode_description})", inline=False)
    embed.add_field(name="Date range", value=f"{interval_description}", inline=False)
    embed.add_field(name="Channel for Alerts", value=f"{channel_description}", inline=False)

    await interaction.response.send_message(embed=embed)


@tasks.loop(seconds=5)
async def alert_check():
    """Check and send RSI alerts if conditions are met."""

    if bot.selected_channel and bot.alert_mode != 'off':
        data = await bot.fetch_rsi_data()

        if data is None:
            await bot.selected_channel.send("Failed to fetch RSI data. Please try again later.")
            return

        if data[1]:
            current_rsi = data[0]['RSI'].iloc[-1]
            await bot.send_rsi_alert(channel=bot.selected_channel, current_rsi=current_rsi)
        else:
            return


@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
    alert_check.start()


bot.run(os.getenv('DISCORD_TOKEN'))
