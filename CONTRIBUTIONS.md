# Guide de Contribution

    Merci de l'intérêt que vous portez à contribuer au projet de Portfolio Artistique ! Toute contribution, qu'il s'agisse de rapports de bugs, de suggestions de fonctionnalités ou de code, est la bienvenue et appréciée.

## Code de Conduite

    Ce projet et tous ceux qui y participent sont régis par notre [Code de Conduite](CODE_OF_CONDUCT.md) (à créer si nécessaire). En participant, vous vous engagez à respecter ce code. Veuillez signaler tout comportement inacceptable à [komythomas@gmail.com].

## Comment Contribuer ?

    Il existe plusieurs façons de contribuer :

### 1. Rapporter des Bugs

    *   **Vérifiez les Issues Existantes:** Avant de soumettre un nouveau rapport de bug, veuillez vérifier s'il n'existe pas déjà un rapport similaire dans la section [Issues](https://github.com/komythomas/artportfolio/issues) du dépôt GitHub.
    *   **Ouvrir une Nouvelle Issue:** Si le bug n'est pas déjà signalé, ouvrez une nouvelle issue. Assurez-vous d'inclure :
        *   Un titre clair et descriptif.
        *   Une description détaillée des étapes pour reproduire le bug.
        *   Le comportement attendu.
        *   Le comportement observé (incluant les messages d'erreur ou captures d'écran si pertinent).
        *   Votre environnement (version du navigateur, système d'exploitation, version de Python, etc.).

### 2. Suggérer des Améliorations ou de Nouvelles Fonctionnalités

    *   **Vérifiez les Issues Existantes:** Regardez si une suggestion similaire n'a pas déjà été faite dans les [Issues](https://github.com/komythomas/artportfolio/issues).
    *   **Ouvrir une Nouvelle Issue:** Si ce n'est pas le cas, ouvrez une nouvelle issue en décrivant clairement :
        *   La fonctionnalité souhaitée ou l'amélioration proposée.
        *   Le problème que cela résoudrait ou la valeur ajoutée.
        *   (Optionnel) Des suggestions sur la manière de l'implémenter.

### 3. Soumettre des Pull Requests (PR)

    Les contributions de code sont les bienvenues !

    1.  **Forker le Dépôt:** Créez une copie (fork) du dépôt principal (`komythomas/artportfolio`) sur votre propre compte GitHub.
    2.  **Cloner votre Fork:** Clonez votre fork sur votre machine locale :
        ```bash
        git clone https://github.com/komythomas/artportfolio.git
        cd artportfolio
        ```
    3.  **Créer une Branche:** Créez une nouvelle branche pour vos modifications. Utilisez un nom descriptif (par exemple, `fix/bug-galerie` ou `feature/ajout-tri-oeuvres`).
        ```bash
        git checkout -b nom-de-votre-branche
        ```
    4.  **Configurer l'Environnement de Développement:** Suivez les instructions de la section "Démarrage Rapide (Local)" du fichier `README.md` pour installer les dépendances et configurer la base de données.
    5.  **Effectuer les Modifications:** Écrivez votre code, corrigez le bug ou implémentez la fonctionnalité.
        *   Respectez le style de code existant.
        *   Ajoutez des tests si pertinent.
        *   Mettez à jour la documentation si nécessaire.
    6.  **Tester vos Modifications:** Assurez-vous que vos changements n'introduisent pas de nouveaux problèmes et que les tests (s'il y en a) passent toujours.
    7.  **Commit vos Changements:** Faites des commits clairs et concis.
        ```bash
        git add .
        git commit -m "Fix: Corrige l'affichage des images dans la galerie"
        # Ou
        git commit -m "Feat: Ajoute la possibilité de trier les œuvres par date"
        ```
    8.  **Pousser vers votre Fork:** Envoyez vos changements vers votre fork sur GitHub.
        ```bash
        git push origin nom-de-votre-branche
        ```
    9.  **Ouvrir une Pull Request:**
        *   Allez sur la page de votre fork sur GitHub.
        *   Cliquez sur "Compare & pull request".
        *   Assurez-vous que la branche de base est `main` (ou la branche principale du dépôt `komythomas/artportfolio`) et que la branche de comparaison est `nom-de-votre-branche` de votre fork.
        *   Donnez un titre clair à votre PR et une description détaillée des changements que vous avez effectués. Liez l'issue correspondante si elle existe (par exemple, `Closes #123`).
        *   Soumettez la Pull Request.

## Processus de Révision

    *   Un mainteneur examinera votre PR. Des commentaires ou des demandes de modifications peuvent être faits.
    *   Une fois approuvée, votre PR sera fusionnée dans la branche principale.

    Merci pour votre contribution !
    ```