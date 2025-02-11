# Chess Recognition Bot

A Telegram bot that recognizes chess positions from images and provides FEN notation and Lichess analysis links.

## Features

- 🎯 Recognizes chess positions from photos
- 📝 Provides FEN (Forsyth–Edwards Notation) for the position
- 🔗 Generates Lichess analysis links
- 📊 Shows prediction confidence levels
- 🚦 Includes confidence indicators (High 🟢, Medium 🟡, Low 🔴)
- ⚠️ Provides suggestions for better photo quality when needed

## Prerequisites

- Python 3.9+
- TensorFlow 2.15.0
- python-telegram-bot 20.7
- Other dependencies listed in `requirements.txt`

## Deployment on Render

### 1. Fork/Clone the Repository

First, fork this repository to your GitHub account or clone it and push to your own repository.

### 2. Prepare the Model Files

The neural network model files should be placed in the `nn` directory:
- `saved_model.pb`
- `variables/variables.data-00000-of-00001`
- `variables/variables.index`

### 3. Set Up Render

1. Create a new account on [Render](https://render.com) if you don't have one
2. Go to the Dashboard and click "New +"
3. Select "Web Service"
4. Connect your GitHub repository
5. Configure the service:

   - **Name**: Choose a name for your service (e.g., `chess-recognition-bot`)
   - **Environment**: `Python 3`
   - **Region**: Choose the closest to your users
   - **Branch**: `main` or `master`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python telegram_bot.py`
   - **Instance Type**: Basic (required for 24/7 operation)

### 4. Environment Variables

The following environment variable must be set in your Render dashboard:

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from BotFather (Required)
- `PORT`: Automatically set by Render, no need to configure

To set environment variables in Render:
1. Go to your service dashboard
2. Click on "Environment"
3. Add the variable `TELEGRAM_BOT_TOKEN` with your bot token
4. Click "Save Changes"

### 5. Keeping the Bot Running 24/7

To ensure your bot runs continuously without sleeping:

1. **Upgrade to Basic Plan**:
   - Go to your service dashboard
   - Click on "Change Plan"
   - Select "Basic" ($7/month)
   - Confirm the upgrade

2. **Configure Auto-Restart**:
   - In your service settings
   - Enable "Auto-Deploy"
   - Set "Health Check Path" to `/`
   - Set "Health Check Period" to 1 minute

3. **Set Resource Limits**:
   - Memory: 512 MB minimum
   - CPU: 0.1 CPU minimum
   - These settings are available in the Basic plan

4. **Monitor Health**:
   - Set up Render monitoring alerts
   - Enable email notifications for service status
   - Check service logs regularly

5. **Prevent Inactivity**:
   - The web server we implemented keeps the service active
   - Render's health checks will ping the server
   - This prevents the service from sleeping

6. **Backup Plan**:
   - Set up a monitoring service (like UptimeRobot)
   - Configure it to ping your service URL every 5 minutes
   - This provides additional uptime assurance

### 6. Monitoring

1. Check the deployment status in Render dashboard
2. Visit your service URL to see if the bot is running
3. The web interface will show:
   - Bot status
   - Last check time
   - Instructions to contact the bot

### 7. Testing

1. Find your bot on Telegram: @ChessRecognitionBot
2. Start a conversation with `/start`
3. Send a chess board photo
4. You should receive:
   - FEN notation
   - Confidence level
   - Lichess analysis link

## Troubleshooting

1. If the bot doesn't respond:
   - Check Render logs for errors
   - Ensure the model files are properly placed in the `nn` directory
   - Verify the bot token is correct

2. If you get low confidence predictions:
   - Ensure the chess board is clearly visible
   - The entire board should be in the frame
   - Good lighting conditions are important
   - Pieces should be clearly distinguishable

3. If the service keeps restarting:
   - Check the logs for any errors
   - Ensure you're on an appropriate plan for your usage
   - Monitor memory usage in Render dashboard

## Support

If you encounter any issues or need help, please:
1. Check the existing issues in the repository
2. Create a new issue with detailed information about your problem
3. Include relevant logs and screenshots

## License

This project is licensed under the MIT License - see the LICENSE file for details.
