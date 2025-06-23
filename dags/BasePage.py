from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

class BasePage:
    _driver = None  # Variable de classe pour stocker l'instance unique du driver

    def __init__(self):
        if BasePage._driver is None:
            BasePage._driver = self.create_driver()
        self.driver = BasePage._driver

    @staticmethod
    def create_driver():
        """Crée une instance unique du driver avec les options optimisées"""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--disable-dev-shm-usage")
        # Options pour la persistance de session
        chrome_options.add_argument('--user-data-dir=/opt/airflow/chrome_profile')
        chrome_options.add_argument('--profile-directory=Default')
        
        # Options supplémentaires pour améliorer la stabilité
        # Désactive l'accélération matérielle GPU pour améliorer la stabilité en mode headless
        chrome_options.add_argument('--disable-gpu')
        # Désactive les notifications du navigateur pour éviter les interruptions
        chrome_options.add_argument('--disable-notifications')
        # Empêche l'ouverture de fenêtres pop-up qui pourraient perturber l'automatisation
        chrome_options.add_argument('--disable-popup-blocking')
        
        try:
            driver = webdriver.Chrome(
                service=ChromeService(
                    ChromeDriverManager().install()  # Suppression de la version fixe
                ),
                options=chrome_options
            )
            print("Driver initialisé avec succès")
            return driver
        except Exception as e:
            print(f"Erreur lors de l'initialisation du driver: {e}")
            raise

    @classmethod
    def quit_driver(cls):
        """Méthode pour fermer proprement le driver"""
        if cls._driver:
            try:
                cls._driver.quit()
                cls._driver = None
                print("Driver fermé avec succès")
            except Exception as e:
                print(f"Erreur lors de la fermeture du driver: {e}")

    def __del__(self):
        """Destructeur pour s'assurer que le driver est fermé"""
        try:
            if hasattr(self, 'driver') and self.driver:
                self.quit_driver()
        except Exception as e:
            print(f"Erreur lors de la destruction: {e}")
