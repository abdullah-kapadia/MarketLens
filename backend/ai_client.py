import requests

AI_SERVICE_URL = "http://localhost:8001/ai/generate"

def get_ai_report(symbol: str):
    try:
        response = requests.post(
            AI_SERVICE_URL,
            json={"symbol": symbol},
            timeout=4
        )
        response.raise_for_status()
        return response.json()
    
    except Exception:
        return {
            "symbol": symbol,
            "headline": f"{symbol}: Bearish Bias as Key Support Tested",
            "commentary": (
                f"{symbol} is currently testing critical support levels "
                "amid fragile momentum. While near-term sentiment remains cautious, "
                "any pullback towards support may present selective buying opportunities. "
                "Investors are advised to monitor volume behavior and broader market cues."
            ),
            "chart_path": f"outputs/charts/{symbol}.png"
        }