from igraph import * ### Redemarrer l'env si on veut les graphics des plots
import numpy as np
import os
import re 


def CreateGraphKnowlegde(path, file, nb_word = 15000, penalize = 10):
    """
    Fonction qui prend unn fichier du dumps jeu de mots qui retourne sont graph de connaissance selon
    Params : 
    - path : str, le chemin d'accès au fichier
    - file : str, le nom du fichier
    - nb_word : int, le nombre d'arret voulu dans le graph issus de jeu de mots
    - penalize : int, poids d'arrete accorder au mots les moins associé aux autres (sachant que la dissociation max est de 1 selon les calculs mais augmenter le poids aura une influence sur le shortpath !)
    
    Retourne :
    {"word": int polarité}
    - Le graph (igraph)
    - Une liste contenant : weigth initiale, li
    """
    if file in os.listdir(path):
        
        li, weightsInitial = take_dump(path, file)
        ###### ###### ###### ###### ###### ###### ######  Mise en place du graph : ###### ###### ###### ###### ###### ###### ###### 
        
         ## On pénalise à une arrete égale à trois pour les mots éloignés intervalle : [0 à penalize == 10] (0 mots proche, "penalize" mots éloigné conceptuellement)
        
        
        ### Changement des poids négatifs en positif : 
        """
        TO DO : trier les liaisons par taille de poids on garde que les n ayant la plus forte liaison entre eux comme ça on est sur de la connexité entre nos vertex !
        """
        mi = min(weightsInitial)
        ma = max(weightsInitial)
        weights = [(w - mi)*penalize/(ma - mi)+1  for w in weightsInitial] # On a des valeur de 0 à 10 !

        ###### ###### ###### ###### ###### ###### ######  Id des mots dans les arretes : ###### ###### ###### ###### ###### ###### ###### 
        keys = {}
        edges = []
        for edge in li[:nb_word]:
          if edge[0] not in keys:
            keys[edge[0]] = len(keys)
          if edge[1] not in keys:
            keys[edge[1]] = len(keys)
          edges.append((keys[edge[0]], keys[edge[1]]))

        keys_reversed = {}

        for k, v in keys.items():
          keys_reversed[v] = k
        
        ###### ###### ###### ###### ###### Build graph ###### ###### ###### ###### ###### ###### ###### 
        g = Graph(directed = True)
        g.add_vertices(len(keys))
        g.add_edges(edges)
        g.vs['name'] = [str(keys_reversed[k]) for k in keys_reversed.keys()]
        g.es['weight'] = weights[:nb_word]
        #### Transformation du graph en unideirectionnelle
        g_uni = g.copy()
        g_uni = g_uni.simplify(combine_edges=sum) ## Choix possible mean, etc.. aussi 
        if [i for i in g_uni.degree()] == [i for i in g.degree()]:
          print("ça marche bien")
        g_uni = g_uni.as_undirected()
        if [i for i in g_uni.degree()] < [i for i in g.degree()]:
          ### Ici il faut que g_uni < g car g compte à la fois l'arrete entrante et sortante or g_test non il dis qu'il y en a qu'une !  
          print("ça marche toujour bien")

        g_uni.es["weight"] = weights[:nb_word]
        
        print("\n\n", g_uni.summary(verbosity=1)[:1000])
        
        g_uni, topicListe = clusteringGraph(g_uni)
        
        return g_uni, (weights, weightsInitial, li), topicListe
        
    else :
        print("Revois ton arborescence le fichier n'existe pas, gros blaireau !")

    

def clusteringGraph(g_cluster):
    """
    Création de cluster de communauté selon l'algorithme walktrap
    """
    
    cluster = g_cluster.community_walktrap()
    nb_clusters = cluster.optimal_count
    clustering = cluster.as_clustering(nb_clusters)
    g_cluster.vs["cluster"] = clustering.membership
    print("il y a :", nb_clusters, " cluster")
    
    ### Nommage des clusters de thèmes
    listMaxDegree = []
    for i in clustering :
        idx = np.array(g_cluster.subgraph(i).degree()).argmax() ## Cherche l'argmax du sommet ayant le plus de degre dans le sous graph
        listMaxDegree.append(g_cluster.vs[i[idx]].index) ## Ajout de ce sommet dans la liste des mots représentant le cluster
    listMaxDegreeLabel = [g_cluster.vs["name"][idx] for idx in listMaxDegree]

    return g_cluster, listMaxDegreeLabel


def take_dump(path, file):
    pattern = '(.*)(>[1-9]{1,}|\n)'
    li = []
    weightsInitial = []
    with open(path+file, encoding="cp1252", newline="\n") as file:
        for i in range(2000000):
            ## TO DO :
            ## https://stackoverflow.com/questions/53418170/why-does-my-decoded-windows-1252-string-show-up-as-a-unicode-value-in-a-dictiona 
            ## Arriver à prendre en compte les mots tels que : 
            ## - Henri Coand&#259;
            ## Le problème est le ";" qui ne permet pas de segmenter le csv facilement...
            ## Jouer avec l'encodage ? ou transformer par un replace toutes les valeurs &#259; par le char voulu ? 
            ## Fonction possible replace

            st = file.readline().split(";")
            if len(st)==4 and st[2].lstrip('-').isdigit():
                ########################## CLeaning ##########################
                if re.search(pattern, st[0], re.IGNORECASE) :
                    li.append([re.search(pattern, st[0], re.IGNORECASE).group(1), st[1]])
                elif re.search(pattern, st[1], re.IGNORECASE):
                    li.append([st[0], re.search(pattern, st[1], re.IGNORECASE).group(1)])
                else :
                    li.append([st[0], st[1]]) 
                weightsInitial.append(int(st[2]))

        print("\n\nliste de liaison : ", li[0:10])
        print("\n\nPoids des liaisons : ", weightsInitial[0:10])
        print("\n\nNombre de liaison possible :", len(li))
        print("\n\nThere are a bad word in liste ? :", [word for liWord in li for word in liWord if word[0:2] == "\n" or word[-2:] == "\n"])
    return li, weightsInitial