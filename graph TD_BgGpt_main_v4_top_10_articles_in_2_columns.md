```mermaid
graph TD;
    A[Start] --> B[Import modules];
    B --> C[Download NLTK resources];
    C --> D[Define Bulgarian stopwords];
    D --> E[Define Constants];
    E --> F[Ensure Results directory exists];
    F --> G[Setup Database];
    G --> H[Fetch News];
    H --> I[Save HTML];
    I --> J[Parse and Save Soup];
    J --> K[Save Articles to DB];
    K --> L[Save Results];
    L --> M[Get Popular Articles];
    M --> N[Display Articles];
    N --> O[End];
'''