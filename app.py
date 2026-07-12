from src.importa_gastos.main import app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.importa_gastos.main:app", host="0.0.0.0", port=8000)