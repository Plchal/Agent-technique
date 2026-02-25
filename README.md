# Mon premier agent IA (Work in progress)

Le but de ce projet est de créer un agent IA qui est entraîné sur des fichiers de documentation technique moto.
Ce projet va se dérouler en plusieurs phases :
* **Proof of Concept (POC) [Fini]**
https://github.com/Plchal/Agent-technique/tree/Phase_1_POC
* **Minimum Viable Product (MVP) [En cours]**
* **Industrialisation**

# 1) Proof of concept (POC) 
Pour ce POC, je vais partir sur le flux suivant:

## Ingestion de la donnée :
### 1.1) Chunking

Le but est de lire mon fichier PDF et de le découper (Chunking)
Plusieurs options sont possible :
* **Taille fixe**
    Coupe brutalement le texte
* **Recursive Character Chunking**
    Coupe au niveau de paragraphe (double '\n'), si cela est trop, il coupe par phrase ('.') et si cela est toujours trop gros, il coupe au mot (' ').
* **Semantic Chnunking**
    L'IA analyse le sens du texte et coupe que quand le sujet change.

Pour un début, l'utilisation d'une stratégie de chunking `Recursive Character Chunking` semble un bon choix.

À ceci, je vais ajouter du `Chevauchement ou Overlap` afin d'éviter la perte de contexte ou de sens due au découpage.
Pour le parametrage commencer avec un chunk d'une taille de 1000 et une taille de 200 pour l'overlap.

Pour le moment je n'ajoute pas d'OCR car le PDF est sélectionnable mais les images ne seront pas traitées.

### 1.2) Embedding

Le but est de transformer le texte en vecteurs avec un modèle d'embedding. Dans mon cas, j'ai choisi un modèle très populaire `nomic-embed-text:v1.5`.
Je fais ce choix car il est open source et peut être utilisé en local. Ceci permet de garder la donnée dans mon environnement de dev même si elle n'est pas sensible.

Vu que je n'ai pas les droits root sur la machine, j'utilise un docker pour installer `ollama` et `nomic-embed-text:v1.5` et j'expose le port 11434:11434 sur le localhost. Ce dernier est le port par défaut de la bibliothèque `ollama`.

Suite à mes recherches, il est conseillé d'enrichir les chunks afin d'avoir les données suivantes :
* **Le Content** 
    C'est le texte écrit sous la forme d'une string

* **La Metadata**
    Elle peut contenir à l'origine du texte titre, page, chapitre, l'ordre, le numéro du chunk ou bien le contexte.

* **L'Embedding** 
    La vectorisation du chunk par un modèle d'embedding.


### 1.3) Stockage de la data

Pour le stockage, j'ai choisi Snowflake pour m'exercer sur un outil data/cloud puissant et adapté à ce que je veux réaliser, avec leur type Vector parfait pour le stockage d'embedding.

Pour ceci, j'ai créé un compte sur le site Snowflake afin d'avoir 30 jours d'essais gratuit.
Une fois le compte créé, je vais utiliser Snowpark, qui est une bibliothèque permettant de traiter les données directement en python.
J'ai réalisé un script Python pour créer la base de données pour stocker mes chunks enrichis.
Ensuite je crée une fonction qui permet de stocker mes chunks enrichis directement après l'embedding.



L'ingestion de mes données étant finie, je peux commencer à traiter la requête utilisateur.

## Interrogation de la donnée :

### 1.4) Recherche Utilisateur

Pour cela nous allons récupérer la question de l'utilisateur afin d'appliquer dessus le même processus d'`embedding` que celui de l'`ingestion` de notre fichier.
Une fois la question de l'utilisateur vectorisée, nous allons chercher la `Similarité Cosinus`. Ceci consiste à mesurer l'angle entre le vecteur de la question et le vecteur d'un chunk. 
* L'angle est de 0 ° (cosinus = 1) : les sens sont identiques.
* L'angle est de 90° (cosinus = 0) : aucun rapport entre les sujets.
* Formule mathématique : $$\text{similarity} = \cos(\theta) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|}$$

Une fois cela réalisé, je vais me servir de la méthode `VECTOR_COSINE_SIMILARITY` de `Snowflake` afin de comparer les vecteurs suivant la méthode ci-dessus et d'extraire mon contexte.
Suite à quelques recherches, je vais commencer par me limiter à 5 chunks de contexte.

## 1.5) Création du prompt

