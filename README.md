# xtask Discord Bot


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

### Additional Information:
- This Discord bot requires proper setup of API keys in the `.env` file before running.
- Ensure appropriate permissions and access controls for the API keys used by this bot.
