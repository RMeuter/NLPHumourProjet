import os,sys
from dico import Dico
from mots_fr import MOTS
# from grid_dico import DICO

# Crée par Fabien Borel, Hugo Valery et Nicolas Rieul dans le cadre de leur projet ISN 2013
# Cette version non compilée requière évidemment python et son module pyQt
# Ceci est le code principale, mais pour lancer le programme il faut exécuter main.py
# Nécessite aussi dictionnaire.py
# [https://github.com/fabYkun/corrortho/blob/master/engine.py]

# Le code a été modifié afin d'effectuer un recherche aussi sur les mots du dictionnaire français (c.f mots_fr.py)

# L'arborescence contient des matrices de mots, organisés par noeuds : un pour chaque lettre. Chaque noeud est suivit par une ou plusieurs lettres susceptibles de fournir un mot et ainsi de suite
class Arborescence:
    def __init__(self): # structure d'un noeud (et, indeed, de toute l'arborescence, c'est un peu comme du fractal (sisi))
        self.word = None
        self.children = {}

    def insert(self, word): # pour compléter l'arborescence on injecte les mots un par un (voir la boucle for plus bas)
        node = self # node prend les attributs de l'arborescence (self), donc son dictionnaire children{} qui contient tous les noeuds
        for letter in word:
            if letter not in node.children:
                node.children[letter] = Arborescence() # là, on crée un noeud. Quand je disais que c'était fractal, c'est qu'en fait on reprend la même architecture que l'arborescence et qu'on la place dans ce noeud #inception1

            node = node.children[letter] # là on se place dans le noeud de la lettre "définie" par la boucle for letter in word, la variable node "avance" d'un "pas"

        node.word = word # quand on a fini de créer/se placer dans les noeuds, on donne à la variable "word" (qui était définie dans la structure d'une arborescence/noeud) le mot qui vcient d'etre ajouté

# parcours le dictionnaire et le transpose en arborescence
arbre = Arborescence()
for word in Dico:
    arbre.insert(word)

# arbre_word = Arborescence()
for word in MOTS: # parcours les noms commus et le transpose en arborescence
    arbre.insert(word)
# for word in DICO:
#     arbre.insert(word)


def search(arbre, word, maxCost): # la fonction search retourne une liste des mots qui ont une ressemblance inférieur ou égale à maxCost (même principe que Levenshtein)
    currentRow = range(len(word) + 1)
    results = []

    for letter in arbre.children: # là on est parti pour scanner toutes les branches (en commençant par les premiers noeuds) de l'arborescence
        searchRecursive(arbre.children[letter], letter, word, currentRow, results, maxCost) # c'est là que tout se joue

    return results # voila c'est fini... LOL

def searchRecursive(node, letter, word, previousRow, results, maxCost):
    # bien comprendre qu'on est actuellement dans un noeud
    columns = len(word) + 1
    currentRow = [previousRow[0] + 1] # row les chemins, là on avance de 1

    # construit un chemin pour la lettre, avec une colonne pour chaque lettre du mot
    for column in range(1, columns): # calcul théorique de combien nous couterai l'insert/suppr/remplacement d'un caractère par rapport à où on est dans le mot
        insertCost = currentRow[column - 1] + 1
        deleteCost = previousRow[column] + 1

        if word[column - 1] != letter:
            replaceCost = previousRow[column - 1] + 1
        else:
            replaceCost = previousRow[column - 1]

        currentRow.append(min(insertCost, deleteCost, replaceCost)) # on ne garde que la distance théorique la moins grande (puisqu'on ne sait pas vraiment, on veut juste éviter d'aller chercher dans un nouveau noeud si on sait déjà que quoi qu'il arrive on ne pourra pas accepter le mot)

    # si la dernière entrée de la ligne indique que la différence ne peut être supérieure au maximum (maxCost) alors on ajoute le mot
    if currentRow[-1] <= maxCost and node.word != None: # en réalité au premier passage, à part pour la branche "a" ou "y", celle ligne est ignorée et on passe à d'autres noeuds car word n'existe pas
        results.append((node.word, currentRow[-1])) # on ajoute le mot et son coût levenshteinien

    # si une entrée dans la ligne est inférieur au max, alors on cherche récursivement chaque branche du noeud, généralement le cas au début
    if min(currentRow) <= maxCost:
        for letter in node.children: #inception2, on scanne les branches à partir de ce noeud
            searchRecursive(node.children[letter], letter, word, currentRow, results, maxCost)
 
