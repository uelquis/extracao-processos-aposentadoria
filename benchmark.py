import cProfile
from src.main import app

if __name__ == "__main__":
    
    cProfile.run("app()", sort="cumtime", filename="benchmark.prof")