import numpy as np


def pathBetweenTwoWord(wordStart, wordEnd, g_uni, listMaxDegreeLabel):
    """
    Return None si y'as pas les mots wordStart, wordEnd ou si la distance entre les mots est infinis (pas trouver par le dijktra) sinon le nombre de thème différents, la liste des thèmes et la liste de mots qu'il faut pour passer entre les deux mots 
    """
    Mot = [wordStart, wordEnd] 
    a, b = g_uni.vs.find(name= Mot[0]), g_uni.vs.find(name= Mot[1])
    if a and b :
        got = g_uni.get_shortest_paths(a.index, to=b.index, weights="weight")
        dist = g_uni.shortest_paths(source = a.index, target=b.index, weights="weight")

        listName = [g_uni.vs["name"][i] for i in got[0]]
        print(listName)

        print("\n Path pour aller à target :", got,"\n Les distances associés:", dist, "\n")
        print("Si la distance est inf alors l'algo n'a pas trouver de liaison :", dist[0][0])
        if dist[0][0] != np.inf:
            unique_cluster = np.unique([g_uni.vs["cluster"][i] for i in got[0]])
            return unique_cluster.size, [listMaxDegreeLabel[theme] for theme in unique_cluster], listName

if __name__ == "__main__":
    pass