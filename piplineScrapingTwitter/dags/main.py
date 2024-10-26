from LoginPage import LoginPage
import json
from datetime import datetime
import os


def main(comptes_twitter , ligne_type):
    try:
        loginPage = LoginPage()  # Créez une instance de LoginPage
        
        # Dictionnaire pour stocker tous les tweets
        all_tweets = {}
        
        # Boucle sur chaque compte
        for compte in comptes_twitter:
            try:
                print(f"Récupération des tweets pour {compte}")
                tweets = loginPage.get_tweets(compte)
                compte_name = compte.split('/')[-1]  # Extrait le nom du compte de l'URL
                all_tweets[compte_name] = tweets
                print(f"Tweets récupérés avec succès pour {compte_name}")
            except Exception as e:
                print(f"Erreur lors de la récupération des tweets pour {compte}: {e}")
                continue
        
        # Définition du chemin relatif au dossier du script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        OUTPUT_DIR = os.path.join(current_dir, "data")
        
        # Sauvegarde des données dans un fichier JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(OUTPUT_DIR, f"tweets_{ligne_type}_{timestamp}.json")
        
        # Création du répertoire data s'il n'existe pas
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_tweets, f, ensure_ascii=False, indent=4)
            
        print(f"Collecte des tweets terminée avec succès. Fichier sauvegardé dans : {output_path}")
        
    except Exception as e:
        print(f"Une erreur générale s'est produite : {e}")
    finally:
        # Fermeture du navigateur à la fin de toutes les opérations
        loginPage.driver.quit()
    
    return all_tweets  # Retourner les tweets collectés

if __name__ == "__main__":
    main([
        "https://x.com/RER_A",
        "https://x.com/RERB",
        "https://x.com/RERC_SNCF",
        "https://x.com/RERD_SNCF",
        "https://x.com/RERE_T4_SNCF",
        "https://x.com/LigneH_SNCF",
        "https://x.com/LIGNEJ_SNCF",
        "https://x.com/LigneK_SNCF",
        "https://x.com/LIGNEL_sncf",
        "https://x.com/lignesNetU_SNCF",
        "https://x.com/LIGNEP_SNCF",
        "https://x.com/LIGNER_SNCF"
    ])
