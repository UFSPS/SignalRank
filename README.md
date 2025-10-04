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