"""
Supabase Integration for StorEdge DaVinci Analyzer

This module handles storing analysis results and user sessions in Supabase.
"""

import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging
from supabase import create_client, Client
from web_config import SUPABASE_CONFIG, DB_CONFIG

logger = logging.getLogger(__name__)

class SupabaseManager:
    """Manages Supabase operations for the web application."""
    
    def __init__(self):
        """Initialize Supabase client."""
        try:
            self.supabase: Client = create_client(
                SUPABASE_CONFIG["url"], 
                SUPABASE_CONFIG["key"]
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.supabase = None
    
    def store_analysis_session(self, session_data: Dict) -> Optional[str]:
        """
        Store analysis session data in Supabase.
        
        Args:
            session_data: Dictionary containing session information
            
        Returns:
            Session ID if successful, None otherwise
        """
        if not self.supabase:
            logger.warning("Supabase client not available")
            return None
        
        try:
            # Prepare data for storage
            session_record = {
                "created_at": datetime.now().isoformat(),
                "user_email": session_data.get("user_email", "anonymous"),
                "total_units": session_data.get("total_units", 0),
                "miscompare_count": session_data.get("miscompare_count", 0),
                "high_severity_count": session_data.get("high_severity_count", 0),
                "analysis_summary": json.dumps(session_data.get("summary", {})),
                "file_names": json.dumps(session_data.get("file_names", [])),
                "status": "completed"
            }
            
            # Insert into Supabase
            result = self.supabase.table("analysis_sessions").insert(session_record).execute()
            
            if result.data:
                session_id = result.data[0]["id"]
                logger.info(f"Analysis session stored with ID: {session_id}")
                return session_id
            else:
                logger.error("Failed to store analysis session")
                return None
                
        except Exception as e:
            logger.error(f"Error storing analysis session: {e}")
            return None
    
    def store_analysis_results(self, session_id: str, results_df: pd.DataFrame) -> bool:
        """
        Store detailed analysis results in Supabase.
        
        Args:
            session_id: ID of the analysis session
            results_df: DataFrame containing analysis results
            
        Returns:
            True if successful, False otherwise
        """
        if not self.supabase:
            logger.warning("Supabase client not available")
            return False
        
        try:
            # Convert DataFrame to records
            records = results_df.to_dict('records')
            
            # Add session_id to each record
            for record in records:
                record["session_id"] = session_id
                record["created_at"] = datetime.now().isoformat()
            
            # Insert in batches to avoid size limits
            batch_size = 100
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                result = self.supabase.table("analysis_results").insert(batch).execute()
                
                if not result.data:
                    logger.error(f"Failed to insert batch {i//batch_size + 1}")
                    return False
            
            logger.info(f"Stored {len(records)} analysis results for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing analysis results: {e}")
            return False
    
    def get_analysis_history(self, user_email: str = None, limit: int = 10) -> List[Dict]:
        """
        Retrieve analysis history for a user.
        
        Args:
            user_email: Email of the user (optional)
            limit: Maximum number of records to return
            
        Returns:
            List of analysis session records
        """
        if not self.supabase:
            logger.warning("Supabase client not available")
            return []
        
        try:
            query = self.supabase.table("analysis_sessions").select("*")
            
            if user_email:
                query = query.eq("user_email", user_email)
            
            query = query.order("created_at", desc=True).limit(limit)
            result = query.execute()
            
            if result.data:
                logger.info(f"Retrieved {len(result.data)} analysis sessions")
                return result.data
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving analysis history: {e}")
            return []
    
    def get_analysis_results(self, session_id: str) -> Optional[pd.DataFrame]:
        """
        Retrieve analysis results for a specific session.
        
        Args:
            session_id: ID of the analysis session
            
        Returns:
            DataFrame containing analysis results, or None if not found
        """
        if not self.supabase:
            logger.warning("Supabase client not available")
            return None
        
        try:
            result = self.supabase.table("analysis_results").select("*").eq("session_id", session_id).execute()
            
            if result.data:
                df = pd.DataFrame(result.data)
                logger.info(f"Retrieved {len(df)} analysis results for session {session_id}")
                return df
            else:
                logger.warning(f"No results found for session {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving analysis results: {e}")
            return None
    
    def create_tables(self) -> bool:
        """
        Create required tables in Supabase if they don't exist.
        This should be run once during setup.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.supabase:
            logger.warning("Supabase client not available")
            return False
        
        try:
            # Note: In a real implementation, you would use Supabase SQL editor
            # or migrations to create these tables. This is just a placeholder.
            
            tables_sql = """
            -- Analysis Sessions Table
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                user_email TEXT,
                total_units INTEGER,
                miscompare_count INTEGER,
                high_severity_count INTEGER,
                analysis_summary JSONB,
                file_names JSONB,
                status TEXT DEFAULT 'completed'
            );
            
            -- Analysis Results Table
            CREATE TABLE IF NOT EXISTS analysis_results (
                id SERIAL PRIMARY KEY,
                session_id INTEGER REFERENCES analysis_sessions(id),
                unit TEXT,
                unit_status TEXT,
                final_status TEXT,
                actual_lock_status TEXT,
                expected_lock_status TEXT,
                is_miscompare BOOLEAN,
                miscompare_severity TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Create indexes for better performance
            CREATE INDEX IF NOT EXISTS idx_analysis_sessions_user_email ON analysis_sessions(user_email);
            CREATE INDEX IF NOT EXISTS idx_analysis_sessions_created_at ON analysis_sessions(created_at);
            CREATE INDEX IF NOT EXISTS idx_analysis_results_session_id ON analysis_results(session_id);
            CREATE INDEX IF NOT EXISTS idx_analysis_results_unit ON analysis_results(unit);
            """
            
            logger.info("Table creation SQL prepared. Run this in Supabase SQL editor.")
            logger.info(tables_sql)
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test the Supabase connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        if not self.supabase:
            return False
        
        try:
            # Try to query a simple table
            result = self.supabase.table("analysis_sessions").select("id").limit(1).execute()
            logger.info("Supabase connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False

# Global instance
supabase_manager = SupabaseManager()
