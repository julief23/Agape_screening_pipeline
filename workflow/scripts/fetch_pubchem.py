from pathlib import Path
import urllib.request

url = "https://ftp.ncbi.nlm.nih.gov/pubchem/Compound/Extras/CID-SMILES.gz"

output = Path("data/raw/CID-SMILES.gz")
output.parent.mkdir(parents=True, exist_ok=True)

print("Downloading PubChem CID-SMILES...")

# download to temp file first
tmp_output = output.with_suffix(".gz.tmp")

urllib.request.urlretrieve(url, tmp_output)

# rename only if download completed
tmp_output.rename(output)

print(f"Saved to {output}")