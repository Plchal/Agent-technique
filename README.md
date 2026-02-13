# Mon premier agent IA (POC)

Le but de ce projet est de créer un agent IA qui est entraîné sur un fichier de documentation technique.

Pour arriver à cela, je suis parti sur le flux suivant:

## Ingestion de la donné :
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

## Interrogation de la donnée :

### 4) Recherche Utilisateur

Pour cela nous allons récupérer la question de l'utilisateur afin d'appliquer dessus le même processus d'`embedding` que celui de l'`ingestion` de notre fichier.
Une fois la question de l'utilisateur vectorisée, nous allons chercher la `Similarité Cosinus`. Ceci consiste à mesurer l'angle entre le vecteur de la question et le vecteur d'un chunk. 
* L'angle est de 0 ° (cosinus = 1) : les sens sont identiques.
* L'angle est de 90° (cosinus = 0) : aucun rapport entre les sujets.
* Formule mathématique : $$\text{similarity} = \cos(\theta) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|}$$

Une fois cela réalisé, je vais me servir de la méthode `VECTOR_COSINE_SIMILARITY` de `Snowflake` afin de comparer les vecteurs suivant la méthode ci-dessus et d'extraire mon contexte.
Suite à quelque recherche je vais commencer par me limiter a 5 chunck de contexte.

## 5) Création du prompt

Une fois notre contexte extrait il vient se positionner au sein d'un prompt assez simple ainsi que la question de l'utilisateur : 
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

## 6) Utilisation d'un modèle

Avec `ollama` on peux utiliser differents models en local. Pour commencer j' ai choisi mistral avec son modele `Mistral-7B`. 
J'ai choisi ce modèle pour les raison suivante :
    - La doc étant  en français celui ci est performant sur tout pour le mots techniques (cardan, arbre à câme, etc...)
    - Le modele est léger et rapide sachant qu'il tourne en local sur `CPU` et `RAM`
    - Open source

Je lui envoie le prompt générer au par avant et celui si me retourne un reponse.
Pour cela je paramettre le modele grossièrement avec le code suivant:
```python
    response = ollama.chat(model='mistral', messages=[
            {'role': 'user', 'content': prompt},
        ])
```

## Résultat :
Voici mon test : 
```bash
    python3 ask_my_docs.py "Procédure d'entretien périodique vidange huile moteur et remplacement filtre à huile avec tout les couples de serrage necessaire"
```

J' ai print le context extrait afin de voir si il est cohérant (de plus étant ancien mécanicien ceci me permet de virifier la cohérence) :
```bash
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

Une fois le traitement fini voici ma première réponnse :
```bash
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


## Source :

* Ollama : https://docs.ollama.com/
* Langchain : https://docs.langchain.com/
* Snowflake : https://docs.snowflake.com/en/ | https://www.youtube.com/@SnowflakeInc
* Fonctionnement d' un agent IA : https://blog.stephane-robert.info/docs/developper/programmation/python/ia/
