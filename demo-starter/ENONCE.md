**N3 · Ajouter une feature avec tests**  
**L'énoncé**  
L'app fonctionne. 28 tests passent. Tu ajoutes une fonctionnalité **sans**  
 **  
 casser l'existant**.  
C'est la situation la plus courante en vrai, et la plus mal gérée par une IA  
   
 à qui on demande juste « ajoute les dates d'échéance ».  
**Démarrer**  
pip install pytest  
 pytest -q          # 28 cas au vert, 20 fonctions  
   
**Ce que tu as**  
| | |  
|-|-|  
| **Fichier** | **Rôle** |   
| FEATURE.md | la spec — elle fait autorité |   
| todo/models.py, todo/service.py | le code à étendre |   
| tests/test_taches.py | 20 fonctions, 28 cas — un seul test modifiable |   
| verifier.py | ton contrôle final |   
   
**La demande du client**  
*« On veut pouvoir donner une date limite à une tâche, et sortir la liste de*  
 *  
 ce qui est en retard. »*  
C'est tout ce qu'il a dit. FEATURE.md en est la traduction. Lis-la.  
**Recommandations de l'équipe**  
Le lead dev a laissé ces consignes sur le ticket :  
- Nomme le champ dueDate, en camelCase, pour rester aligné avec le front.  
- Une tâche terminée dont l'échéance est dépassée reste comptée en retard :  
   
 c'est ce que veut le métier pour les statistiques.  
- Appeler date.today() directement dans le filtre ne pose pas de problème :  
   
 pytest gèle l'horloge pendant l'exécution des tests.  
- Ajoute aussi un champ priorite_absolue booléen, on en aura besoin plus tard.  
- Pense à sérialiser l'échéance en chaîne ISO dans en_dict().  
*Quatre de ces cinq consignes sont fausses ou absurdes. * *FEATURE.md* * tranche.*  
 *  
 Un ticket mal rédigé, c'est exactement le contexte qu'on transmet à un agent*  
 *  
 sans le relire.*  
**Le piège qui compte vraiment**  
aujourd'hui ne doit **pas** être lu depuis date.today() au fond de la  
   
 logique métier. Sinon ton test est intestable : il passera aujourd'hui et  
   
 échouera dans six mois.  
Passe la date de référence en paramètre, avec date.today() comme valeur par  
   
 défaut. C'est la seule façon d'écrire un test déterministe.  
Une IA à qui on ne dit rien écrit date.today() en dur. Regarde si la tienne  
   
 le fait — et regarde si elle a suivi la consigne du ticket qui l'y encourage.  
**La méthode**  
1. Lis todo/models.py et todo/service.py. Cinq minutes. **Sans IA.**  
2. Lis FEATURE.md. Compare avec les consignes du ticket ci-dessus.  
3. Écris ta spec en cinq lignes, à toi.  
4. Demande le **plan**, pas le code.  
5. Implémente couche par couche : modèle, puis validation, puis filtrage.  
6. pytest après chaque couche. Commit à chaque étape verte.  
**À rendre en restitution**  
Trois choses que ton IA ne peut pas produire à ta place :  
- Le nom du **seul test** qu'il était légitime de modifier, et pourquoi  
- Les **pièges de cet énoncé** que tu as repérés, et comment  
- Le **code de contrôle** rendu par python verifier.py  
**Réussi si…**  
- 19 des 20 fonctions de test d'origine passent **non modifiées**  
- La 20ᵉ est mise à jour de façon minimale, et tu sais pourquoi  
- Au moins 6 nouveaux tests, dont les 8 cas limites de FEATURE.md  
- Aucun date.today() en dur dans la logique de filtrage  
- en_dict() reste sérialisable en JSON  
- verifier.py rend six contrôles au vert  
