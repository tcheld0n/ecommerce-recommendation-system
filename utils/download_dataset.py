import kagglehub

# Download latest version
path = kagglehub.dataset_download("muhammadraqim/online-book-store")

print("Path to dataset files:", path)