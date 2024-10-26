from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import os


# Connexion à MongoDB
client = MongoClient("mongodb+srv://aya2024:aya2024@cluster0.m30i8.mongodb.net/")  
db = client["gestion_cabinet_db"]  # Créer ou se connecter à la base de données
patients_collection = db["patients_collection"]  # Créer ou se connecter à la collection
rdv_collection = db["rendezvous"]  # Collection pour les rendez-vous


# Gestion des patients



    
def generer_id_patient():
    dernier_patient = patients_collection.find_one(sort=[("_id", -1)])
    if dernier_patient:
        return dernier_patient["_id"] + 1
    else:
        return 1  

# Exemple d'utilisation dans la fonction ajouter_patient
def ajouter_patient(nom, prenom, adresse, numero_telephone, email, date_naissance):
    patient_id = generer_id_patient()  # Générer un identifiant unique
    patient = {
        "_id": patient_id,  
        "nom": nom,
        "prenom": prenom,
        "date_naissance": date_naissance,
        "adresse": adresse,
        "num_tel": numero_telephone,
        "email": email
    }
    patients_collection.insert_one(patient)
    print(f"Patient {nom} {prenom} ajouté avec ID {patient_id}.")




def afficher_patients():
    patients = list(patients_collection.find())  
    if patients:
        # Extraire les données des patients et les formater pour un tableau
        patients_data = []
        for patient in patients:
            patient_info = {
                "_id": patient.get("_id"),
                "Nom": patient.get("nom"),
                "Prénom": patient.get("prenom"),
                "Date de Naissance": patient.get("date_naissance"),
                "Adresse": patient.get("adresse"),
                "Numéro de Téléphone": patient.get("num_tel"),
                "Email": patient.get("email")
            }
            patients_data.append(patient_info)

        # Créer un DataFrame avec les données
        df = pd.DataFrame(patients_data)

        # Sauvegarder dans un fichier Excel
        file_name = "patients_list.xlsx"
        df.to_excel(file_name, index=False)

        # Ouvrir fichier Excel
        os.system(f"xdg-open {file_name}")  
        print(f"Liste des patients exportée dans le fichier {file_name} et ouvert.")

    else:
        print("Aucun patient trouvé.")

def mettre_a_jour_patient(id, nom, prenom, date_naissance, adresse, numero_telephone, email):
    try:
        
        
        # Créer un dictionnaire avec les nouvelles valeurs à mettre à jour
        nouvelles_valeurs = {
            "nom": nom,
            "prenom": prenom,
            "date_naissance": date_naissance,
            "adresse": adresse,
            "num_tel": numero_telephone,
            "email": email
        }
        
        # Exécuter la mise à jour dans MongoDB
        result = patients_collection.update_one(
            {"_id": id},  
            {"$set": nouvelles_valeurs}  
        )
        
        if result.modified_count > 0:
            print(f"Les informations du patient avec l'ID {id} ont été mises à jour.")
        else:
            print(f"Aucun patient trouvé avec l'ID {id} ou aucune modification apportée.")
    
    except ValueError:
        print("ID invalide. Veuillez entrer un entier valide.")




def supprimer_patient(id):
    patient = patients_collection.find_one({"_id": id})
    
    if patient:  
        patients_collection.delete_one({"_id": id})
        print(f"Patient de l'ID {id} supprimé.")
    else:
        print("Le patient est introuvable!")




