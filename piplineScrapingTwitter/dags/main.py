from LoginPage import LoginPage     
import json
from datetime import datetime
from typing import List


def main(comptes_twitter: List[str]) -> None:
    try:
        loginPage: LoginPage = LoginPage()  # Créez une instance de LoginPage
        for compte in comptes_twitter:
            try:
                compte_name: str = compte.split('/')[-1]  # Extrait le nom du compte de l'URL
                print(f"Récupération des tweets pour {compte_name}")
                loginPage.get_tweets(compte)
                print(f"Tweets récupérés avec succès pour {compte_name}")
            except Exception as e:
                print(f"Erreur lors de la récupération des tweets pour {compte_name}: {e}")
                continue
    except Exception as e:
        print(f"Une erreur générale s'est produite : {e}")
    finally:
        # Fermeture du navigateur à la fin de toutes les opérations
        loginPage.driver.quit()
    
 


