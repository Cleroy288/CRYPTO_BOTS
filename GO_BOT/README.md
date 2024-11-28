Trading Bot en Go (Backtest uniquement)
Introduction
Bienvenue sur ce projet de backtesting d’un bot de trading codé en Go !
L'objectif principal de ce projet n'est pas de créer un véritable bot de trading, mais plutôt d'explorer et d'apprendre les bases du langage Go à travers l'implémentation d'une logique de stratégie de trading.

Ce bot implémente une stratégie basée sur les bandes EMA (Exponential Moving Averages) avec des périodes de 13 et 38. Il effectue uniquement des backtests sur des données historiques. Le code est loin d’être parfait et n’est pas conçu pour être utilisé en production ou pour trader en direct.
C’est avant tout un exercice pédagogique et une première expérience avec le traitement de données en Python et l’utilisation d’outils d’analyse financière.

Fonctionnalités
Stratégie EMA :

Utilise des bandes EMA pour générer des signaux d’achat et de vente.
EMA rapide (13 périodes) et EMA lente (38 périodes).
Logique de croisement des bandes pour déterminer les opportunités de trading.
Backtest uniquement :

Le bot analyse des données historiques et simule des transactions en fonction de la stratégie.
Modularité :

Chargement des données historiques via un script Python.
Traitement des données avec des outils en Python pour s'assurer de la cohérence des données téléchargées.
Instructions pour l'utilisation

1. Télécharger les données historiques
Avant de pouvoir exécuter le bot, il est nécessaire de télécharger les données nécessaires. Un script Python est fourni dans le dossier DB_S pour faciliter cette étape.
	python DB_S/download_data.py

2. Vérifier les données téléchargées
Le téléchargement peut parfois rencontrer des soucis, et des données corrompues ou incomplètes pourraient être récupérées. Pour cela, un script de vérification et de reconversion est inclus dans le fichier verify_downloaded_data.ipynb.
	Exécutez ce notebook pour corriger et valider les données.

3. Exécuter le bot
Après avoir vérifié les données, compilez le programme Go et exécutez-le avec les données corrigées.
	go build -o trading_bot
	./trading_bot

Remarques
Apprentissage Go : Ce projet a été réalisé pour me permettre d’apprendre le langage Go et explorer des concepts basiques de trading algorithmique.
Traitement de données en Python : C’était ma première expérience de traitement de données en Python, notamment avec des fichiers volumineux. Le script peut être amélioré, mais il permet de traiter les données nécessaires pour le bot.
Limitations :
Le bot ne vise pas à être un produit sérieux ou performant.
Les résultats sont uniquement des simulations et doivent être pris avec beaucoup de recul.
Améliorations possibles
Intégrer d'autres indicateurs pour compléter la stratégie (ex : RSI, MACD).
Optimiser le traitement des données pour des périodes plus longues ou des intervalles plus courts.
Ajouter une visualisation des résultats (exemple : profit dans le temps, drawdowns).
Contribution
Si vous avez des suggestions ou des idées d'amélioration, n’hésitez pas à les partager ou à soumettre des pull requests.
Et si grâce à ce bot, vous parvenez à créer un super bot de trading qui fait des millions par an, pensez à m’en envoyer une copie ! 😉

Conclusion
Ce bot est un projet simple et imparfait, mais il m’a permis d’apprendre beaucoup sur le Go, le traitement de données et les stratégies de trading.
Amusez-vous avec le code, explorez-le, et surtout, ne le prenez pas trop au sérieux !

Bon backtest ! 🚀