def verification(phrase):
    phrase = phrase.replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "").replace("6", "").replace("7", "").replace("8", "").replace("9", "").replace("0", "").replace("#", "").replace("'", " ").replace('"', " ").replace('-', " ").replace(".", " ").replace(",", " ").replace(":", " ").replace(";", " ").replace("!", " ").replace("?", " ").replace("(", " ").replace(")", " ").replace("/", " ").replace("\\", " ").replace('’', ' ').replace('`', ' ').replace("«", " ").replace("»", " ").replace("_", " ") # enlève un certain nombre de caractères incorrigibles
    phrase = phrase.split() # transforme la phrase en un array de mots
    erreurs = []
    for x in range(len(phrase)):
        if not recherche(phrase[x]):
            # print("NOT IN RECHERCHE : {}".format(phrase[x]))
            erreurs.append(phrase[x])
            # print("IN RECHERCHE : {}".format(phrase[x]))
    return erreurs
 
def recherche(mot):
    mot = mot.lower() # change le mot en minuscule
    if (not mot in Dico) and (not mot in MOTS) and mot != 'c' and mot != 's' and mot != 'j' and mot != 't' and mot != 'y' and mot != 'd' and mot != 'l' and mot != 'n' and mot != 'm' and mot != 'qu':
        return False
    return True
 
def propositions(arbre, erreur, valeurmin):
    results = dict(search(arbre, erreur, valeurmin))
    return results # il faut trier les résultats, ceux qui sont les plus proches de valeurmin = 1 doivent apparaître les premiers

def correction(arbre, phrase, erreurs): # corrige toutes les erreurs arbitrairement
    for x in range(len(erreurs)):
        newmot = ""
        valeurmin = 0
        while not newmot:
            valeurmin += 1
            result = dict(search(arbre, erreurs[x], valeurmin))
            if result:
                newmot = next(iter(result.keys())) # selectionne le premier index du dictionnaire
        phrase = remplacer(phrase, erreurs[x], newmot)
    return phrase

def remplacer(texte, erreur, remplacement): # remplace toutes les erreurs par leur correction
    newremplacement = "" # met une majuscule dans la correction si l'erreur comportait des majuscules
    if len(remplacement) > len(erreur):
        for x in range(len(erreur)):
            if erreur[x].istitle():
                newremplacement = newremplacement + str(remplacement[x]).upper()
            else:
                newremplacement = newremplacement + remplacement[x]
        newremplacement += remplacement[len(erreur):] # sinon il manque des mots
    else:
        for x in range(len(remplacement)):
            if erreur[x].istitle():
                newremplacement = newremplacement + str(remplacement[x]).upper()
            else:
                newremplacement = newremplacement + remplacement[x]
    texte = " "+texte # on ajoute un espace au début pour contourner les conditions suivantes qui sans l'espace ne réctifirait pas le 1er mot
    texte = texte.replace(" "+erreur+" ", " "+newremplacement+" ").replace("'"+erreur+" ", "'"+newremplacement+" ").replace('"'+erreur+" ", '"'+newremplacement+" ").replace("("+erreur+" ", "("+newremplacement+" ").replace("-"+erreur+" ", "-"+newremplacement+" ").replace("_"+erreur+" ", "_"+newremplacement+" ").replace("."+erreur+" ", "."+newremplacement+" ").replace("!"+erreur+" ", "!"+newremplacement+" ").replace("?"+erreur+" ", "?"+newremplacement+" ").replace("'"+erreur+"'", "'"+newremplacement+"'").replace('"'+erreur+'"', '"'+newremplacement+'"').replace('('+erreur+')', '('+newremplacement+')').replace("'"+erreur+"'", "'"+newremplacement+"'").replace(" "+erreur+"'", " "+newremplacement+"'").replace(" "+erreur+'"', " "+newremplacement+'"').replace(" "+erreur+")", " "+newremplacement+")").replace(" "+erreur+"-", " "+newremplacement+"-").replace(" "+erreur+"_", " "+newremplacement+"_") # ces conditions sont nécessaires aux remplacements car un mot juste peut contenir l'erreur !
    return texte[1:] # on retranche tout ce qui est après le premier caractère, donc l'espace mis au début
