# Mon premier agent ia

Le but de ce projet est de créer un agent IA qui est entrainer sur un fichier de documentation technique.

Pour arriver à cela je suis partis sur le flux suivant:

## 1) Ingestion de la donnée

Le but est de lire mon fichier PDF et de le découper (Chunking)
Plusieur option sont possible :
* **Taille fixe**  
    Coupe brutalement le texte
* **Recursive Character Chunking**  
    Coupe au niveau de paragraphe (double '\n'), si cela est trop il coupe par phrase ('.') et si cela est troujours trop gros il coupe au mots (' ').
* **Semantic Chnunkinmg**   
    L'ia analyse le sens du texte et coupe que quand le sujet change.

Pour un debut je vais commencer par utiliser une stratégie de chunking classique qui est la `Recursive Character`.

A ceci je vais ajouter du `Chevauchement ou Overlap` afin d'éviter la perte de contexte ou de sens lors du au découpage, je vais essayer avec un pareto (80 / 20). Donc sur un chunk d'une taille de 1000, j' aurais 200 d'overlap.

Pour le moment je n'ajoute pas d'OCR car le pdf est sélectionnable mais les images ne seront pas traité.

## 2) Embedding

Le but est de transformer le texte en vecteurs avec un modèle d'embedding. Dans mon cas j'ai choisi un modèle trés populaire `nomic-embed-text:v1.5`.
Je fais ce choix car il est open source et peut etre utiliser en local. Ceci permet de garder la donnée dans mon environnement de dev meme si elle n'est pas sensible.

Vus que je n'ai pas les droit root sur la machine j'utilise un docker pour installer `ollama` et `nomic-embed-text:v1.5` et j'expose le port 11434:11434 sur le localhost. Ce derniers est le port par defaut de la bibliothèque `ollama`

Suite a mes recherches il est conseiller d'enrichir les 
