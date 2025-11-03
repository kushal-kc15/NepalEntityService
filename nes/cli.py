def main():
    """Entry point for api command for production use case."""
    import uvicorn

    uvicorn.run("nes.api.app:app", host="0.0.0.0", port=8000)


def dev():
    import subprocess

    subprocess.run(
        [
            "fastapi",
            "run",
            "--host",
            "localhost",
            "--port",
            "8000",
            "nes/api/app.py",
            "--reload",
        ]
    )


if __name__ == "__main__":
    main()
