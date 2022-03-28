# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from time import perf_counter

#variable début calcule
tempsDebut = perf_counter()

# url de l'acceuil du site
url = 'https://www.legallais.com'
resultatRequete = requests.get(url)

#catégorie de tout le site
listCategorie = ['batiment','agencement','plomberie','electricite','consommables','outillage','materiels','protection']

#déclaration des listes
listLien = []
listHref = []

#liste comparative des elements de la liste 'listHref'
listCaractere = ['/','1','2','3','4','5','6','7','8','9','0'] 
listSousCategorie = []

#calcul du nombre de produits passés
listEchec = []

#permet de parcourir la liste 'listSousCategorie'
CSV = 0


#récupération des liens et des noms de toutes les sous-catégories
def lienSousCategorie(resultatRequete) :
    if resultatRequete.ok:
        soup = BeautifulSoup(resultatRequete.text, 'lxml')
        #boucle pour traverser toutes les catégories de la liste
        for i in range(len(listCategorie)):
            lis = soup.find_all('li', class_='overlay-menu_family overlay-menu_family--' + listCategorie[i] + '-color')
            for li in lis:
                a = li.find('a')
                #implémentation des liens des sous-catégories dans la liste 'listLien'
                listLien.append(url + a['href'])
                listHref.append(a['href'])
    #récupération des noms de chaque sous-catégories            
    for lien in listHref :
        for lettre in lien :
            for j in listCaractere :
                if j == lettre :
                    lien = lien.replace(lettre, '')
        listSousCategorie.append(lien)
              
#obtention du nombre de pages   
def nbPage(lienCategorie) :
    url = str(lienCategorie)
    resultatRequete = requests.get(url)
    compteurPage = 0
    if resultatRequete.ok :
        soup = BeautifulSoup(resultatRequete.text, 'lxml')
        select = soup.find('select', class_='js-pagination__go')
        for option in select :
            compteurPage = compteurPage + 1
        return(compteurPage + 1)

