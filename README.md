# Poker Analysis App

A Streamlit application that analyzes poker game sessions using CrewAI.

## Local Development

1. Create a conda environment:
```bash
conda create -n crewai_env python=3.9
conda activate crewai_env
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env` file:
```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

4. Run the app:
```bash
streamlit run app.py
```

## Deploying to Streamlit Cloud

1. Push your code to GitHub

2. Go to [share.streamlit.io](https://share.streamlit.io)

3. Connect your GitHub repository

4. Add the following secrets in the Streamlit Cloud dashboard:
   - OPENAI_API_KEY
   - ANTHROPIC_API_KEY

5. Deploy!
