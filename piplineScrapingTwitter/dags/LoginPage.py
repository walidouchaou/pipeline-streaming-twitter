import time
import logging
import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from BasePage import BasePage
from twitter_database import TwitterDatabase
from typing import Dict, List, Optional, Tuple, Any
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver

class LoginPage(BasePage):
    # Constantes pour les sélecteurs XPath
    SELECTORS: Dict[str, str] = {
        'username_input': "//input[@name='text' and @type='text']",
        'email_input': "//input[@name='text']",
        'password_input': "//input[@autocomplete='current-password']",
        'tweet_article': '//article[@data-testid="tweet" and not(@disabled)]'
    }

    def __init__(self) -> None:
        super().__init__()
        self.username: str = ""
        self.password: str = ""
        self.email: str = ""
        self.wait: WebDriverWait = WebDriverWait(self.driver, 10)
        logging.basicConfig(level=logging.INFO)
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.db: TwitterDatabase = TwitterDatabase()

    def ensure_logged_in(self) -> None:
        """S'assure que l'utilisateur est connecté avant toute action"""
        if not self.is_logged_in():
            self.logger.info("Session non détectée, connexion en cours...")
            self.login()
        else:
            self.logger.info("Session active détectée")

    def is_logged_in(self) -> bool:
        """Vérifie si l'utilisateur est déjà connecté"""
        try:
            self.driver.get("https://x.com/home")
            time.sleep(3)  # Attente courte pour le chargement
            return "login" not in self.driver.current_url
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification de connexion : {e}")
            return False

    def wait_and_send_keys(self, xpath: str, keys: str, description: str) -> bool:
        """Attend la présence d'un élément et envoie des touches"""
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            element.clear()  # Nettoie le champ avant la saisie
            element.send_keys(keys)
            element.send_keys(Keys.RETURN)
            self.logger.info(f"{description} envoyé avec succès")
            return True
        except TimeoutException:
            self.logger.error(f"Timeout en attendant l'élément : {description}")
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de {description}: {e}")
            return False

    def login(self):
        """Processus de connexion à Twitter"""
        try:
            self.logger.info("Début du processus de connexion")
            self.driver.get("https://x.com/i/flow/login")

            # Saisie du nom d'utilisateur
            if not self.wait_and_send_keys(
                self.SELECTORS['username_input'], 
                self.username, 
                "nom d'utilisateur"
            ):
                raise Exception("Échec de la saisie du nom d'utilisateur")

            # Saisie de l'email si nécessaire
            try:
                self.wait_and_send_keys(
                    self.SELECTORS['email_input'], 
                    self.email, 
                    "email"
                )
            except TimeoutException:
                self.logger.info("Pas de demande d'email, continuation...")

            # Saisie du mot de passe
            if not self.wait_and_send_keys(
                self.SELECTORS['password_input'], 
                self.password, 
                "mot de passe"
            ):
                raise Exception("Échec de la saisie du mot de passe")

            time.sleep(3)  # Attente courte pour la validation
            self.logger.info("Connexion réussie")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la connexion : {e}")
            raise
    
    def get_tweets(self, href_page: str) -> None:
        """Point d'entrée principal pour la récupération des tweets"""
        try:
            self._navigate_to_page(href_page)
            articles = self._fetch_tweet_articles()
            tweets = self._process_articles(articles)
            self._save_tweets(tweets)
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des tweets : {e}")

    def _navigate_to_page(self, href_page: str) -> None:
        """Navigation vers la page cible"""
        self.logger.info(f"Navigation vers : {href_page}")
        self.driver.get(href_page)
        time.sleep(3)
        self.scroll_by_pages(pages=4)
        time.sleep(3)

    def _fetch_tweet_articles(self) -> List[WebElement]:
        """Récupération des articles de tweets"""
        return self.wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, self.SELECTORS['tweet_article'])
            )
        )

    def _process_articles(self, articles: List[WebElement]) -> List[Tuple[str, str, Optional[str], Optional[str]]]:
        """Traitement des articles pour extraire les tweets"""
        tweets = []
        time_window = self._get_time_window()
        
        for article in articles:
            tweet_data = self._extract_tweet_data(article)
            if tweet_data and self._is_valid_tweet(tweet_data, time_window):
                tweets.append(self._format_tweet_data(tweet_data))
        
        return tweets

    def _extract_tweet_data(self, article: WebElement) -> Optional[Dict[str, Any]]:
        """Extraction des données d'un tweet individuel"""
        try:
            article_soup = BeautifulSoup(article.get_attribute('outerHTML'), 'html.parser')
            
            if self._is_pinned_tweet(article_soup):
                return None
                
            return {
                'line_name': self._get_author_name(article_soup),
                'image': self._get_tweet_image(article_soup),
                'publication_time': self._get_publication_time(article_soup),
                'text': self._get_tweet_text(article_soup)
            }
        except Exception as e:
            self.logger.warning(f"Erreur lors de l'extraction du tweet: {e}")
            return None

    def _get_time_window(self) -> Dict[str, datetime.datetime]:
        """Définition de la fenêtre temporelle pour les tweets"""
        now = datetime.datetime.now()
        return {
            'start': now - datetime.timedelta(hours=1),
            'end': now
        }

    def _is_valid_tweet(self, tweet_data: Optional[Dict[str, Any]], time_window: Dict[str, datetime.datetime]) -> bool:
        """Vérifie si le tweet est dans la fenêtre temporelle"""
        if not tweet_data or not tweet_data['publication_time']:
            return False
            
        tweet_datetime = datetime.datetime.strptime(
            tweet_data['publication_time']['datetime'], 
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        return time_window['start'] <= tweet_datetime <= time_window['end']

    def _format_tweet_data(self, tweet_data: Dict[str, Any]) -> Tuple[str, str, Optional[str], Optional[str]]:
        """Formatage des données du tweet pour le stockage"""
        return (
            tweet_data['publication_time']['datetime'],
            tweet_data['text'],
            tweet_data['image'],
            tweet_data['line_name']
        )

    def _save_tweets(self, tweets: List[Tuple[str, str, Optional[str], Optional[str]]]) -> None:
        """Sauvegarde des tweets en base de données"""
        if tweets:
            inserted_count = self.db.insert_tweets(tweets)
            self.logger.info(f"{inserted_count} nouveaux tweets stockés sur {len(tweets)} récupérés")

    # Méthodes auxiliaires pour l'extraction des données
    def _is_pinned_tweet(self, soup: BeautifulSoup) -> bool:
        return bool(soup.find('div', text='Pinned'))

    def _get_author_name(self, soup: BeautifulSoup) -> Optional[str]:
        name_element = soup.find('span', {'class': 'css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3'})
        return name_element.text if name_element else None

    def _get_tweet_image(self, soup: BeautifulSoup) -> Optional[str]:
        image_element = soup.find('img', {'class': 'r-4qtqp9 r-dflpy8 r-k4bwe5 r-1kpi4qh r-pp5qcn r-h9hxbl'})
        return image_element.get('src') if image_element else None

    def _get_publication_time(self, soup: BeautifulSoup) -> Optional[Any]:
        return soup.find('time')

    def _get_tweet_text(self, soup: BeautifulSoup) -> Optional[str]:
        text_element = soup.find('div', {'data-testid': 'tweetText'})
        return text_element.text if text_element else None

    def scroll_by_pages(self, pages: int = 1) -> None:
        """
        Fait défiler la page d'un nombre spécifique de hauteurs de fenêtre
        
        Args:
            pages (int): Nombre de pages à faire défiler (positif pour descendre, négatif pour monter)
        """
        self.logger.info(f"Défilement de {pages} pages")
        try:
            # Calcul de la hauteur à défiler basé sur la hauteur de la fenêtre
            viewport_height = self.driver.execute_script("return window.innerHeight")
            scroll_amount = viewport_height * pages
            
            # Utilisation de scrollBy avec animation fluide
            self.driver.execute_script("""
                window.scrollBy({
                    top: arguments[0],
                    behavior: 'smooth'
                });
            """, scroll_amount)
            
            time.sleep(2)  # Attente pour le chargement du contenu
            self.logger.debug(f"Défilement effectué de {scroll_amount}px")
                
        except Exception as e:
            self.logger.error(f"Erreur lors du défilement : {e}")

