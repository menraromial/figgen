# FigGen - Scientific Figure Generator

**Application web professionnelle 100% Python pour la génération de graphiques scientifiques de haute qualité.**

## Fonctionnalités

- **Multi-format**: CSV, JSON, YAML, Excel, Parquet
-  **Auto-détection**: Types de colonnes, séries temporelles, données manquantes
- **10+ types de graphiques**: Courbes, scatter, barres, histogrammes, boxplots, heatmaps...
- **Thèmes publication**: Nature, Science, IEEE, Modern Dark, Minimal...
- **Code reproductible**: Scripts Python Plotly & Matplotlib générés automatiquement
- **Export HD**: PNG, SVG, PDF jusqu'à 600 DPI

## Installation

```bash
# Cloner ou naviguer vers le projet
cd figgen

# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

L'application sera accessible à l'adresse `http://localhost:8501`

## Utilisation

1. **Chargez vos données** via drag & drop ou en cliquant sur le bouton d'upload
2. **Explorez** les colonnes détectées automatiquement (numériques, catégorielles, temporelles)
3. **Configurez** votre graphique:
   - Sélectionnez le type de graphique
   - Mappez les colonnes sur les axes
   - Choisissez un thème (Nature, Science, IEEE...)
   - Personnalisez titres, labels et styles
4. **Prévisualisez** en temps réel (Plotly interactif ou Matplotlib publication)
5. **Exportez**:
   - Image: PNG, SVG, PDF haute résolution
   - Configuration: JSON ou YAML pour réutilisation
   - Code: Script Python reproductible

## Architecture

```
figgen/
├── app.py                    # Application Streamlit principale
├── requirements.txt          # Dépendances Python
├── config/
│   └── default_themes.yaml   # Configuration des thèmes
├── core/
│   ├── data_loader.py        # Chargement multi-format
│   ├── data_analyzer.py      # Analyse automatique
│   └── models.py             # Modèles Pydantic (ChartConfig, etc.)
├── viz/
│   ├── viz_engine.py         # Moteur Plotly/Matplotlib
│   └── themes.py             # Thèmes publication-ready
├── codegen/
│   └── code_generator.py     # Génération de scripts Python
├── components/
│   ├── file_uploader.py      # Upload drag & drop
│   ├── data_explorer.py      # Exploration des données
│   ├── chart_config.py       # Configuration graphique
│   ├── chart_preview.py      # Aperçu temps réel
│   ├── export_panel.py       # Options d'export
│   └── code_viewer.py        # Affichage du code généré
└── sample_data/
    └── sample.csv            # Données de démonstration
```

## 🛠️ Technologies

| Composant | Technologie |
|-----------|-------------|
| Interface | Streamlit |
| Données | Pandas |
| Visualisation | Plotly, Matplotlib, Seaborn |
| Configuration | Pydantic |
| Code Generation | Jinja2 |

## Types de graphiques supportés

- Courbes (Line)
- ⚬ Nuage de points (Scatter)
-  Barres (Bar)
-  Histogramme
-  Box plot
-  Violin plot
-  Heatmap
-  Aires (Area)
-  Camembert (Pie)
-  Bulles (Bubble)

##  Licence

MIT License - Libre d'utilisation pour la recherche et les publications scientifiques.
