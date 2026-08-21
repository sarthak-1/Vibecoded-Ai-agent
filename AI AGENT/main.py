import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Load environment variables
load_dotenv()

app = Flask(__name__)

# 1. Initialize client
client = genai.Client()

# 2. Define your exact system prompt
genz_instruction = """
You are a Gen Z news anchor. Your job is to take news topics, headlines, or user questions 
and break them down into pure Gen Z slang (e.g., 'no cap', 'fr fr', 'lowkey', 'cooked', 
'slay', 'bet', 'aura points', 'main character', Ate / Left no crumbs: Nailed a performance, look, or task completely.Bet: Agreement, 
meaning "yes" or "sure". Bussin: Extremely good or delicious (usually for food). Cap / No Cap: Cap means a lie; no cap means telling the truth.
Cheugy: Outdated, uncool, or trying too hard to be trendy. Delulu: Short for delusional; living in an unrealistic fantasy. Drip: Cool, fashionable clothing or style. Flex: To show off or brag about possessions or achievements. 
Ghosting: Suddenly cutting off all communication with someone.GOAT: Greatest of All Time.High-key / Low-key: High-key means openly or very much; low-key means secretly or mildly.
Its giving: The vibe or energy a person or thing emits (e.g., "It's giving luxury").Mid: Mediocre, average, or underwhelming.Rizz: Short for charisma; skill in charming or flirting with someone.
Sigma: An independent, cool, self-reliant male persona.Slay: To succeed or look amazing while doing something.Sus: Suspicious or shady.Tea: Gossip or juicy information.Vibe check: An assessment of someone's mood or general energy leve).
Keep summaries short, punchy, and formatted with bullet points. 
"""

# Note: You can re-enable live search here when your rate limits reset by adding:
# tools=[types.Tool(google_search=types.GoogleSearch())]
agent_config = types.GenerateContentConfig(
    system_instruction=genz_instruction,
    temperature=0.8
)

# 3. Create the chat session
chat_session = client.chats.create(
    model="gemini-3.6-flash",
    config=agent_config
)

# Render the web interface
@app.route('/')
def home():
    return render_template('index.html')

# Handle API requests from the webpage
@app.route('/chat', methods=['POST'])
def chat():
    user_prompt = request.json.get('prompt', '')
    
    if not user_prompt.strip():
        return jsonify({'reply': 'Yo, drop a topic or headline fr fr.'})

    try:
        response = chat_session.send_message(user_prompt)
        
        if response.text:
            return jsonify({'reply': response.text})
        else:
            return jsonify({'reply': '[Empty response received. Try rephrasing!]' })

    except APIError as e:
        if e.code == 429:
            return jsonify({'reply': '⚠️ Rate limit hit (429)! Please wait ~60 seconds before sending your next message.'})
        else:
            return jsonify({'reply': f'❌ Google API Error ({e.code}): {e.message}'})
    except Exception as e:
        return jsonify({'reply': f'❌ Unexpected error: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)