#récupération de toutes les données des produits      
def recuperationDonnee(listLien, listSousCategorie, CSV) :
    for lienCategorie in listLien :
        listLienProduit = []
        listPrixProduit = []
        compteurProduit = 0
        compteurPage = nbPage(str(lienCategorie) + "?page=1&show=100")
        
        #obtention des prix et des liens des produits de toute une sous-catégorie
        print('Catégorie: ' + '-' + str(listSousCategorie[CSV]) + '-')
        for i in range(1, compteurPage) :
            url = str(lienCategorie) + "?page=" + str(i) + "&show=100"
            resultatRequete = requests.get(url)
            
            #récupération du code html de la page url
            if resultatRequete.ok :
                soup = BeautifulSoup(resultatRequete.text, 'lxml')
                uls = soup.find('ul', class_='js-products-container c-articles-preview c-articles-preview--list o-layout o-layout--small o-layout--stretch')
                
                #parcours de tout le contenu de la balise <ul>
                for ul in uls :
                    divs =  ul.find('div', class_='js-articles-preview c-articles-preview__item')
                    
                    #si la balise <div> avec la 'class' spécifique existe
                    if divs :
                        lien = divs.find('a', class_='c-articles-preview__picture-container')
                        
                        #ajout du lien dans la liste 'listLienProduit'
                        listLienProduit.append(lien['href'])
                        span = divs.find('span', class_='price__amount')
                        
                        #si la balise <span> avec la 'class' spécifique existe
                        if span :
                          
                            #ajout du prix dans la liste 'listPrixProduit'
                            listPrixProduit.append(str(span.get_text().replace(',', '.').replace('€', '') + '€'))
                        else :
                            listPrixProduit.append("Indisponible")      
        tailleListPrixProduit = len(listPrixProduit)
        #récupération et écriture dans le fichier CSV
        with open(str(listSousCategorie[CSV]) + '.csv', 'w') as outf :
          
            #écriture du nom des colonnes dans le fichier CSV
            outf.write("Référence,Titre,Prix,Image,Caractéristique,Description,Fil d'Ariane,PDF" + '\n')
            
            #parcours de chaque articles       
            for i in range(tailleListPrixProduit) :
                compteurProduit = compteurProduit + 1
                listFilArianeProduit = []
                listDocumentation = []
                nombreRef = 0
                resultatRequete = requests.get(str(listLienProduit[i]))
                
                #fonction qui calcule et retourne le nombre de références d'un même produit
                def nombreReference(resultatRequete) :
                    nombreRef = 0
                    if resultatRequete.ok :
                        soup = BeautifulSoup(resultatRequete.text, 'lxml')
                        tbody = soup.find('tbody', class_='js-articles-table-body')
                        if tbody :
                            trs = tbody.find_all('tr')
                            for tr in trs :
                                tds = tr.find_all('td', class_='u-nowrap text-center u-bold js-article-code')
                                for ref in tds :
                                    nombreRef = nombreRef + 1
                    return nombreRef
                  
                #fonction qui permet d'obtenir toutes les références des produits
                def reference(resultatRequete) :
                    if resultatRequete.ok :
                        soup = BeautifulSoup(resultatRequete.text, 'lxml')
                        tbody = soup.find('tbody', class_='js-articles-table-body')
                        if tbody :
                            trs = tbody.find_all('tr')
                            for tr in trs :
                                tds = tr.find_all('td', class_='u-nowrap text-center u-bold js-article-code')
                                for ref in tds :
                                    var = ref.get_text()
                                    url = listLienProduit[i] + '/' + var + '/' + var
                                    result = requests.get(url)
                                    recupDonnee(result)
                            
                #récupération des données
                def recupDonnee(resultatRequete) :
                    if resultatRequete.ok :
                      
                      	#récupération du code html
                        soup = BeautifulSoup(resultatRequete.text, 'lxml')
                        
                        #obtention du titre
                        titre = soup.find('div', class_="product-title u-margin-bottom-small")
                        titreProduit = titre.find('h1')
        
                        #obtention de l'image
                        image = soup.find('div', class_="u-padding-horizontal u-padding-vertical").find('img')
                        sourceImage = image['src']
        
                        #obtention de la description
                        section = soup.find('section', class_='u-1/2@tablet u-1/1 o-layout__item description')
                        divDescription = section.find_all('div', class_='u-margin-bottom-small')
        
                        #obtention de la liste des caractéristiques
                        table = soup.find('table', class_='characteristics u-margin-bottom-tiny')
        
                        #obtention du fil d'Ariane
                        ol = soup.find('ol', class_='c-breadcrumb u-margin-bottom-small u-padding-top-tiny')
                        a = ol.find_all('a') 
              
              					#obtention de la documentation    
                        div = soup.find('div',class_='o-layout u-padding-horizontal')
                        lien = div.find_all('a', class_='c-link u-display-block')
              					
                        for a in ol:
                            filAriane = a.get_text()
                            listFilArianeProduit.append(filAriane)
              
                        for a in lien:
                            href = a['href']
                            listDocumentation.append(href)
                        
                        #insertion de la liste 'listCaractéristique' dans le fichier CSV
                        def affichTab(table) :
                            if table :
                                trs = table.find_all('tr')
                                for tr in trs :
                                    caracteristiqueProduit = tr.th.get_text().replace("'", "'").replace(',', '.') + '= ' + tr.td.get_text().replace("'", "'").replace(',', '.') + ' |'
                                    try:
                                        outf.write(caracteristiqueProduit)
                                    except (AttributeError, UnicodeEncodeError):
                                        listEchec.append("1")
                                        pass
                            else :
                                caracteristiqueProduit = "Pas de caractéristique"
                                outf.write(caracteristiqueProduit)
                            outf.write(',')
                            
                        #insertion du prix dans le fichier CSV
                        def affichlistPrixProduit(i) :
                            if nombreRef == 0 :
                                try:
                                    outf.write(listPrixProduit[i] + ',')
                                except (AttributeError, UnicodeEncodeError) :
                                    listEchec.append("1")
                                    pass
                            else :
                                outf.write('/' + ',')
                            
                        #insertion du lien de l'image dans le fichier CSV
                        def affichImg() :
                            outf.write(sourceImage + ',')
                            
                        #insertion du nom dans le fichier CSV
                        def affichTitre() :
                            try:
                                soup = BeautifulSoup(resultatRequete.text, 'lxml')
                                tbody = soup.find('tbody', class_='js-articles-table-body')
                                if tbody :
                                    trs = tbody.find('tr')
                                    try:
                                        tds = trs.find('td', class_='u-nowrap text-center u-bold js-article-code')
                                        outf.write(str(tds.text) + ',')
                                    except (AttributeError, UnicodeEncodeError):
                                        listEchec.append("1")
                                        pass
                                outf.write(str(titreProduit.get_text()).replace(',', ' ') + ',')
                            except (AttributeError, UnicodeEncodeError) :
                                listEchec.append("1")
                                pass
                        
                        #insertion de la description dans le fichier CSV 
                        def affichDiv(divDescription) :
                            for div in divDescription :
                                if div.h2 :
                                  
                                    #description
                                    description = div.text.replace("'", "'").replace(',', '').replace('Description', '' ) + ' '
                                    try:
                                        outf.write(description)
                                    except (AttributeError, UnicodeEncodeError) :
                                        listEchec.append("1")
                                        pass
                                else :
                                    description = ''
                                    outf.write(description)
                                if div.h3 :
                                  
                                    #gamme
                                    gamme = div.h3.get_text().replace("'", "'").replace(',', ' ').replace('La gamme', '')
                                    try:
                                        outf.write(gamme)
                                    except (AttributeError, UnicodeEncodeError) :
                                        listEchec.append("1")
                                        pass
                                else :
                                    gamme = ''
                                    outf.write(gamme)
                                if div.div :
                                  
                                    #autres informations
                                    autreInfo = div.div.get_text().replace("'", "'").replace(',', ' ')
                                    try:
                                        outf.write(autreInfo)
                                    except (AttributeError, UnicodeEncodeError) :
                                        listEchec.append("1")
                                        pass
                                else :
                                    autreInfo = ''
                                    outf.write(autreInfo)
                            outf.write(',')
                            
                        #insertion du fil d'Ariane du produit dans le fichier CSV
                        def affichFilAriane() :
                            try:
                                outf.write(str(listFilArianeProduit).replace(',','>').replace('[','').replace(']','').replace("'",'')+',')
                            except (AttributeError, UnicodeEncodeError) :
                                listEchec.append("1")
                                pass
                            
                        #insertion des liens PDF dans le fichier CSV
                        def affichPDF() :
                            try:
                                outf.write(str(listDocumentation).replace(',',' | ').replace('[','').replace(']','') + '\n')
                            except (AttributeError, UnicodeEncodeError) :
                                listEchec.append("1")
                                pass
                            
                        #écriture du fichier CSV
                        def ecritureCSV(i, table, divDescription) :
                            affichTitre()
                            affichlistPrixProduit(i)
                            affichImg()
                            affichTab(table)
                            affichDiv(divDescription)
                            affichFilAriane()
                            affichPDF()
                            print(str(compteurProduit))
                            
                        ecritureCSV(i, table, divDescription)
                
                recupDonnee(resultatRequete)
                nombreRef = nombreReference(resultatRequete)
                reference(resultatRequete)
            CSV = CSV + 1
   
lienSousCategorie(resultatRequete)
recuperationDonnee(listLien, listSousCategorie, CSV)
print('Erreur : ' + str(len(listEchec)))

#variable fin 
tempsFin = perf_counter()
#affichage durée du programme
print('La récupération des produits a duré : ' + str(((tempsFin - tempsDebut)/3600)) + 'heures')
  