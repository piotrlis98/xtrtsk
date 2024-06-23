# xtrtsk Discord Bot

Welcome to a Discord bot designed for monitoring and alerting Relative Strength Index (RSI) values for SOLUSDT.

![image](https://github.com/piotrlis98/xtrtsk/assets/31008706/1bbf7d60-422d-4b6e-8a2f-9565b795c726)


### Running the bot with Docker:

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

- `/check`: Check the current RSI. ![Check](https://i.imgur.com/TPEzy9P.png)
- `/start`: Start sending alerts to this channel.
- `/summary`: Display the current configuration summary. ![Summary](https://i.imgur.com/SiOfZkk.png)
- `/stop`: Stop notifications on this channel.
- `/interval`: Set the interval (in days) over which the RSI will be calculated (default: last month). ![Set Interval](https://i.imgur.com/3ouCtpt.png)
- `/mode`: Set the mode for RSI alerts (default: alert). ![Set Mode](https://i.imgur.com/ox03yDF.png)

___

### Invite the bot to your server
[CLICK](https://discord.com/oauth2/authorize?client_id=1254165520194867372&permissions=2112&integration_type=0&scope=bot)
