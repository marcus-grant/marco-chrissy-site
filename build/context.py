"""BuildContext for managing build environment state."""


class BuildContext:
    """Context object that tracks build environment state.
    
    Provides build environment information like production vs development mode
    to guide URL generation and other context-sensitive build decisions.
    """

    def __init__(self, production: bool = True):
        """Initialize BuildContext.
        
        Args:
            production: Whether this is a production build (default: True)
                       False indicates development/serve mode
        """
        self.production = production