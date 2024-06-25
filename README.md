# xtrtsk Discord Bot

Welcome to a Discord bot designed for monitoring and alerting Relative Strength Index (RSI) values for SOLUSDT.


![image](https://github.com/piotrlis98/xtrtsk/assets/31008706/3c4083a0-8668-4c85-bf01-97662634ac06)



### Running the bot with Docker:

> [!IMPORTANT]  
> Bot is already running on a Oracle VPS server.
> For testing, scroll down to the bottom of this instruction and invite the bot to your server.

0. **Clone or download this repository and navigate to the project directory**.

1. **Ensure Docker is running on your device.**

2. **Build the Docker image:**
   ```bash
   docker build -t xtask .
   ```

3. **Prepare the `.env` file:**
   - Make sure your project directory contains a `.env` file with your API keys.
   - Example `.env` file structure:
     ```plaintext
     DISCORD_TOKEN=your_discord_token_here
     BYBIT_API_KEY=your_bybit_api_key_here
     BYBIT_API_SECRET=your_bybit_api_secret_here
     ```

4. **Run the Docker container:**
   ```bash
   docker run --env-file .env xtask
   ```

### Additional information:
- This Discord bot requires proper setup of API keys in the `.env` file before running.
- Ensure appropriate permissions and access controls for the API keys used by this bot.
- For Discord API, the required permissions are **2048** (ability to write messages). 

___

### Available commands overview:

- `/check`: Check the current RSI. ![image](https://github.com/piotrlis98/xtrtsk/assets/31008706/c339b303-0714-4bcf-b064-c9193a9d68f7)
- `/start`: Start sending alerts to this channel.
- `/summary`: Display the current configuration summary. ![image](https://github.com/piotrlis98/xtrtsk/assets/31008706/2adb9d6d-418a-43e5-b772-24f1df62d2e4)
- `/stop`: Stop notifications on this channel.
- `/timerange`: Set the time range over which the RSI will be calculated (default: last month). ![image](https://github.com/piotrlis98/xtrtsk/assets/31008706/9ec457b6-a4fd-4ad9-94f2-3f7586d601ff)
- `/mode`: Set the mode for RSI alerts (default: alert). \
  ![image](https://github.com/piotrlis98/xtrtsk/assets/31008706/e66fcd9b-cbe3-4a88-855e-8dc8656a9b76)

___

### Invite the bot to your server
[CLICK](https://discord.com/oauth2/authorize?client_id=1254165520194867372&permissions=2048&integration_type=0&scope=bot)
