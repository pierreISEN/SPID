# Projet SpiDiagMir

Spidiagmir est un projet mené par l'[IRDL](https://www.irdl.fr/) et [DIAFIR](https://diafir.com/). Il a pour but d'appuyer l'activité de ces deux entités dans le domaine du biomédical et de la santé, en repertoriant une très grande quantité de données liés à la spectroscopie infrarouge.

# Spidiagmir-App

Le module d'application est responsable de la visualisation des données extraites par le module d'extraction.

## Installation :

Tout est dans le `requirements.txt` !

Utilisez Python 3**.11**, les autres versions ne sont pas testées.
Je vous conseille de faire appel à quelqu'un familier avec le déploiement de code python pour procéder.

## Utilisation :

Veuillez avoir `spidiagmir_processed.db` dans le dossier courant, et exécutez `app.py` ! L'adresse web pour accéder à l'application sera affichée.

## Mise à jour de la base :

Déplacez le nouveau fichier spidiagmir_export.db dans le dossier de Spidiagmir. La base de données sera alors à jour.

## Informations développeurs :

Le module d'application est très simple, et ne nécessite pas de documentation particulière. Il est basé sur Flask, et utilise Jinja2 pour les templates. `¯\_(ツ)_/¯`
Bonne chance !
