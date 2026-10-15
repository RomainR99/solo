# Rapport — Token de réinitialisation dans l'URL

Passer un token de réinitialisation de mot de passe directement dans l'URL (par exemple : `https://exemple.com`) est une méthode très courante pour les fonctionnalités de type « Mot de passe oublié ».

Cependant, en cybersécurité, cette approche présente plusieurs inconvénients majeurs pour un seul avantage principal lié à la traçabilité.

## Sommaire

- [L'unique avantage : la simplicité et la traçabilité (logs)](#avantage)
- [Les inconvénients majeurs en cybersécurité](#inconvenients)
  - [1. La fuite via les serveurs et intermédiaires (le problème des logs)](#logs)
  - [2. La fuite via l'en-tête Referer](#referer)
  - [3. L'historique du navigateur et l'épaulement (shoulder surfing)](#historique)
  - [4. Le risque d'indexation par les moteurs de recherche](#indexation)
- [Comment sécuriser cette méthode](#securiser)
- [PKI (infrastructure de gestion de clés)](#pki)
  - [Les 4 composants majeurs](#composants)
  - [Le principe des clés](#cles)
  - [Pourquoi utilise-t-on une PKI](#pourquoi)
  - [PKI publique et PKI privée](#publique-privee)

<a id="avantage"></a>

## L'unique avantage : la simplicité et la traçabilité (logs)

L'avantage principal réside dans la facilité de mise en œuvre et le suivi technique :

- **Génération automatique de logs applicatifs.** Les serveurs web (comme Nginx ou Apache) enregistrent par défaut l'intégralité des URL demandées dans leurs fichiers de logs (`access.log`). Si un utilisateur signale un problème, l'administrateur peut facilement vérifier dans les logs si l'URL de réinitialisation a bien été cliquée, à quelle heure, et par quelle adresse IP.
- **Simplicité d'utilisation.** Pour l'utilisateur, un simple clic sur le lien reçu par e-mail suffit. Il n'a pas besoin de copier-coller manuellement un code secret dans un formulaire.

<a id="inconvenients"></a>

## Les inconvénients majeurs en cybersécurité

Le transport de données sensibles (comme un token qui donne accès au compte) dans une URL viole un principe fondamental de la sécurité web. Voici pourquoi.

<a id="logs"></a>

### 1. La fuite via les serveurs et intermédiaires (le problème des logs)

Si les logs du serveur sont un avantage pour le développeur, ils sont un cauchemar pour la sécurité. L'URL contenant le token va être stockée en texte clair à de multiples endroits :

- dans les logs du serveur web de l'entreprise ;
- dans les logs des serveurs proxys ou des reverse-proxys par lesquels passe le trafic.

Si un attaquant parvient à s'introduire sur le serveur de logs (ou si ces logs sont mal protégés), il peut voler les tokens actifs et pirater les comptes avant que les utilisateurs ne cliquent sur le lien.

<a id="referer"></a>

### 2. La fuite via l'en-tête Referer

C'est le risque le plus critique. Lorsque l'utilisateur clique sur le lien dans son e-mail, il arrive sur la page de changement de mot de passe.

- Si cette page web charge des scripts tiers (comme Google Analytics, des boutons de réseaux sociaux, ou des polices externes), le navigateur envoie automatiquement l'URL complète (avec le token) à ces sites tiers via l'en-tête HTTP `Referer`.
- Les gestionnaires de ces services tiers ont alors potentiellement accès au token.

<a id="historique"></a>

### 3. L'historique du navigateur et l'épaulement (shoulder surfing)

- **Historique.** L'URL reste enregistrée dans l'historique de navigation de l'utilisateur. Si quelqu'un d'autre utilise le même ordinateur ou si l'appareil est volé, le token peut être réutilisé (si sa durée de vie n'a pas expiré).
- **Visibilité à l'écran.** Une personne physique située derrière l'utilisateur peut voir ou photographier le token affiché dans la barre d'adresse.

<a id="indexation"></a>

### 4. Le risque d'indexation par les moteurs de recherche

Si la page de réinitialisation du site n'est pas correctement configurée (absence de balise `noindex` ou mauvaise configuration du fichier `robots.txt`), des robots de moteurs de recherche pourraient indexer l'URL complète, la rendant visible publiquement dans les résultats de recherche.

<a id="securiser"></a>

## Comment sécuriser cette méthode

Si vous devez absolument utiliser un token dans l'URL, les bonnes pratiques de sécurité imposent de :

1. **Utiliser une durée de vie ultra-courte.** Le token doit expirer après 10 à 15 minutes maximum.
2. **Usage unique.** Dès que le token a été utilisé (ou même dès que la page a été chargée une fois, selon la politique choisie), il doit être immédiatement invalidé en base de données.
3. **Ajouter la directive Referrer-Policy.** Configurer l'en-tête HTTP `Referrer-Policy: no-referrer` sur la page de réinitialisation pour empêcher le navigateur de partager l'URL avec des outils comme Google Analytics.
4. **La meilleure alternative.** Envoyer un code de validation à 6 chiffres par e-mail. L'utilisateur clique sur un lien générique (`/reset`), puis saisit manuellement son code à l'écran. Le code transite alors de manière sécurisée via le corps d'une requête HTTP POST (invisible dans les URL et les logs).

<a id="pki"></a>

## PKI (infrastructure de gestion de clés)

Une PKI (Public Key Infrastructure), ou infrastructure de gestion de clés (IGC) en français, est le système complet (matériel, logiciels, personnes et règles) qui permet de créer, gérer, distribuer, stocker et révoquer des certificats numériques.

Pour faire une analogie simple : la PKI est l'équivalent de l'administration de l'État qui fabrique et valide les cartes d'identité (les certificats), garantissant ainsi que vous êtes bien la personne que vous prétendez être sur Internet ou au sein d'une entreprise.

<a id="composants"></a>

### Les 4 composants majeurs d'une PKI

Une PKI ne se résume pas à un seul logiciel, elle est composée de plusieurs rôles distincts :

- **L'Autorité de certification (AC ou CA, Certificate Authority).** C'est le cœur de la PKI. C'est elle qui signe numériquement et délivre le certificat. Sa signature prouve que le certificat est authentique. Exemples publics connus : Let's Encrypt, DigiCert.
- **L'Autorité d'enregistrement (AE ou RA, Registration Authority).** C'est le guichet de vérification. Avant que la CA ne crée le certificat, la RA vérifie l'identité du demandeur (s'agit-il du bon domaine web ? de la bonne personne ?). Une fois l'identité validée, elle demande à la CA de générer le certificat.
- **Le répertoire des certificats (et la CRL).** Un annuaire qui stocke les certificats actifs, mais surtout la CRL (Certificate Revocation List), une liste noire des certificats qui ont été révoqués avant leur date d'expiration (par exemple, si une clé privée a été volée).
- **La politique de certification (PC / DPS).** Le cadre juridique et technique qui définit les règles de sécurité de la PKI (qui a le droit d'avoir un certificat, comment sont protégées les clés, etc.).

<a id="cles"></a>

### Comment ça fonctionne en pratique (le principe des clés)

La PKI repose sur la cryptographie asymétrique, qui utilise une paire de clés mathématiquement liées :

1. **La clé privée.** Elle reste secrète (sur votre serveur ou votre ordinateur). Elle sert à prouver votre identité.
2. **La clé publique.** Elle est partagée avec le monde entier à l'intérieur du certificat numérique.

Le scénario type, lorsque vous vous connectez à un site sécurisé en `https://` :

1. Le site envoie son certificat (qui contient sa clé publique) à votre navigateur.
2. Votre navigateur regarde qui a signé ce certificat (la CA).
3. Comme votre ordinateur possède nativement une liste des CA de confiance (les autorités racines), il vérifie la signature de la CA.
4. Si la signature est valide, la connexion est sécurisée.

<a id="pourquoi"></a>

### Pourquoi utilise-t-on une PKI

La PKI apporte trois garanties fondamentales en cybersécurité :

- **L'authentification.** Savoir exactement avec qui vous communiquez (par exemple, être sûr que vous êtes sur le vrai site de votre banque et pas une copie).
- **Le chiffrement.** Protéger les données durant leur transport pour que personne ne puisse les intercepter en clair.
- **La non-répudiation / signature.** Garantir qu'un document ou un message signé numériquement n'a pas été modifié et a bien été envoyé par l'émetteur.

<a id="publique-privee"></a>

### PKI publique et PKI privée (entreprise)

- **PKI publique.** Utilisée pour le web mondial. Les certificats sont reconnus par tous les navigateurs de la planète (par exemple, les certificats SSL/TLS des sites web).
- **PKI privée / interne.** Déployée au sein d'une seule entreprise. Elle sert à sécuriser les accès Wi-Fi de l'entreprise, authentifier les ordinateurs des employés, chiffrer les e-mails internes ou signer des applications internes. Les ordinateurs des employés sont configurés pour lui faire confiance, mais le grand public ne la connaît pas.
