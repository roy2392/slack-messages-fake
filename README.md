# Slack Fake Messages Generator

A Python script to send fake conversation messages to a Slack channel for testing, demo, or development purposes.

## Features

- 🤖 Sends messages with custom usernames and emojis
- ⏱️ Configurable delays between messages for realistic conversation flow
- 🎭 Easily customizable conversation templates
- ✅ Connection testing before sending messages
- 🔒 Secure credential management with environment variables

## Prerequisites

- Python 3.7 or higher
- A Slack workspace where you have permission to create apps
- A Slack App with a Bot Token

## Setup

### 1. Create a Slack App

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click **"Create New App"** → **"From scratch"**
3. Give your app a name (e.g., "Fake Messages Bot")
4. Select your workspace

### 2. Configure Bot Permissions

1. In your app settings, go to **"OAuth & Permissions"**
2. Scroll down to **"Scopes"** → **"Bot Token Scopes"**
3. Add the following scopes:
   - `chat:write` - Send messages
   - `chat:write.customize` - Send messages with custom username and avatar

### 3. Install App to Workspace

1. Scroll to the top of the **"OAuth & Permissions"** page
2. Click **"Install to Workspace"**
3. Authorize the app
4. Copy the **"Bot User OAuth Token"** (starts with `xoxb-`)

### 4. Invite Bot to Channel

1. Open the Slack channel where you want to send messages
2. Type `/invite @YourBotName` (replace with your bot's name)
3. Or right-click the channel → Integrations → Add apps

### 5. Install Dependencies

```bash
# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 6. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your credentials
```

Edit `.env` file:
```env
SLACK_BOT_TOKEN=xoxb-your-actual-bot-token-here
SLACK_CHANNEL=#your-channel-name
```

You can also use the channel ID instead of the name (e.g., `C01234567`).

## Usage

### Run the Script

```bash
python send_fake_messages.py
```

The script will:
1. Test the connection to Slack
2. Show you the target channel
3. Ask for confirmation
4. Send the fake conversation with realistic delays

### Customize the Conversation

Edit the `FAKE_CONVERSATIONS` list in `send_fake_messages.py`:

```python
FAKE_CONVERSATIONS = [
    {
        "username": "Alice",
        "icon_emoji": ":woman:",
        "messages": [
            "Your custom message here",
            "Another message from Alice",
        ]
    },
    {
        "username": "Bob",
        "icon_emoji": ":man:",
        "messages": [
            "Bob's response",
        ]
    },
    # Add more participants...
]
```

### Available Emoji Icons

Use any Slack emoji with the format `:emoji_name:`. Common ones:
- `:woman:`, `:man:`, `:person:`
- `:technologist:`, `:woman_technologist:`, `:man_technologist:`
- `:scientist:`, `:teacher:`, `:student:`
- `:robot_face:`, `:alien:`, `:ghost:`

### Adjust Message Timing

Change the `delay_range` parameter in the `send_fake_conversation()` call:

```python
send_fake_conversation(
    channel=SLACK_CHANNEL,
    conversations=FAKE_CONVERSATIONS,
    delay_range=(0.5, 2)  # Faster: 0.5-2 seconds between messages
)
```

## Troubleshooting

### "Error: not_in_channel"
- Make sure you've invited the bot to the channel using `/invite @YourBotName`

### "Error: invalid_auth"
- Check that your `SLACK_BOT_TOKEN` in `.env` is correct
- Ensure the token starts with `xoxb-`

### "Error: missing_scope"
- Go to your app's **OAuth & Permissions** page
- Add the required scopes: `chat:write` and `chat:write.customize`
- Reinstall the app to your workspace

### Messages appear as the bot instead of custom usernames
- Verify you've added the `chat:write.customize` scope
- Check that `username` and `icon_emoji` are set in your conversation data

## Security Notes

- ⚠️ Never commit your `.env` file or expose your bot token
- The `.gitignore` file is configured to prevent accidental commits
- Rotate your bot token if it's ever exposed
- Only grant the minimum required permissions to your bot

## License

MIT License - feel free to use and modify as needed.

## Contributing

Feel free to submit issues or pull requests to improve this script!