Une fois notre contexte extrait, il vient se positionner au sein d'un prompt assez simple ainsi que la question de l'utilisateur : 
```python
f"""
    Tu es un expert mécanique KTM. Réponds UNIQUEMENT à partir du contexte fourni.
    Si l'information n'est pas dans le texte, dis que tu ne sais pas.

    CONTEXTE RÉCUPÉRÉ DE SNOWFLAKE:
    {context}

    QUESTION:
    {question}
"""
```
C'est un premier prompt de test très simple pour voir si concept fonctionne.

## 1.6) Utilisation d'un modèle

Avec `ollama` on peut utiliser différents modèles en local. Pour commencer j'ai choisi Mistral avec son modèle `Mistral-7B`. 
J'ai choisi ce modèle pour les raison suivante :
– La doc étant  en français, celui-ci est performant sur tout pour les mots techniques (cardan, arbre à cames, etc...)
– Le modèle est léger et rapide, sachant qu'il tourne en local sur `CPU` et `RAM`
– Open source.

Je lui envoie le prompt généré auparavant et celui-ci me retourne une réponse.
Pour cela je paramètre le modèle grossièrement avec le code suivant:
```python
    response = ollama.chat(model='mistral', messages=[
            {'role': 'user', 'content': prompt},
        ])
```

## Résultat :
Voici mon test : 
```bash
    python3 ask_my_docs.py "Procédure d'entretien périodique vidange huile moteur et remplacement filtre à huile avec tous les couples de serrage necessaire"
```

