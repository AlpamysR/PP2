import psycopg2
from psycopg2 import sql
from config import DB_CONFIG
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            self.create_tables()
        except Exception as e:
            print(f"Database connection error: {e}")
            
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id SERIAL PRIMARY KEY,
                    player_id INTEGER REFERENCES players(id),
                    score INTEGER NOT NULL,
                    level_reached INTEGER NOT NULL,
                    played_at TIMESTAMP DEFAULT NOW()
                );
            """)
            self.conn.commit()
        except Exception as e:
            print(f"Error creating tables: {e}")
            self.conn.rollback()
            
    def get_or_create_player(self, username):
        """Get player ID or create new player"""
        try:
            self.cursor.execute(
                "INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO UPDATE SET username = EXCLUDED.username RETURNING id",
                (username,)
            )
            player_id = self.cursor.fetchone()[0]
            self.conn.commit()
            return player_id
        except Exception as e:
            print(f"Error getting/creating player: {e}")
            self.conn.rollback()
            return None
            
    def save_game_session(self, username, score, level_reached):
        """Save game session to database"""
        try:
            player_id = self.get_or_create_player(username)
            if player_id:
                self.cursor.execute(
                    "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
                    (player_id, score, level_reached)
                )
                self.conn.commit()
        except Exception as e:
            print(f"Error saving game session: {e}")
            self.conn.rollback()
            
    def get_leaderboard(self, limit=10):
        """Get top 10 scores"""
        try:
            self.cursor.execute("""
                SELECT p.username, gs.score, gs.level_reached, gs.played_at
                FROM game_sessions gs
                JOIN players p ON gs.player_id = p.id
                ORDER BY gs.score DESC
                LIMIT %s
            """, (limit,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching leaderboard: {e}")
            return []
            
    def get_personal_best(self, username):
        """Get player's personal best score"""
        try:
            self.cursor.execute("""
                SELECT MAX(gs.score)
                FROM game_sessions gs
                JOIN players p ON gs.player_id = p.id
                WHERE p.username = %s
            """, (username,))
            result = self.cursor.fetchone()
            return result[0] if result[0] else 0
        except Exception as e:
            print(f"Error fetching personal best: {e}")
            return 0
            
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()