"""
Module de gestion de la base de données pour les tweets
"""
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extensions import connection, cursor
import logging

TweetTuple = Tuple[datetime, str, str, str]  # (publication_datetime, text, image_url, author)

class TwitterDatabase:
    """Gère les opérations de base de données pour les tweets"""
    
    pool: SimpleConnectionPool
    logger: logging.Logger
    
    def __init__(self) -> None:
        """
        Initialise la connexion à la base de données PostgreSQL
        avec les paramètres pour un environnement conteneurisé
        """
        db_config: Dict[str, str] = {
            'host': 'piplinescrapingtwitter-tweets_db-1',  # nom du service dans docker-compose
            'port': '5432',      # port par défaut de PostgreSQL
            'database': 'twitter_data',
            'user': 'root',
            'password': 'root'
        }
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            **db_config
        )
        self._init_db()

    def _init_db(self) -> None:
        """Initialise la structure de la base de données"""
        try:
            conn: connection = self._get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS tweets (
                        id SERIAL PRIMARY KEY,
                        publication_datetime TIMESTAMP,
                        tweet_text TEXT,
                        image_url TEXT,
                        author_name VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(publication_datetime, tweet_text, author_name)
                    )
                """)
            conn.commit()
            self.pool.putconn(conn)
            self.logger.info("Base de données initialisée avec succès")
        except Exception as e:
            self.logger.error(f"Erreur d'initialisation de la base de données: {str(e)}")
            raise

    def _get_connection(self) -> connection:
        """Récupère une connexion du pool"""
        conn: connection = self.pool.getconn()
        if conn is None:
            raise RuntimeError("Impossible d'obtenir une connexion")
        return conn

    def tweet_exists(self, tweet: TweetTuple) -> bool:
        """
        Vérifie si un tweet existe déjà dans la base
        Args:
            tweet (TweetTuple): Tuple contenant (datetime, text, image_url, author)
        Returns:
            bool: True si le tweet existe, False sinon
        """
        try:
            conn: connection = self._get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 1 FROM tweets 
                    WHERE publication_datetime = %s
                    AND tweet_text = %s
                    AND author_name = %s
                """, (tweet[0], tweet[1], tweet[3]))
                result: Optional[Tuple] = cur.fetchone()
            self.pool.putconn(conn)
            return result is not None
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification du tweet: {str(e)}")
            return False

    def insert_tweet(self, tweet: TweetTuple) -> bool:
        """
        Insère un nouveau tweet dans la base
        Args:
            tweet (TweetTuple): Tuple contenant (datetime, text, image_url, author)
        Returns:
            bool: True si l'insertion réussit, False sinon
        """
        try:
            if not self.tweet_exists(tweet):
                conn: connection = self._get_connection()
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO tweets (publication_datetime, tweet_text, image_url, author_name)
                        VALUES (%s, %s, %s, %s)
                    """, tweet)
                conn.commit()
                self.pool.putconn(conn)
                self.logger.info(f"Tweet de {tweet[3]} inséré avec succès")
                return True
            self.logger.info(f"Tweet de {tweet[3]} déjà existant")
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de l'insertion du tweet: {str(e)}")
            return False

    def insert_tweets(self, tweets: List[TweetTuple]) -> int:
        """
        Insère une liste de tweets dans la base
        Args:
            tweets (List[TweetTuple]): Liste de tweets à insérer
        Returns:
            int: Nombre de tweets insérés
        """
        inserted_count = 0
        for tweet in tweets:
            if self.insert_tweet(tweet):
                inserted_count += 1
        return inserted_count

    def close(self) -> None:
        """Ferme le pool de connexions"""
        try:
            self.pool.closeall()
            self.logger.info("Connexions à la base de données fermées")
        except Exception as e:
            self.logger.error(f"Erreur lors de la fermeture des connexions: {str(e)}")