J'ai print le contexte extrait afin de voir s'il est cohérent (de plus, étant ancien mécanicien, ceci me permet de vérifier la cohérence) :
```
– Mettre en place un nouveau filtre à huile5.
– Huiler le joint torique du couvercle de filtre à huile. Mettre le
couvercle de filtre à huile6 en place.
– Mettre les vis3 en place et les serrer.
Indications prescrites
Vis du couvercle de
filtre à huile
M6 9 Nm (6,6 lbf ft)
Info
Une trop faible quantité d'huile moteur ou une huile
de basse qualité provoquent une usure prématurée du
moteur.
401955-13
– Retirer le bouchon de remplissage7 et le joint torique et
remplir d'huile moteur.
Huile moteur
Température
ambiante : 0 …
50 °C (32 … 122 °F)
1,5 l (1,6 qt.) Huile moteur
(SAE 15W/50)
(
 p. 120)
Huile moteur
Température
ambiante : −10 …
40 °C (14 … 104 °F)
Huile moteur
(SAE 10W/40)
(
 p. 120)
– Mettre le bouchon de remplissage en place avec son joint
torique et le serrer.
---
– Mettre en place un nouveau filtre à huile5.
– Huiler le joint torique du couvercle de filtre à huile. Mettre le
couvercle de filtre à huile6 en place.
– Mettre les vis3 en place et les serrer.
Indications prescrites
Vis du couvercle de
filtre à huile
M6 9 Nm (6,6 lbf ft)
Info
Une trop faible quantité d'huile moteur ou une huile
de basse qualité provoquent une usure prématurée du
moteur.
401955-13
– Retirer le bouchon de remplissage7 et le joint torique et
remplir d'huile moteur.
Huile moteur
Température
ambiante : 0 …
50 °C (32 … 122 °F)
1,5 l (1,6 qt.) Huile moteur
(SAE 15W/50)
(
 p. 120)
Huile moteur
Température
ambiante : −10 …
40 °C (14 … 104 °F)
Huile moteur
(SAE 10W/40)
(
 p. 120)
– Mettre le bouchon de remplissage en place avec son joint
torique et le serrer.
---
○ ● ● ● ●
Contrôler le bon fonctionnement de l'équipement électrique.
 ○ ● ● ● ●
Remplacer l'huile moteur et remplacer le filtre à huile, nettoyer la crépine.
(
 p. 101)
○ ● ● ● ●
Vérifier les disques de frein. (
 p. 69) ○ ● ● ● ●
Vérifier les plaquettes de frein et la sécurité des plaquettes de frein à l’avant. (
 p. 71) ○ ● ● ● ●
Vérifier les plaquettes de frein et la sécurité des plaquettes de frein à l’arrière.
(
 p. 74)
○ ● ● ● ●
Vérifier l'état et l'étanchéité des durites de frein.
 ○ ● ● ● ●
Vérifier le niveau de liquide de frein à l'avant. (
 p. 69) ○ ● ● ●
Vérifier le niveau de liquide de frein à l'arrière. (
 p. 72) ○ ● ● ●
Vérifier l'état des pneus. (
 p. 80) ○ ● ● ● ●
Vérifier la pression des pneus. (
 p. 82) ○ ● ● ● ●
Vérifier l'étanchéité de l'amortisseur et de la fourche.
 ○ ● ● ● ●
Nettoyer les cache-poussières des bras de fourche. (
 p. 61) ● ●
Vérifier la chaîne, la couronne et le pignon de chaîne. (
 p. 65) ● ● ● ●
Contrôler la tension de la chaîne. (
---
○ ● ● ● ●
Contrôler le bon fonctionnement de l'équipement électrique.
 ○ ● ● ● ●
Remplacer l'huile moteur et remplacer le filtre à huile, nettoyer la crépine.
(
 p. 101)
○ ● ● ● ●
Vérifier les disques de frein. (
 p. 69) ○ ● ● ● ●
Vérifier les plaquettes de frein et la sécurité des plaquettes de frein à l’avant. (
 p. 71) ○ ● ● ● ●
Vérifier les plaquettes de frein et la sécurité des plaquettes de frein à l’arrière.
(
 p. 74)
○ ● ● ● ●
Vérifier l'état et l'étanchéité des durites de frein.
 ○ ● ● ● ●
Vérifier le niveau de liquide de frein à l'avant. (
 p. 69) ○ ● ● ●
Vérifier le niveau de liquide de frein à l'arrière. (
 p. 72) ○ ● ● ●
Vérifier l'état des pneus. (
 p. 80) ○ ● ● ● ●
Vérifier la pression des pneus. (
 p. 82) ○ ● ● ● ●
Vérifier l'étanchéité de l'amortisseur et de la fourche.
 ○ ● ● ● ●
Nettoyer les cache-poussières des bras de fourche. (
 p. 61) ● ●
Vérifier la chaîne, la couronne et le pignon de chaîne. (
 p. 65) ● ● ● ●
Contrôler la tension de la chaîne. (
---
18 TRAVAUX D'ENTRETIEN SUR LE MOTEUR
102
S04689-10
Travail principal
– Placer un récipient approprié sous le moteur.
– Enlever la vis de vidange d'huile1 avec le joint torique.
– Enlever la crépine d'huile2 avec le joint torique.
– Laisser l'huile moteur s'écouler entièrement.
– Nettoyer soigneusement la vis de vidange et la crépine.
– Mettre en place la crépine2 et monter la vis de vidange
d'huile1 avec le joint torique, serrer le tout.
Indications prescrites
Vis de vidange
d'huile
M24x1,5 13 Nm (9,6 lbf ft)
S04690-10
– Retirer les vis3. Enlever le couvercle de filtre à huile4
avec son joint torique.
– Retirer le filtre à huile5 du carter du filtre à huile.
– Laisser l'huile moteur s'écouler entièrement.
– Nettoyer soigneusement les pièces et la surface étanche.
S04691-10
– Mettre en place un nouveau filtre à huile5.
– Huiler le joint torique du couvercle de filtre à huile. Mettre le
couvercle de filtre à huile6 en place.
– Mettre les vis3 en place et les serrer.

```

Une fois le traitement fini, voici ma première réponse :
```
Voici la reponse :
 La procédure d'entretien périodique pour la vidange de l'huile moteur et le remplacement du filtre à huile sur un KTM consiste principalement dans les étapes suivantes :

1. Placer un récipient approprié sous le moteur.
2. Enlever la vis de vidange d'huile (M24x1,5) avec son joint torique.
3. Enlever la crépine d'huile avec son joint torique.
4. Laisser l'huile moteur s'écouler entièrement.
5. Nettoyer soigneusement la vis de vidange et la crépine.
6. Mettre en place une nouvelle crépine d'huile et monter la vis de vidange d'huile avec son joint torique, serrer le tout (13 Nm ou 9,6 lbf ft).
7. Retirer les vis du couvercle de filtre à huile (M6) puis enlever le couvercle de filtre à huile avec son joint torique.
8. Retirer le filtre à huile du carter du filtre à huile et laisser l'huile moteur s'écouler entièrement.
9. Nettoyer soigneusement les pièces et la surface étanche.
10. Mettre en place un nouveau filtre à huile.
11. Huiler le joint torique du couvercle de filtre à huile et mettre le couvercle de filtre à huile en place.
12. Mettre les vis du couvercle de filtre à huile (M6, 9 Nm ou 6,6 lbf ft) et serrer.

```

