import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# List of NLTK resources to download
resources = [
    'punkt',
    'stopwords',
    'punkt_tab'
]

for resource in resources:
    try:
        nltk.download(resource, quiet=True)
        print(f"Successfully downloaded {resource}")
    except Exception as e:
        print(f"Error downloading {resource}: {e}")

print("NLTK setup complete.")