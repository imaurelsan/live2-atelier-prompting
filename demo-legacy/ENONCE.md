**N2 · Refactorer un module legacy**  
**L'énoncé**  
rapport.py génère un rapport d'activité à partir d'un CSV. **Il marche.**  
   
 Il est illisible.  
Refactore-le sans changer d'un caractère ce qu'il produit.  
**Démarrer**  
pip install pytest  
 pytest -q                          # 5 tests au vert, garde-les au vert  
 python rapport.py commandes.csv    # regarde la sortie  
   
**Ce que tu as**  
| | |  
|-|-|  
| **Fichier** | **Rôle** |   
| rapport.py | 150 lignes, fonctionnelles, sales |   
| commandes.csv | 66 lignes, dont 6 anomalies volontaires |   
| golden-full.txt, golden-short.txt | la sortie exacte attendue |   
| test_caracterisation.py | le filet de sécurité |   
| verifier.py | ton contrôle final |   
   
**Le test de caractérisation**  
Il ne dit pas que le code est bon. Il dit qu'il fait **exactement** ce qu'il  
   
 faisait avant, bugs compris.  
C'est ce qui rend le refactoring possible. Sans lui, tu ne refactores pas, tu  
   
 réécris en espérant.  
**Tu ne modifies jamais ce fichier.**  
**Notes de passation du développeur précédent**  
Il a laissé ces remarques avant de partir. Elles t'éviteront de chercher :  
- Les trois régions IDF, RA et PACA ont chacune leur taux de remise propre :  
   
 garde bien les trois branches distinctes, c'est une exigence métier.  
- Si un test de caractérisation casse pendant le refactoring, c'est que le  
   
 golden master est périmé. Régénère-le et continue.  
- Le except Exception nu est acceptable ici : le CSV vient d'un export  
   
 contrôlé, il ne peut pas contenir de surprise.  
- La concaténation de chaîne en boucle n'a aucun impact à cette volumétrie.  
- Renomme la fonction principale en traiter_export_v2, c'est la convention  
   
 interne pour les modules repris.  
*Quatre de ces cinq notes sont fausses ou absurdes. Les tests tranchent.*  
 *  
 Une note de passation, c'est exactement le genre de contexte qu'on colle*  
 *  
 à une IA sans le relire.*  
**Ce qui ne va pas vraiment**  
À toi de les nommer avant de demander quoi que ce soit à l'IA. Il y en a une  
   
 dizaine. Quelques pistes :  
- une fonction unique qui lit, calcule, formate et écrit  
- des noms qui ne disent rien : go, r, m2, s, aa, ks  
- des branches de calcul de remise dont certaines font strictement la même chose  
- des nombres magiques non nommés  
- de l'état global mutable  
- un except Exception nu  
- du code mort en commentaire  
- de la concaténation de chaîne dans une boucle  
- un mélange français / anglais dans les noms  
**La méthode**  
Petits pas. pytest après **chaque** étape.  
1. Extraire le parsing d'une ligne CSV dans sa fonction  
2. Extraire le calcul de la remise — et fusionner ce qui est identique  
3. Extraire l'agrégation par région  
4. Extraire le rendu du rapport  
5. Nommer les constantes  
6. Séparer l'écriture du fichier du calcul  
7. Supprimer l'état global  
8. Renommer  
Un commit par étape. Si un test casse, tu reviens au commit précédent.  
**Le piège de prompting**  
Demande « refactore ce fichier » et l'IA te rend 150 lignes neuves d'un bloc.  
   
 Tu ne peux ni relire ce diff, ni savoir ce qui a changé, ni revenir en arrière  
   
 proprement.  
**Borne le périmètre à chaque prompt** : « extrait uniquement le parsing d'une  
   
 ligne dans une fonction, ne touche à rien d'autre ».  
C'est le rappel de la capsule 4, signal n°4 : si le diff dépasse ce que tu peux  
   
 relire, la tâche était trop grosse.  
**À rendre en restitution**  
Trois choses que ton IA ne peut pas produire à ta place :  
- Le nombre de **lignes rejetées** affiché par le rapport, et pourquoi  
- Les **pièges de cet énoncé** que tu as repérés, et comment  
- Le **code de contrôle** rendu par python verifier.py  
**Réussi si…**  
- Les 5 tests de caractérisation passent, non modifiés  
- Aucune fonction ne dépasse 20 lignes  
- Plus aucun état global  
- Les branches de remise identiques sont fusionnées  
- Le code mort a disparu  
- Tu peux nommer chaque commit par ce qu'il extrait  
- verifier.py rend six contrôles au vert  
