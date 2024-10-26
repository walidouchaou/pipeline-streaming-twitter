import time
import logging
from datetime import datetime

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

class LoginPage(BasePage):
    # Constantes pour les sélecteurs XPath
    SELECTORS = {
        'username_input': "//input[@name='text' and @type='text']",
        'email_input': "//input[@name='text']",
        'password_input': "//input[@autocomplete='current-password']",
        'tweet_article': '//article[@data-testid="tweet" and not(@disabled)]'
    }

    def __init__(self):
        super().__init__()
        self.username = "yannioucha3706"
        self.password = "Wm16062017@"
        self.email = "walidouchaou1998@gmail.com"
        self.wait = WebDriverWait(self.driver, 10)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def ensure_logged_in(self):
        """S'assure que l'utilisateur est connecté avant toute action"""
        if not self.is_logged_in():
            self.logger.info("Session non détectée, connexion en cours...")
            self.login()
        else:
            self.logger.info("Session active détectée")

    def is_logged_in(self):
        """Vérifie si l'utilisateur est déjà connecté"""
        try:
            self.driver.get("https://x.com/home")
            time.sleep(3)  # Attente courte pour le chargement
            return "login" not in self.driver.current_url
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification de connexion : {e}")
            return False

    def wait_and_send_keys(self, xpath, keys, description):
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

    def get_tweets(self, href_page):
        """
        Récupère les tweets du jour en excluant les tweets épinglés
        """
        try:
            self.logger.info(f"Récupération des tweets de : {href_page}")
            self.ensure_logged_in()
            
            self.driver.get(href_page)
            time.sleep(3)
            self.scroll_by_pages(pages=3)
            articles = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, self.SELECTORS['tweet_article'])
                )
            )
            
            tweets = []
            today = datetime.now().date()
            
            for article in articles:
                try:
                    article_soup = BeautifulSoup(article.get_attribute('outerHTML'), 'html.parser')
                    
                    # Vérifier si c'est un tweet épinglé
                    pinned_div = article_soup.find('div', text='Pinned')
                    if pinned_div:
                        self.logger.debug("Tweet épinglé ignoré")
                        continue
                    
                    # Récupération de la date du tweet
                    publication_time = article_soup.find('time')
                    if publication_time:
                        tweet_date = datetime.fromisoformat(publication_time['datetime']).date()
                        # Ne garder que les tweets d'aujourd'hui
                        if tweet_date == today:
                            tweet_text = article_soup.find('div', {'data-testid': 'tweetText'}).text
                            tweets.append((publication_time['datetime'], tweet_text))
                            self.logger.debug(f"Tweet du jour récupéré - Date: {tweet_date}")
                    
                except Exception as e:
                    self.logger.warning(f"Erreur lors de la récupération du tweet: {e}")
                    continue
                    
            self.logger.info(f"Nombre de tweets du jour récupérés : {len(tweets)}")
            return tweets
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des tweets : {e}")
            return []



    def scroll_by_pages(self, pages=1):
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
