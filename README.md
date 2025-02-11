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
   - **Instance Type**: Free (for testing) or Basic (for production)

### 4. Environment Variables

The following environment variable must be set in your Render dashboard:

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from BotFather (Required)
- `PORT`: Automatically set by Render, no need to configure

To set environment variables in Render:
1. Go to your service dashboard
2. Click on "Environment"
3. Add the variable `TELEGRAM_BOT_TOKEN` with your bot token
4. Click "Save Changes"

### 5. Important Notes

1. The free tier of Render has some limitations:
   - Services sleep after 15 minutes of inactivity
   - Limited compute resources
   - May have slower cold starts

2. For production use:
   - Use at least the Basic plan ($7/month)
   - This ensures your bot stays active 24/7
   - Provides better performance and reliability

3. The web server runs on port 10000 by default
   - Render will automatically assign a port via the `PORT` environment variable
   - The bot handles this automatically

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