def ajouter_rendezvous(patient_id, date_rdv, heure_rdv, motif, statut="En attente"):
    try:
        date_rdv = datetime.strptime(date_rdv, "%d/%m/%Y")
        heure_rdv = datetime.strptime(heure_rdv, "%H:%M").time()
    except ValueError:
        print("Format de date ou heure invalide.")
        return

    # Obtenir le dernier id_rdv dans la collection, trier par ordre décroissant
    dernier_rdv = rdv_collection.find_one(sort=[("id_rdv", -1)])
    
    # Si un id_rdv existe déjà, incrémentez-le, sinon démarrez à 1
    if dernier_rdv and "id_rdv" in dernier_rdv:
        nouvel_id_rdv = dernier_rdv["id_rdv"] + 1
    else:
        nouvel_id_rdv = 1  # Premier rendez-vous ou documents sans id_rdv
    print(nouvel_id_rdv)
    # Créer l'objet rendez-vous avec l'id_rdv
    rdv = {
        "id_rdv": nouvel_id_rdv,  # Ajout de l'id_rdv
        "patient_id": int(patient_id),
        "date_rdv": date_rdv,
        "heure_rdv": heure_rdv.strftime("%H:%M"),  # Conversion en chaîne
        "motif": motif,
        "statut": statut
    }

    # Insérer le rendez-vous dans la collection
    rdv_collection.insert_one(rdv)
    print(f"Rendez-vous ID {nouvel_id_rdv} ajouté pour le patient ID {patient_id} à {heure_rdv.strftime('%H:%M')} le {date_rdv.strftime('%d/%m/%Y')}.")






def afficher_rendezvous():
    rendezvous = list(rdv_collection.find())  
    if rendezvous:
        # Extraire les données des rendez-vous et les formater pour un tableau
        rdv_data = []
        for rdv in rendezvous:
            rdv_info = {
                "id_rdv": rdv.get("id_rdv"),
                "ID du Patient": rdv.get("patient_id"),
                "Date": rdv.get("date_rdv").strftime("%d/%m/%Y"),
                "Heure": rdv.get("heure_rdv"),
                "Motif": rdv.get("motif"),
                "Statut": rdv.get("statut")
            }
            rdv_data.append(rdv_info)

        # Créer un DataFrame avec les données
        df = pd.DataFrame(rdv_data)

        # Sauvegarder dans un fichier Excel
        file_name = "rendezvous_list.xlsx"
        df.to_excel(file_name, index=False)

        
        os.system(f"xdg-open {file_name}")  
        print(f"Liste des rendez-vous exportée dans le fichier {file_name} et ouvert.")
    else:
        print("Aucun rendez-vous trouvé.")




def mettre_a_jour_rendezvous(rdv_id, nouvelle_date, nouvelle_heure):
    try:
        # Vérifier et convertir la nouvelle date en datetime
        nouvelle_date = datetime.strptime(nouvelle_date, "%d/%m/%Y")
        nouvelle_heure = datetime.strptime(nouvelle_heure, "%H:%M").strftime("%H:%M")

        #c'est une forme de vérification pour que l'id soit entier
        rdv_id = int(rdv_id)

        # Mettre à jour les champs du rendez-vous 
        result = rdv_collection.update_one(
            {"id_rdv": rdv_id},
            {"$set": {"date_rdv": nouvelle_date, "heure_rdv": nouvelle_heure}}
        )

        # Vérifier si la mise à jour a été effective
        if result.matched_count > 0:
            print(f"Le rendez-vous avec l'ID {rdv_id} a été mis à jour.")
        else:
            print(f"Aucun rendez-vous trouvé avec l'ID {rdv_id}.")

    except ValueError as e:
        print(f"Erreur de format de date ou heure : {e}")





def supprimer_rendezvous(rdv_id):
    rdv_id = int(rdv_id)
    rdv_collection.delete_one({"_id": rdv_id})
    print(f"Rendez-vous ID {rdv_id} supprimé.")

def verifier_date(date_str):
    try:
        # Tenter de convertir la date dans le format JJ/MM/AAAA
        date_valide = datetime.strptime(date_str, "%d/%m/%Y")
        return True  # La date est valide
    except ValueError:
        return False 
