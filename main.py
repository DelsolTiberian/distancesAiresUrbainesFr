from folium import *
from csv import *
from math import *
import webbrowser as wb
from os import getcwd

#Fonctions importation, formatage et tri de l'information

def importCsv(csvName: str, delimit: str)->list[str]:
    """
    Import informations of a csv file in the code
    Args:
        csvName (str): csv file's name
        delimiter (str): delimiter between the differents columns of the csv file

    Returns:
        elementList[str]: csv file's element list
    """
    elementList = []
    with open("dataSets/"+ csvName, newline="",encoding="utf-8") as csvfile:
        reader = DictReader(csvfile, delimiter=delimit)
        for line in reader:
            elementList.append(dict(line))
    return(elementList)

def triInsertionDict(tab:list[dict], key:str):
    """
       Trie les matrice au format csv.DictReader selon l'ordre alphabétique de l'element des dictionnaire assigne a key
    Args:
        tab (list[dict]): list au format csv.DictReader
        key (str): cle du dictionnaire, donnant acces a l'element de tri
    """
    n=len(tab)
    for i in range(1, n):
        while tab[i][key]<tab[i-1][key] and i>0:
            tab[i], tab[i-1] = tab[i-1], tab[i]
            i-=1

def rechercheDichotomique(val:str, list:list[dict], key:str)->dict:
    """
       recherche un dictionnaire selon un de ses cle dans une matrice au format csv.DictReader, la dichotomie se fait selon l'orde alphabetique'
       Entree: val:  valeur a laquelle l'element assigne a la key du dict recherché est egal
             : key: cle des dictionnaires a laquelle est assigne le critere de recherche
       Sortie: dictionnaire recherché
    """
    a=0
    b=len(list)-1
    while a<b:
        m=(a+b)//2
        if list[m][key]==val:
            return(list[m])
        elif list[m][key]> val:
            b = m-1
        elif list[m][key]< val:
            a = m+1
    return(-1)

def plusProcheDe(list:list[int or float], v:int or float)-> int :
    """
       Donne la position du nombre le plus proche d'une valeur: v dans un tableau: list

    Args:
        list (list[int or float]): tableau de valeurs
        v (int or float): valeur dont on doit trouver le nombre la plus proche dans le tableau

    Returns:
        int: position de l'element le plus proche de v
    """
    ecartMin=abs(list[0]-v)
    pos=0
    for i in range(len(list)):
        if abs(list[i]-v)<ecartMin:
            ecartMin=abs(list[i]-v)
            pos=i
    return(pos)




#Fonctions Calculs de distances et Folium

def distances(ville1:dict, ville2:dict)->float:
    """
       Calule la distance a vol d'oiseau de la distance entre deux villes
       Entree: ville1: dictionnaire comportant les informations sur la premiere ville dont sa longitude et sa latitude
             : ville2: dictionnaire comportant les informations sur la seconde ville dont sa longitude et sa latitude
       Sortie: Distance entre les deux villes
    """
    distance=sqrt((abs(float(ville1['latitude'])-float(ville2['latitude']))*111.319)**2+(abs(float(ville1['longitude'])-float(ville2['longitude']))*111.319)**2)# Conversion la latitude et la longitude en km, puis utilise Pythagore pour avoir la distande a vol d'oiseau
    return distance

