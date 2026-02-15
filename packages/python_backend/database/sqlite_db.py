import sqlite3
import os

DATABASE_FILE = os.path.join(os.path.dirname(__file__), "..", "local.db")

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        base_formality_level INTEGER DEFAULT 3,
        base_friendliness_level INTEGER DEFAULT 3,
        base_emotion_level INTEGER DEFAULT 3,
        base_directness_level INTEGER DEFAULT 3,
        session_formality_level REAL,
        session_friendliness_level REAL,
        session_emotion_level REAL,
        session_directness_level REAL,
        questionnaire_responses TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversion_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        original_text TEXT NOT NULL,
        converted_texts TEXT NOT NULL,
        context TEXT DEFAULT 'personal',
        user_rating INTEGER,
        selected_version TEXT,
        feedback_text TEXT,
        sentiment_analysis TEXT,
        prompts_used TEXT,
        model_used TEXT DEFAULT 'gpt-4o',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS negative_preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        avoid_flowery_language TEXT DEFAULT 'moderate',
        avoid_repetitive_words TEXT DEFAULT 'moderate',
        comma_usage_style TEXT DEFAULT 'moderate',
        content_over_format TEXT DEFAULT 'moderate',
        bullet_point_usage TEXT DEFAULT 'moderate',
        emoticon_usage TEXT DEFAULT 'strict',
        custom_negative_prompts TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vector_document_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_hash TEXT UNIQUE NOT NULL,
        file_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_size_bytes INTEGER NOT NULL,
        content_type TEXT DEFAULT 'text/plain',
        embedding_model TEXT NOT NULL,
        chunk_count INTEGER NOT NULL,
        chunk_size INTEGER NOT NULL,
        chunk_overlap INTEGER NOT NULL,
        faiss_index_path TEXT NOT NULL,
        vector_dimension INTEGER NOT NULL,
        status TEXT DEFAULT 'active',
        last_accessed TEXT DEFAULT CURRENT_TIMESTAMP,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rag_query_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        query_text TEXT NOT NULL,
        query_hash TEXT NOT NULL,
        context_type TEXT DEFAULT 'general',
        retrieved_documents TEXT,
        similarity_scores TEXT,
        total_search_time_ms INTEGER DEFAULT 0,
        generated_answer TEXT,
        answer_quality_score REAL,
        model_used TEXT DEFAULT 'gpt-4',
        total_generation_time_ms INTEGER DEFAULT 0,
        user_rating INTEGER,
        user_feedback TEXT,
        was_helpful INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS company_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id TEXT,
        company_name TEXT,
        industry TEXT,
        team_size TEXT,
        primary_business TEXT,
        communication_style TEXT,
        main_channels TEXT,
        target_audience TEXT,
        generated_profile TEXT,
        survey_data TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
