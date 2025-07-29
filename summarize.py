# summarize.py
import json
import openai
import pandas as pd
from config import OPENAI_API_KEY

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def summarize_trials(trials_json_path: str) -> str:
    """
    Loads Optuna trial history from JSON, identifies top 5 trials,
    and uses GPT-4 to summarize key parameter patterns.
    """
    df = pd.read_json(trials_json_path)

    # Optuna stores parameters under 'params_<name>' columns
    param_cols = [col for col in df.columns if col.startswith('params_')]
    top5 = df.nlargest(5, "value")[param_cols + ['value']]
    rename_map = {col: col.replace('params_', '') for col in param_cols}
    top5 = top5.rename(columns=rename_map)

    prompt = f"""You are a quantitative analyst. Here are the top 5 hyperparameter trials for our SMA+RSI strategy:
{top5.to_csv(index=False)}

In clear, concise language, summarize the common characteristics of these setups and recommend which parameters we should choose for live trading."""

    # Request summary from OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    summary = summarize_trials("optuna_study_trials.json")
    print(summary)