def createMap(tabVilles:list[dict]):
    """
       Cree la map à partir d'une liste de differentes villes, les reliant dans l'ordre de la liste

    Args:
        tabVilles (list[dict]): listes de dictionnaires de villes
    """
    #Prend la première et la dernière ville du tableau pour ajuster le zoom
    distance_totale = 0
    for i in range(len(tabVilles) - 1):
        distance_totale += distances(tabVilles[i], tabVilles[i + 1])
    
    if tabVilles[0]['latitude'] > tabVilles[-1]['latitude']:
        lat = float(tabVilles[-1]['latitude']) + distance_totale / 111.319 / 2
    else:
        lat = float(tabVilles[0]['latitude']) + distance_totale / 111.319 / 2
    if tabVilles[0]['longitude'] > tabVilles[-1]['longitude']:
        lon = float(tabVilles[-1]['longitude']) + distance_totale / 111.319 / 2
    else:
        lon = float(tabVilles[0]['longitude']) + distance_totale / 111.319 / 2

    #Definis le zoom
    tabDistances = [50, 100, 500, 1000]
    zooms = [10, 8, 6, 5]
    zoom = zooms[plusProcheDe(tabDistances, distance_totale)]

    carte = Map(location=[lat, lon], zoom_start=zoom)

    # Ajout du texte au centre de la carte avec la distance totale
    distance_text = f'Distance totale: {int(distance_totale)} km'
    icon = DivIcon(
        icon_size=(150, 36),
        icon_anchor=(0, 0),
        html=f'<div style="font-size: 12pt; color: black; background-color: white; padding: 5px;">{distance_text}</div>'
    )
    Marker([lat, lon], icon=icon).add_to(carte)
    
    #Ajout des marqueurs
    for i in range(len(tabVilles)):
        Marker([float(tabVilles[i]['latitude']), float(tabVilles[i]['longitude'])], 
               popup=tabVilles[i]['nom_commune_complet']).add_to(carte)
        if i < len(tabVilles) - 1:
            distance_villes = int(distances(tabVilles[i], tabVilles[i + 1]))
            Marker([float(tabVilles[i]['latitude']), float(tabVilles[i]['longitude'])], 
                   popup=f"{tabVilles[i]['nom_commune_complet']}<br/>Distance de {tabVilles[i + 1]['nom_commune_complet']}: {distance_villes} km").add_to(carte)

    #Ajout des tracés
    coords = [[float(ville['latitude']), float(ville['longitude'])] for ville in tabVilles]
    PolyLine(locations=coords, weight=8, opacity=0.8).add_to(carte)
    
    carte.save('distances.html')





def menu()->int:
    """
       Gere le menu de l'application
       Sortie: reponse: int, reponse de l'utilisateur, choix de navigation
    """
    reponseValable=False
    while reponseValable == False:
        print(2*"\n"+15*' '+ "Carte des distance \n")
        print(5*""+"1- Mesurer la distance entre deux villes")
        print(5*""+"2- Mesurer la distance entre plusieurs villes")
        print(5*""+"3- Quitter")
        reponse=int(input("\n>>>"))
        if 4>reponse>0:
            reponseValable=True
        else:
            print("Votre reponse doit être le chiffre assigné à la fonction choisie!!")
    return(reponse)

def choixVilles(listVilles:list[dict])->dict:
    """
       Deamnde a l'utilisateur de choisir une ville et renvoie la liste de cette ville
    Args:
        listVilles (list[dict]): liste des Villes

    Returns:
        dict: dictionnaire correspondant a la ville recherche
    """
    ville=-1
    while ville== -1:
        print("Entrez le nom de la commune (seules les communes français sont accéptées)")
        nomVille=input('>>>').upper().replace(" ", "").replace("-", "")
        ville=rechercheDichotomique(nomVille, villesFrance, 'nom_commune')
        if ville==-1:
            print("Votre ville n'apparaît pas dans la base de données, ou peut être avez vous mal écrit son nom")
    return(ville)



#EXECUTION APPLICATION

#Importe les fichiers csv et formate les noms de communes
villesFrance=importCsv("communes.csv",";")
for ville in villesFrance:
    ville['nom_commune']= ville['nom_commune'].upper().replace(" ", "").replace("-", "")

#Boucle de l'application
run=True
while run==True:
    choix=menu()
    if choix==3:
        #Quitte l'application
        run=False
    elif choix==1:
        #Calcul des distances entre deux villes et affichage sur la map
        ville1=choixVilles(villesFrance)
        ville2=choixVilles(villesFrance)
        createMap([ville1, ville2])
        #Ouvre l'onglet dans chrome
        wb.open('distances.html')
        #Au cas ou l'utilisateur n'a pas chrome :
        chAbsolue=getcwd()+'/distances.html'
        print('Si vous ne possédez pas Chrome ou que la fenêtre ne s\'est pas ouverte, veuillez rentrer ce lien dans votre navigateur: ' + chAbsolue)

    elif choix== 2:
        #Calcul des distances entre plusieurs villes
        nbVilles=int(input("Combien de villes souhaitez vous? \n>>>"))
        villesChoisies=[]
        for i in range(nbVilles):
            villesChoisies.append(choixVilles(villesFrance))
        createMap(villesChoisies)
                #Ouvre l'onglet dans chrome
        wb.open('distances.html')
        #Au cas ou l'utilisateur n'a pas chrome :
        chAbsolue=getcwd()+'/distances.html'
        print('Si vous ne possédez pas Chrome ou que la fenêtre ne s\'est pas ouverte, veuillez rentrer ce lien dans votre navigateur: ' + chAbsolue)