# Benchmark
Benchmark between suggester-lunatic vs melauto-35d2

L'idée est de comparer les deux navigations sur liste à partir des saisies utilisateurs

Pour chaque code trouvé (saisie utilisateur -> code la pcs2020 trouvé) avec Melauto, on vérifie si le suggester propose dans la liste des échos proposés le même item.

Test 1 : suggester lunatic simple avant modification

Test 2 : suggester lunatic après modification

## Suggester-Lunatic on Stromae

https://stromae-90-01z.dev.insee.io/questionnaire/90-01z/unite-enquetee/11

Scénario : 
- accès au questionnaire de l'UE 11
- retour à la première page
- réponse à la question sur le sexe
- reponse à la question suggester avec la saisie utilisateur
- récupération de la liste des réponses proposées par le suggester
- vérification si le code trouvé par Melauto est dans la liste

## Données

XX saisies utilisateurs avec match

