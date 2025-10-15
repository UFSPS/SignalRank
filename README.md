# SignalRank
Bot solution for Discord that utilizes Python and Generative AI integration to deliver instant knowledge within a gamified environment.

## Setup
Follow steps to set up and run bot locally.

### Prerequisites
- Python 3.8+
- `pip` (Python package installer)
- Access to **MongoDB** database instance (local for development)

### 1. Clone the Repository
```bash
git clone https://github.com/UFSPS/SignalRank
cd SignalRank
```

### 2. Install Required Project Dependencies

```
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create `.env` file following `.env.example`. Be sure to edit the file and fill in the unique values.

### 4. Running the Bot
Once the `.env` file is configured, start the application:
```
python main.py
```
If the connection is successful, you should see confirmation messages regarding the database connection and the bot's readiness in your console.

## Workflow
Avoid direct commits to `main`, keep it functional and stable. For new features, bug fix, or experiment, create a new branch off of `main`, make changes and push to main when ready. 

## Working with APIs
**1. Install and import the required module**  
Most APIs have an official or community-supported Python library. For example:
```
pip install requests
```
Then at the top of the file where it is needed:
```python
import requests
```
If it's a specialized API like `pymongo` or `google-genai`, you'd install that library instead:
```
pip install pymongo
pip install google-genai
```

**2. Get the API key**  
Requires an account on the API provider's site, where you can then generate an API key. In general, we should all be using the same API keys to keep everything consistent, although some local testing can be performed with a local instance of MongoDB instead of one on the cloud... but that would require some more configurations and extra downloads.

Note: keys should be stored in the .env file rather than hardcoded. **NEVER** push your .env file to the repo. The .gitignore file should handle this (tells git to ignore certain files). Variables located in .env should be secret and never public.

You can load the API key and get its value in string format via os:

```python
import os

token = os.getenv("DISCORD_TOKEN")
```

**3. Make an API request**  
For the trivia DB, use the `requests` library, which will return the data is JSON format. 

For `pymongo` and `google-genai`, refer to the official documentation to get started:
- pymongo: https://www.mongodb.com/docs/languages/python/
- google-genai: pymongo-driver/current/get-started/#connect-to-mongodb
https://github.com/googleapis/python-genai

**4. Hadle reponse data**  
Parse the data and format it for bot reponses/requests.

**5. Integrate with the bot**  
Once you have working API logic, wrap it in a function that the bot interface will be able to call on (through cogs!).

**Final Note: Keep dependencies up to date!**  
Whenever you install a new library, **add it to `requirements.txt`** so others can install it easily.
Likewise, run:
```
pip install -r requirements.txt
```
after pulling updates to make sure your environment matches the project's dependencies.