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

