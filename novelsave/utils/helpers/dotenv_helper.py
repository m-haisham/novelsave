"""
Wrapper around the optional dependency dotenv

The exported method `load_dotenv` fails silently if
dependency `dotenv` is not available
"""

try:
    import dotenv

    def load_dotenv(*args, **kwargs):
        """Loads environment variables from .env files"""
        dotenv.load_dotenv(*args, **kwargs)

except ImportError:

    def load_dotenv(*args, **kwargs):
        """Loads environment variables from .env files [noimpl]"""
        pass
