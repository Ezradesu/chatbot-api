import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

# --------------------------------
# 1. Load ENV
# --------------------------------
load_dotenv()

db_url = os.getenv("DATABASE_URL")
api_key = os.getenv("GOOGLE_API_KEY")

# --------------------------------
# 2. Connect ke Supabase Postgres
# --------------------------------
db = SQLDatabase.from_uri(db_url)

# --------------------------------
# 3. Init LLM
# --------------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=api_key
)

# --------------------------------
# 4. Create SQL Agent
# --------------------------------
agent_executor = create_sql_agent(
    llm=llm,
    db=db,
    verbose=True,
    handle_parsing_errors=True
)

# --------------------------------
# 5. Query natural language
# --------------------------------
print("\n--- Mulai Eksekusi Query ---\n")
response = agent_executor.invoke({"input": "mesin mana saja yang membutuhkan perbaikan?"})

print("\n--- JAWABAN AKHIR ---")
print(response["output"])
