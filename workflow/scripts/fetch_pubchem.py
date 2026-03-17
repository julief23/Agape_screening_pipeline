from pathlib import Path
import urllib.request

url = "https://ftp.ncbi.nlm.nih.gov/pubchem/Compound/Extras/CID-SMILES.gz"

output = Path("data/raw/CID-SMILES.gz")
output.parent.mkdir(parents=True, exist_ok=True)

print("Downloading PubChem CID-SMILES...")

urllib.request.urlretrieve(url, output)

print(f"Saved to {output}")