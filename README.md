# Mon premier agent ia

Le but de ce projet est de créer un agent IA qui est entraîné sur un fichier de documentation technique.

Pour arriver à cela, je suis parti sur le flux suivant:

## Ingestion de la donné
### 1) Chunking

Le but est de lire mon fichier PDF et de le découper (Chunking)
Plusieurs options sont possible :
* **Taille fixe**  
    Coupe brutalement le texte
* **Recursive Character Chunking**  
    Coupe au niveau de paragraphe (double '\n'), si cela est trop, il coupe par phrase ('.') et si cela est toujours trop gros, il coupe au mot (' ').
* **Semantic Chnunkinmg**
L'IA analyse le sens du texte et coupe que quand le sujet change.

Pour un début, je vais commencer par utiliser une stratégie de chunking classique qui est la `Recursive Character`.

À ceci, je vais ajouter du `Chevauchement ou Overlap` afin d'éviter la perte de contexte ou de sens due au découpage, je vais essayer avec un pareto (80/20). Donc sur un chunk d'une taille de 1000, j'aurais 200 d'overlap.

Pour le moment je n'ajoute pas d'OCR car le PDF est sélectionnable mais les images ne seront pas traitées.

### 2) Embedding

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


### 3) Stockage de la data

Pour le stockage, j'ai choisi Snowflake pour m'exercer sur un outil data/cloud puissant et adapté à ce que je veux réaliser, avec leur type Vector parfait pour le stockage d'embedding.

Pour ceci, j'ai créé un compte sur le site Snowflake afin d'avoir 30 jours d'essais gratui.
Une fois le compte créé, je vais utiliser Snowpark, qui est une bibliothèque permettant de traiter les données directement en python.
J'ai réalisé un script Python pour créer la base de données pour stocker mes chunks enrichis.
Ensuite je crée une fonction qui permet de stocker mes chunks enrichis directement après l'embedding.



L'ingestion de mes données étant finie, je peux commencer à traiter la requête utilisateur.

## Interrogation de la donnée 

### 4) Recherche Utilisateur

Pour cela nous allons récupérer la question de l'utilisateur afin d'appliquer dessus le même processus d'`embedding` que celui de l'`ingestion` de notre fichier.
Une fois la question de l'utilisateur vectorisée, nous allons chercher la `Similarité Cosinus`. Ceci consiste à mesurer l'angle entre le vecteur de la question et le vecteur d'un chunk. 
* L'angle est de 0 ° (cosinus = 1) : les sens sont identiques.
* L'angle est de 90° (cosinus = 0) : aucun rapport entre les sujets.
* Formule mathématique : $$\text{similarity} = \cos(\theta) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|}$$

Une fois cela réalisé, je vais me servir de la méthode `VECTOR_COSINE_SIMILARITY` de `Snowflake` afin de comparer les vecteurs suivant la méthode ci-dessus et d'extraire mon contexte.
Suite à quelque recherche je vais commencer par me limiter a 5 chunck de context.

## Source :

* Ollama : https://docs.ollama.com/
* Langchain : https://docs.langchain.com/
* Snowflake : https://docs.snowflake.com/en/ | https://www.youtube.com/@SnowflakeInc
* Fonctionnement d' un agent IA : https://blog.stephane-robert.info/docs/developper/programmation/python/ia/
