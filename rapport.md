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
- [Device Authorization Grant (Device Code Flow)](#device-code)
  - [Quel problème résout-il pour une CLI](#cli)
- [Un VPN ne rend pas anonyme à lui tout seul](#vpn)
  - [L'empreinte de la machine](#empreinte)
  - [Pourquoi un VPN reste utile](#utilite-vpn)
  - [À quoi ça sert si on peut remonter à vous](#remontee)
- [Comment fonctionne un proxy VPN](#proxy-vpn)
  - [Le fonctionnement en tunnel](#tunnel)
  - [Différence entre un proxy et un VPN](#proxy-vs-vpn)
  - [Ce qui se passe sur la machine](#carte-reseau)
- [En quoi Tor anonymise](#tor)
  - [Le circuit à trois nœuds](#circuit)
  - [La machine unique](#machine-unique)
  - [Les limites de Tor](#limites-tor)
  - [Comparaison VPN et Tor](#comparaison)
- [URL-capacité : une URL plus un token](#url-capacite)
  - [L'URL classique](#url-classique)
  - [L'URL-capacité](#url-cle)
  - [Si l'URL-capacité est interceptée](#fuite-capacite)
  - [Que faire si le lien a fuité](#invalider)

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

<a id="device-code"></a>

## Device Authorization Grant (Device Code Flow)

Le Device Authorization Grant (souvent appelé Device Code Flow) est un flux d'authentification OAuth 2.0 spécialement conçu pour les appareils connectés ou les outils en ligne de commande (CLI, Command Line Interface) qui ont des contraintes d'affichage spécifiques.

Il est utilisé pour authentifier un utilisateur sur un appareil qui n'a pas de navigateur web intégré, ou sur lequel la saisie de texte est difficile (comme un terminal de commande, une Smart TV, une console de jeux ou une enceinte connectée).

<a id="cli"></a>

### Quel problème résout-il pour une CLI

Lorsque vous utilisez un outil en ligne de commande dans votre terminal (par exemple `gh` pour GitHub CLI, `aws` pour Amazon Web Services, ou `gcloud` pour Google Cloud), l'outil a besoin d'un jeton d'accès (access token) pour agir en votre nom.

Comme le terminal ne peut pas afficher de manière sécurisée la page de connexion officielle de Google ou GitHub, et que vous ne devez jamais taper votre mot de passe directement dans l'outil tiers, le Device Code Flow déporte la connexion sur un appareil équipé d'un navigateur (votre smartphone ou votre ordinateur).

<a id="vpn"></a>

## Un VPN ne rend pas anonyme à lui tout seul

Un VPN ne rend pas anonyme à lui tout seul, car votre machine possède effectivement une empreinte unique.

Cependant, ce qu'un VPN bloque réellement va plus loin que le changement d'adresse IP. Voici l'explication technique de ce qui est vrai dans cette analyse, et de ce qu'un VPN apporte malgré tout.

<a id="empreinte"></a>

### Là où l'analyse a raison : l'empreinte de la machine

Changer d'adresse IP (ce que fait NordVPN) ne suffit pas pour être anonyme face aux géants du web (Google, Meta, Amazon) ou à des services de pistage avancés, car ils utilisent d'autres méthodes pour identifier votre machine unique :

1. **Le browser fingerprinting (l'empreinte de navigateur).** Même avec l'IP d'un VPN, un site web peut lire la configuration de votre machine : votre système d'exploitation, la version de votre navigateur, vos polices installées, votre résolution d'écran, vos extensions, et même la langue de votre clavier. Cette combinaison est souvent unique au monde, comme une empreinte digitale.
2. **Les cookies et les comptes connectés.** Si vous activez NordVPN mais que vous restez connecté à votre compte Google, Discord ou Amazon, le VPN ne sert à rien pour l'anonymat. Le site sait exactement qui vous êtes, peu importe votre adresse IP.

<a id="utilite-vpn"></a>

### Là où le VPN est utile (pourquoi la machine ne fait pas tout)

Si la machine est unique, pourquoi utilise-t-on quand même un VPN ? Parce que l'adresse IP reste la clé principale utilisée par votre fournisseur d'accès à Internet (FAI) et par la loi pour lier vos actions en ligne à votre identité réelle.

Voici à quoi sert concrètement un VPN.

#### 1. Masquer votre activité à votre FAI (Orange, SFR, Bouygues, Free…)

Sans VPN, votre FAI enregistre l'historique de tous les sites web que vous visitez.

- **Avec le VPN.** Votre trafic est entièrement chiffré dans un tunnel sécurisé. Votre FAI voit uniquement que votre machine est connectée à un serveur NordVPN. Il est incapable de savoir quels sites vous visitez, quelles vidéos vous regardez ou ce que vous téléchargez.

#### 2. Protéger votre identité réelle face aux serveurs distants

Si vous visitez un site sans VPN, ce site enregistre votre adresse IP publique. Cette adresse IP permet de remonter directement à votre box internet, donc à votre nom, votre adresse postale et votre compte bancaire (via une requête judiciaire ou Hadopi/Arcom en France).

- **Avec le VPN.** Le site web voit l'adresse IP du serveur VPN (partagée en même temps par des milliers d'autres utilisateurs). Même si le site web devine que votre machine est unique via le fingerprinting, il ne sait pas qui se cache derrière cette machine physiquement, car l'adresse IP n'est pas la vôtre.

#### 3. Sécuriser les réseaux Wi-Fi publics

Dans un café ou un aéroport, un pirate connecté au même Wi-Fi que vous peut intercepter vos requêtes réseau. Le VPN chiffre tout le trafic sortant de votre machine, rendant l'interception inutile pour le pirate.

<a id="remontee"></a>

### À quoi ça sert si on peut remonter à vous

Pour remonter jusqu'à vous lorsque vous utilisez un VPN, il faut que la justice ou un attaquant force le fournisseur de VPN (comme NordVPN) à donner ses registres (logs) pour savoir quelle IP réelle était connectée à leur serveur à une heure précise. Les gros VPN du marché affirment avoir une politique « no-logs » (ils ne gardent pas ces traces), ce qui coupe le lien entre votre machine et vos actions.

- Le VPN ne vous protège pas du pistage publicitaire (Google vous reconnaîtra toujours via vos cookies et votre navigateur).
- Le VPN vous protège de l'association directe entre votre activité en ligne et votre identité civile / géographique.

<a id="proxy-vpn"></a>

## Comment fonctionne un proxy VPN

Pour bien comprendre comment fonctionne un proxy VPN, il faut d'abord lever une ambiguïté technique : un proxy et un VPN sont deux technologies différentes, mais elles partagent le même principe de base. Quand on parle de « proxy VPN » (ou de proxy tout court), le fonctionnement repose sur le concept de l'intermédiaire.

Voici ce qui se passe entre votre machine et Internet.

<a id="tunnel"></a>

### Le principe de base : le fonctionnement en tunnel

Sans intermédiaire, votre machine se connecte directement au site web (par exemple Netflix ou Google). Le site voit votre adresse IP réelle.

Avec un proxy ou un VPN, un serveur intermédiaire vient s'interposer :

```text
[ Votre machine ] ───▶ [ Serveur proxy / VPN ] ───▶ [ Site web ]
      (IP réelle)             (IP masquée)              (cible)
```

1. **La requête.** Vous tapez une adresse web sur votre machine. Au lieu d'aller directement sur le site, votre requête est envoyée au serveur du proxy/VPN.
2. **Le relais.** Le serveur intermédiaire reçoit votre demande. Il prend votre paquet de données, efface votre adresse IP réelle, et la remplace par la sienne (l'IP du serveur).
3. **La livraison.** Le serveur transmet la requête au site web visé.
4. **Le retour.** Le site web répond au serveur intermédiaire (en pensant que c'est lui qui a formulé la demande), et le serveur vous renvoie la réponse.

Pour le site web cible, votre machine est invisible ; il ne connaît que le serveur intermédiaire.

<a id="proxy-vs-vpn"></a>

### Quelle est la différence entre un proxy et un VPN

C'est là que se joue toute la sécurité. Bien qu'ils masquent tous les deux votre IP de la même manière, ils ne protègent pas vos données de la même façon.

#### 1. Le proxy classique (simple relais)

- **Pas de chiffrement.** Les données circulent en clair entre votre machine et le serveur proxy. Si quelqu'un (votre FAI, un pirate sur le Wi-Fi) intercepte le trafic à ce moment-là, il peut voir ce que vous faites.
- **Niveau applicatif.** Un proxy ne gère généralement que le trafic d'une application spécifique (par exemple, uniquement votre navigateur web ou votre logiciel de téléchargement). Le reste de votre machine continue de naviguer sans protection.

#### 2. Le VPN (tunnel sécurisé et chiffré)

- **Chiffrement total.** Avant même de quitter votre machine, toutes vos données sont encapsulées dans un tunnel chiffré. Personne, pas même votre FAI, ne peut voir le contenu de ce qui circule entre votre machine et le serveur VPN.
- **Niveau système.** Le VPN intercepte 100 % du trafic de votre machine (les sites web, les jeux en ligne, les mises à jour du système, les applications d'arrière-plan).

<a id="carte-reseau"></a>

### Concrètement, que se passe-t-il sur votre machine

Lorsque vous cliquez sur « Connexion » sur un logiciel comme NordVPN :

1. Le logiciel installe une carte réseau virtuelle sur votre système.
2. Il négocie une clé de chiffrement secrète avec le serveur distant (via des protocoles comme OpenVPN ou WireGuard).
3. Dès que vous tentez d'accéder à Internet, la carte virtuelle intercepte les données, les chiffre, et les envoie au serveur.

C'est pour cela que votre FAI voit uniquement que vous envoyez des données cryptées vers une seule et unique adresse : celle du serveur VPN.

<a id="tor"></a>

## En quoi Tor anonymise

Le réseau Tor (The Onion Router, le routeur oignon) est conçu pour détruire l'empreinte qui lie votre identité réelle à votre activité en ligne.

Contrairement à un VPN qui utilise un seul intermédiaire (un seul serveur), Tor fait rebondir votre connexion à travers trois serveurs différents (appelés nœuds) répartis partout dans le monde. De plus, il chiffre vos données par couches successives, comme les couches d'un oignon.

Voici comment le réseau Tor réussit à anonymiser, là où un VPN classique échoue.

<a id="circuit"></a>

### Le fonctionnement du circuit Tor (les 3 couches)

Lorsque vous utilisez le navigateur Tor, votre connexion passe par un circuit obligatoire de 3 nœuds :

```text
[Votre PC] ──(chiffrement ×3)──▶ [Nœud d'entrée] ──(chiffrement ×2)──▶ [Nœud du milieu] ──(chiffrement ×1)──▶ [Nœud de sortie] ──(en clair)──▶ [Site web cible]
```

Pour garantir l'anonymat, aucun serveur dans la chaîne ne sait à la fois d'où vous venez et où vous allez :

1. **Le nœud d'entrée (entry guard).** Ce serveur voit votre adresse IP réelle. En revanche, il ne sait pas quel site vous voulez visiter. Tout ce qu'il sait, c'est qu'il doit passer le paquet chiffré au nœud suivant.
2. **Le nœud du milieu (middle relay).** Ce serveur reçoit le paquet. Il ne sait pas qui vous êtes (il voit l'IP du nœud d'entrée) et ne sait pas où vous allez (il voit l'IP du nœud de sortie). Son seul rôle est de faire le passe-plat.
3. **Le nœud de sortie (exit node).** Ce serveur retire la dernière couche de chiffrement. Il voit le site web de destination (par exemple `wikipedia.org`), mais il n'a aucune idée de qui a demandé cette page, car il ne connaît que l'IP du nœud du milieu.

<a id="machine-unique"></a>

### Comment Tor règle le problème de la machine unique

La machine est unique à cause du browser fingerprinting (langue, résolution d'écran, extensions). Le Tor Browser résout ce problème de manière radicale :

- **Une empreinte identique pour tout le monde.** Le navigateur Tor applique des règles strictes à tous ses utilisateurs. Il bloque les scripts de traçage, n'autorise aucune extension, standardise la taille de la fenêtre et rapporte de fausses informations système aux sites web. Pour un outil de pistage publicitaire, votre machine ressemble à l'identique aux millions d'autres machines qui utilisent Tor. Vous vous fondez dans la foule.
- **Effacement automatique.** Dès que vous fermez Tor, l'intégralité de vos cookies, de votre historique et de vos caches est instantanément supprimée de votre ordinateur.

<a id="limites-tor"></a>

### Les limites de Tor

Tor est l'outil grand public le plus puissant pour l'anonymat, mais il a des contreparties :

- **La lenteur.** Faire rebondir vos données à travers trois pays différents et appliquer trois couches de chiffrement ralentit considérablement la connexion. Oubliez le streaming de vidéos en 4K ou les jeux en ligne.
- **Le nœud de sortie est visible.** Le dernier serveur de la chaîne envoie vos données en clair au site web cible. Si vous vous connectez sur ce site à un compte personnel (comme votre compte Facebook ou votre banque), l'anonymat est brisé : le site saura instantanément qui vous êtes.

<a id="comparaison"></a>

### Comparaison : VPN et Tor

| Critère | VPN classique (ex. NordVPN) | Réseau Tor |
|---|---|---|
| Principe | 1 seul intermédiaire de confiance | 3 intermédiaires qui ne se connaissent pas |
| Confiance | Vous devez faire confiance au VPN (qui peut théoriquement voir vos logs) | Confiance zéro requise (le système empêche l'espionnage) |
| Vitesse | Très rapide (streaming, téléchargement) | Lent (conçu pour la navigation web) |
| Protection de l'empreinte | Faible (ne modifie pas votre navigateur) | Maximale (modifie votre empreinte pour vous rendre anonyme) |

<a id="url-capacite"></a>

## URL-capacité : une URL plus un token

La différence fondamentale entre une URL-capacité (capability URL) et une URL classique réside dans l'autorisation d'accès : une URL classique indique simplement où se trouve une ressource, tandis qu'une URL-capacité sert à la fois d'adresse et de clé d'accès (mot de passe).

<a id="url-classique"></a>

### 1. L'URL classique (adresse simple)

Une URL classique identifie un emplacement sur le web, mais elle n'accorde aucun droit particulier par elle-même.

- **Le principe.** Si la ressource est privée, le fait de connaître l'URL ne suffit pas. Le site web va vous bloquer et vous demander de vous connecter (via un identifiant et un mot de passe).
- **Exemple.** `https://google.com`. Si vous donnez ce lien à un ami, il ne pourra pas voir vos e-mails. S'il clique dessus, Google va lui demander de se connecter à son propre compte.

<a id="url-cle"></a>

### 2. L'URL-capacité (adresse + clé d'accès)

Une URL-capacité contient un jeton secret (un token) directement intégré dans sa structure.

- **Le principe.** Le site web considère que quiconque possède cette URL a le droit de voir la ressource. Il n'y a aucune vérification d'identité ni demande de mot de passe. L'URL est le mot de passe.
- **Exemple.** `https://google.com`. Si vous partagez ce lien Google Docs avec l'option « Tous les utilisateurs disposant du lien peuvent lire », n'importe qui dans le monde pourra ouvrir le document instantanément, sans avoir besoin de compte Google.

<a id="fuite-capacite"></a>

### Si quelqu'un découvre ou intercepte l'URL-capacité

Si quelqu'un découvre ou intercepte votre URL-capacité, les risques sont immédiats et particulièrement élevés car cette URL agit comme un mot de passe sans identifiant.

Voici les risques concrets si cette URL tombe entre de mauvaises mains.

#### 1. L'accès illimité à vos données privées (fuite d'informations)

C'est le risque le plus direct. L'attaquant accède instantanément à la ressource protégée par le lien, sans que le système ne lui demande de mot de passe ni de double authentification (2FA).

- **Si c'est un document (Google Drive, Dropbox).** Il peut lire l'intégralité de vos informations personnelles, professionnelles ou médicales.
- **Si c'est un lien de suivi (colis, commande).** Il peut voir votre nom, prénom, adresse postale complète, numéro de téléphone et le détail de ce que vous avez acheté.
- **Si c'est un lien de connexion automatique (magic link d'e-mail).** Il se connecte directement à votre compte à votre place.

#### 2. La modification ou la destruction de vos fichiers

Si l'URL-capacité que vous avez partagée possède des droits en écriture ou en modification (par exemple, un lien Google Docs configuré sur « Tous ceux qui ont le lien peuvent modifier »), l'intrus peut :

- modifier le contenu pour y insérer de fausses informations ;
- tout effacer définitivement ;
- injecter du code malveillant (comme un lien de phishing ou une faille XSS) dans le document pour piéger les autres personnes légitimes qui ouvriront le lien après lui.

#### 3. La perte totale de contrôle du partage (effet viral)

Une fois qu'une personne malveillante possède l'URL, vous perdez le contrôle de sa diffusion :

- elle peut transférer le lien à d'autres pirates, le publier sur un forum public ou l'envoyer sur les réseaux sociaux ;
- le nombre de personnes accédant à vos données peut exploser en quelques minutes, et vous ne saurez jamais précisément qui a consulté le fichier, car l'accès est anonyme.

#### 4. L'impossibilité de bloquer uniquement le pirate

Dans un système classique (avec compte), si un pirate vole votre mot de passe, vous pouvez simplement bloquer son adresse IP ou supprimer son accès spécifique.

- **Avec une URL-capacité.** Le serveur ne fait pas la différence entre vous et le pirate, car vous utilisez exactement la même clé. Si vous voulez bloquer le pirate, vous devez désactiver complètement le lien, ce qui coupe également l'accès pour vous et pour toutes les personnes légitimes avec qui vous aviez partagé le document.

<a id="invalider"></a>

### Que faire immédiatement si le lien a fuité

1. **Invalidez le lien au plus vite.** Allez sur l'application concernée (Google Drive, OneDrive, etc.) et modifiez les options de partage. Changez « Toute personne disposant du lien » par « Limité aux personnes ajoutées ». Cela rendra l'URL-capacité instantanément inutilisable.
2. **Générez un nouveau lien.** Si vous devez absolument continuer à partager la ressource, créez un nouveau lien (ce qui modifiera le jeton secret à l'intérieur de l'URL).
3. **Surveillez vos comptes.** Si l'URL permettait de se connecter à un service, changez immédiatement le mot de passe principal de ce service et déconnectez toutes les sessions actives.
