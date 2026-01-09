# Intaker

A customer-facing tool for chains to upload files onto Blob storage.

## How to run locally

```
# Build & run the container
docker-compose up --build 

# Flask edge
python3 edge.py

# Serve the frontend
python3 -m http.server 8000

# Browse to the frontend
http://localhost:8000/index.html

# Manually upload test files
testdata/*
```
