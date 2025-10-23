import kagglehub

# Download latest version
path = kagglehub.dataset_download("diegomariano/tabela-de-livros")

print("Path to dataset files:", path)