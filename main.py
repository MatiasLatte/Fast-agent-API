from fastapi import FastAPI

app = FastAPI(title="Nassau National Cable AI Assistant")

@app.get("/")
def root():
    return {"message": "AI Assistant API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}