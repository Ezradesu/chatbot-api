from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = Flask(__name__)
CORS(app)  # 🔥 WAJIB supaya Next.js bisa fetch

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

db = SQLDatabase.from_uri(os.getenv("DATABASE_URL"))

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

agent_executor = create_sql_agent(llm=llm, db=db, verbose=True, handle_parsing_errors=True)


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message')
    session_id = data.get('session_id', 'default_session')

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Query ke agent
        response = agent_executor.invoke({"input": user_message})
        bot_answer = response["output"]

        # Simpan ke Supabase
        try:
            supabase.table("chat_logs").insert({
                "session_id": session_id,
                "user_query": user_message,
                "bot_response": bot_answer
            }).execute()
        except Exception as log_error:
            print(f"Gagal simpan log: {log_error}")

        return jsonify({
            "response": bot_answer,
            "status": "success"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
