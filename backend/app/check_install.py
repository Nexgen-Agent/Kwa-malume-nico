import importlib.util
import sys

required_packages = [
    'litestar', 'sqlalchemy', 'aiosqlite', 'asyncpg', 'authlib',
    'bcrypt', 'python_dotenv', 'hypercorn', 'uvicorn', 
    'email_validator', 'psutil', 'structlog', 'pytest'
]

print("Checking package installations...")
for package in required_packages:
    try:
        spec = importlib.util.find_spec(package)
        if spec is not None:
            print(f"✅ {package}")
        else:
            print(f"❌ {package} - NOT FOUND")
    except Exception as e:
        print(f"❌ {package} - ERROR: {e}")

print("\nPython version:", sys.version)