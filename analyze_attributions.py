import pandas as pd
from collections import Counter
import re
import nltk
from nltk.tokenize import word_tokenize

nltk.data.path.append('/Users/pierrequemener/nltk_data')
nltk.download('punkt', download_dir='/Users/pierrequemener/nltk_data')

def extract_chemical_entities(attribution):
    entities = [
        'C-H', 'C=C', 'C-O', 'O-H', 'N-H', 'C-N', 'C≡C', 'C≡N', 'C-S', 'S-H', 'P-O', 
        'P=O', 'N≡N', 'glucose', 'phenylalanine', 'water', 'methane', 'ethanol', 
        'carbohydrate', 'protein', 'lipid', 'amino acid', 'nucleic acid', 
        'benzene', 'toluene', 'xylene', 'hexane', 'heptane', 'octane', 'nonane', 
        'decane', 'formaldehyde', 'acetaldehyde', 'acetic acid', 'acetone', 
        'benzaldehyde', 'benzyl alcohol', 'glycine', 'alanine', 'valine', 
        'leucine', 'isoleucine', 'serine', 'threonine', 'cysteine', 'methionine', 
        'aspartic acid', 'glutamic acid', 'asparagine', 'glutamine', 'lysine', 
        'arginine', 'histidine', 'phenylalanine', 'tyrosine', 'tryptophan', 'proline',
        'amide', 'ketone', 'aldehyde', 'ester', 'ether', 'halide', 'alkene', 'alkyne',
        'carbonyl', 'hydroxyl', 'amine', 'carboxyl', 'phosphate', 'sulfate',
        'ethyl', 'methyl', 'butyl', 'propyl', 'isopropyl', 'isobutyl', 'sec-butyl',
        'tert-butyl', 'phenyl', 'naphthyl', 'pyridyl', 'furyl', 'thienyl', 
        'hydrogen bond', 'ionic bond', 'covalent bond', 'van der Waals force', 
        'dipole-dipole interaction', 'π-π interaction', 'cation-π interaction',
        'disulfide bond', 'ester linkage', 'glycosidic linkage', 'peptide bond'
    ]
    
    bonds = re.findall(r'C-H|C=C|C-O|O-H|N-H|C-N|C≡C|C≡N|C-S|S-H|P-O|P=O|N≡N|amide|ketone|aldehyde|ester|ether|halide|alkene|alkyne|carbonyl|hydroxyl|amine|carboxyl|phosphate|sulfate|ethyl|methyl|butyl|propyl|isopropyl|isobutyl|sec-butyl|tert-butyl|phenyl|naphthyl|pyridyl|furyl|thienyl|hydrogen bond|ionic bond|covalent bond|van der Waals force|dipole-dipole interaction|π-π interaction|cation-π interaction|disulfide bond|ester linkage|glycosidic linkage|peptide bond', attribution)
    
    tokens = word_tokenize(attribution.lower())
    compounds = [token for token in tokens if token in entities]
    
    return bonds + compounds

def analyze_attributions(csv_file):
    bond_counter = Counter()
    
    # Lire uniquement la colonne 'Attribution' du fichier CSV
    try:
        data = pd.read_csv(csv_file, usecols=['Attribution'])
    except pd.errors.ParserError as e:
        print(f"Error reading {csv_file}: {e}")
        return bond_counter

    # Parcourir chaque attribution pour extraire et compter les entités chimiques
    for attribution in data['Attribution']:
        entities = extract_chemical_entities(attribution)
        bond_counter.update(entities)
    
    return bond_counter

def save_analysis_results(results, output_file):
    # Convertir les résultats en DataFrame pour sauvegarder en CSV
    df = pd.DataFrame(results.items(), columns=['Entity', 'Count'])
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    # Chemin vers le fichier CSV à analyser
    csv_file = 'uploads/bands_data.csv'
    output_file = 'uploads/chemical_entities_analysis.csv'
    
    bond_counter = analyze_attributions(csv_file)
    
    print("Fréquence des entités chimiques :")
    for entity, count in bond_counter.items():
        print(f"{entity}: {count}")
    
    # Sauvegarder les résultats de l'analyse
    save_analysis_results(bond_counter, output_file)
    print(f"Les résultats de l'analyse ont été sauvegardés dans {output_file}")