# 2) Minimum Viable Product (MVP)

Le but de cette phase est de passer de scripts exécutables en local à une application web conteneurisée, capable d'ingérer de nouveaux documents de manière dynamique et d'avoir une interface utilisateur (UI).
Pour ce MV, le flux a été optimisé et automatisé.

## 2.1) Architecture et conteneurisation de base
Mise en place de l'environnement reproductible pour passer outre les contraintes locales.
* Création d'un fichier docker-compose.yml : Pour orchester  tour les services entre eux
* Securisation des identifiants avec l'utilisation d'un fichier d'environnement `.env`

## 2.2) Structuration de la base de donnée:

Restructuration de la base de données afin de stocker différentes documentations techniques de différentes motos et de les questionner précisément.

```
+-----------------------+       +-------------------------+
|      DOCUMENTS        |       |         CHUNKS          |
+-----------------------+       +-------------------------+
| PK  DOC_ID            | <---+ | PK  ID                  |
|     FILE_NAME         |     | | FK  DOC_ID              |
|     BRAND             |     | |     CONTENT             |
|     MODEL             |     +-|     METADATA            |
|     YEAR              |       |     EMBEDDING           |
|     UPLOAD_DATE       |       +-------------------------+
+-----------------------+
```

Cette structuration me permet de répertorier quelle documentation a été ingérée et de le questionner lui précisément en fonction du document choisi avec chaque chunk qui pointe vers le document de provenance grâce à la foreign key.

## 2.3) Orchestration du RAG
Liaison entre la base de données, la requête de l'utilisateur et le modèle d'IA
* Récupération du document a questionné
* Utilisation de LangChain pour formater les requêtes, gérer la Similarité Cosinus dans Snowflake, et injecter le contexte dans le prompt.

* Ajustement du prompt système pour l'agent (basé sur Mistral-7B) afin de structurer les réponses pour une interface graphique plutôt qu'un terminal.

* Suite à quelques tests, le chunking semble trop large. Reprise de celui ci avec un `taille de 600` et un `overlap de 90`.
## 2.4) Transparence et Sources
L'IA ayant tendance à halluciner, l'objectif est de lutter contre en assurant la traçabilité de l'information.
* Modification du backend pour qu'il retourne non seulement la réponse générée, mais aussi les métadonnées (nom du document, numéro de page) associées aux chunks utilisés.

* Bénéfice : l'utilisateur peut auditer la réponse en se référant directement au manuel.
## 2.5) Interface Utilisateur

Développement de l'interface graphique accessible via navigateur  avec localhost sur le port 3000
* remplacement des commandes dans le terminal par une interface covertsationnelle.
* Affichage des sources sous chaque réponse afin de renforcer la confiance dans l'outil et d'aider l'utilisateur

## 2.6) Finalisation, test et Déploiement
* Vérification de la résilience des conteneurs via Docker Compose.
* Consolidation des liens entre le front, le back et la db
* Test de l'interface et de l'application.

# Utilisation :

Créer un fichier `.env` à la racine du projet qui ressemble à ce qui suit.
```.env
SNOWFLAKE_ACCOUNT="Your"
SNOWFLAKE_USER="Your"
SNOWFLAKE_PASSWORD="Your"
SNOWFLAKE_ROLE="Your"
SNOWFLAKE_WAREHOUSE=RAG_WH
SNOWFLAKE_DATABASE=RAG_DB
SNOWFLAKE_SCHEMA=RAG_SCHEMA
UPLOAD_DIRECTORY=./uploads
```

Créer un dossier ollama_data avec la commande suivante `mkdir ollama_data`

Puis lancer le projet avec la commande suivante `docker compose -f docker-compose.yml up -d`
Une fois les services disponibles, ouvrez une page web à l'adresse suivante `http://0.0.0.0:3000/`


# Source :

* Ollama : https://docs.ollama.com/
* Langchain : https://docs.langchain.com/
* Snowflake : https://docs.snowflake.com/en/ | https://www.youtube.com/@SnowflakeInc
* Fonctionnement d' un agent IA : https://blog.stephane-robert.info/docs/developper/programmation/python/ia/
* Docker: https://docs.docker.com/reference/compose-file | https://docs.docker.com/reference