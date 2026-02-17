class PropjectError(Exception):
    """Classe de base pour toutes les erreurs de mon application."""
    pass

class ConnexionError(PropjectError):
    """Erreur lors de la connexion."""
    pass

class AuthentificationError(PropjectError):
    """Erreur d'identifiants."""
    pass    