# Interface utilisateur
while True:
    print("\nOptions:")
    print("1. Ajouter un patient")
    print("2. Afficher les patients")
    print("3. Mettre à jour un patient")
    print("4. Supprimer un patient")
    print("5. Ajouter un rendez-vous")
    print("6. Afficher les rendez-vous")
    print("7. Mettre à jour un rendez-vous")
    print("8. Supprimer un rendez-vous")
    print("9. Quitter")

    choix = input("Choisissez une option (1-9): ")

    if choix == "1":
        nom = input("Nom du patient : ")
        prenom = input("Prénom du patient : ")
        date_naissance = input("Date de naissance (JJ/MM/AAAA) : ")
        while not verifier_date(date_naissance):
            date_naissance = input("Date de naissance (JJ/MM/AAAA) : ")
        adresse = input("Adresse du patient : ")
        numero_telephone = input("Numéro de téléphone du patient : ")
        email = input("Email du patient : ")
        ajouter_patient(nom, prenom, date_naissance, adresse, numero_telephone, email)

    elif choix == "2":
        print("Liste des patients :")
        afficher_patients()

    elif choix == "3":
        id = input("ID du patient à mettre à jour : ")
        
        # Récupérer le patient existant pour afficher les informations actuelles
        patient_actuel = patients_collection.find_one({"_id": int(id)})
        
        if patient_actuel:
            print(f"Modification des informations pour le patient ID {id}. Laissez vide pour ne pas modifier le champ.")

            nom = input(f"Nom [{patient_actuel.get('nom')}] : ") or patient_actuel.get('nom')
            prenom = input(f"Prénom [{patient_actuel.get('prenom')}] : ") or patient_actuel.get('prenom')
            
            date_naissance = input(f"Date de naissance (JJ/MM/AAAA) [{patient_actuel.get('date_naissance')}] : ")
            while date_naissance and not verifier_date(date_naissance):
                date_naissance = input("Date de naissance invalide, veuillez entrer une date valide (JJ/MM/AAAA) : ")
            date_naissance = date_naissance or patient_actuel.get('date_naissance')
            
            adresse = input(f"Adresse [{patient_actuel.get('adresse')}] : ") or patient_actuel.get('adresse')
            numero_telephone = input(f"Numéro de téléphone [{patient_actuel.get('num_tel')}] : ") or patient_actuel.get('num_tel')
            email = input(f"Email [{patient_actuel.get('email')}] : ") or patient_actuel.get('email')

            mettre_a_jour_patient(id, nom, prenom, date_naissance, adresse, numero_telephone, email)
        else:
            print(f"Aucun patient trouvé avec l'ID {id}.")


    elif choix == "4":
        id = int(input("ID du patient à supprimer : "))
        supprimer_patient(id)

    elif choix == "5":
        patient_id = input("ID du patient : ")
        date_rdv = input("Date du rendez-vous (JJ/MM/AAAA) : ")
        heure_rdv = input("Heure du rendez-vous (HH:MM) : ")
        motif = input("Motif du rendez-vous : ")
        ajouter_rendezvous(patient_id, date_rdv, heure_rdv, motif)

    elif choix == "6":
        print("Liste des rendez-vous :")
        afficher_rendezvous()

    elif choix == "7":
        rdv_id = input("ID du rendez-vous à mettre à jour : ")

        # Vérifier si l'ID existe dans la base de données
        rendezvous = rdv_collection.find_one({"id_rdv": int(rdv_id)})
        
        if rendezvous:
            # Si le rendez-vous existe, demander les nouvelles informations
            nouvelle_date = input("Nouvelle date (JJ/MM/AAAA) : ")
            nouvelle_heure = input("Nouvelle heure (HH:MM) : ")
            mettre_a_jour_rendezvous(rdv_id, nouvelle_date, nouvelle_heure)
        else:
            # Si aucun rendez-vous n'a été trouvé avec cet id_rdv
            print(f"Rendez-vous avec l'ID {rdv_id} non trouvé.")

    elif choix == "8":
        rdv_id = input("ID du rendez-vous à supprimer : ")
        supprimer_rendezvous(rdv_id)

    elif choix == "9":
        print("Au revoir!")
        break

    else:
        print("Choix invalide. Veuillez réessayer.")
