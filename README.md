# 🧠 Líderes o Puentes: Descifrando el Rol de los Influencers con Análisis de Grafos

**Autores:**  
- Santiago González — [sgonzaleg2@eafit.edu.co](mailto:sgonzaleg2@eafit.edu.co)  
- Paula Andrea Pirela — [papirelar@eafit.edu.co](mailto:papirelar@eafit.edu.co)  
- María del Rosario Castro Mantilla — [mrcastrom@eafit.edu.co](mailto:mrcastrom@eafit.edu.co)

**Programa:** Maestría en Ciencia de los Datos y Analítica  
**Curso:** Minería de Grandes Volúmenes de Información  
**Institución:** Universidad EAFIT — Escuela de Ciencias Aplicadas e Ingeniería  
**Fecha:** 12 de noviembre de 2025  

---

## 🎯 Pregunta de Investigación

> ¿De qué manera los usuarios más influyentes en la red social **LiveJournal**, identificados mediante medidas de centralidad a gran escala como **PageRank** y **Grado**, actúan principalmente como **líderes internos de sus comunidades** o como **nodos puente que enlazan múltiples comunidades**?

---

## 🚀 Objetivos

### Objetivo General
Determinar si los usuarios influyentes en LiveJournal actúan como **líderes internos** dentro de sus comunidades o como **nodos puente** entre comunidades distintas.

### Objetivos Específicos
- Identificar los usuarios más influyentes con métricas de centralidad (PageRank, grado, intermediación) usando **Spark**.  
- Detectar comunidades mediante algoritmos de clustering como **Louvain** o **Label Propagation**.  
- Calcular métricas de rol estructural:  
  - **Within-community degree z-score (z)** → mide liderazgo interno.  
  - **Participation coefficient (P)** → mide función de puente.

---

## 🧩 Metodología

El proyecto se desarrolla en **cuatro fases secuenciales**:

### 1️⃣ Fase 1: Comprensión y Adquisición de Datos
- Definición del problema y exploración del dataset **LiveJournal** (~69M aristas, 4.8M nodos).  
- Verificación de escalabilidad y justificación del uso de herramientas distribuidas.

### 2️⃣ Fase 2: Preparación e I/O Distribuido
- **Dataset almacenado en Amazon S3** para lectura distribuida.  
- Evaluación de librerías (Python, DuckDB, Polars, Spark).  
- Implementación final con **Apache Spark** por su eficiencia en grafos masivos.

### 3️⃣ Fase 3: Modelado de Redes y Métricas
- Cálculo de **PageRank** y **Grado**.  
- Detección de comunidades con **Louvain**.  
- Clasificación de nodos según **z-score** (liderazgo) y **P** (puente).

### 4️⃣ Fase 4: Evaluación y Comunicación
- Clasificación de roles y validación mediante visualización.  
- Presentación de resultados y conclusiones académicas.

---

## 🏗️ Arquitectura del Proyecto

PROYECTO FINAL/
│
├── .venv/ # Entorno virtual local (dependencias)
├── DATA/ # Datos fuente
│ └── soc-LiveJournal1.txt
├── infrastructure/ # Infraestructura como código (Terraform)
│ ├── ec2/ # Instancias EC2 para cómputo
│ └── s3/ # Buckets S3 para almacenamiento
├── RESULTS/ # Resultados de métricas
│ └── Resultados_duckdb.txt
├── scpts/ # Scripts de análisis
│ ├── ex-duckdb/
│ ├── POLARS/
│ ├── PYTHON/
│ └── SPARK/
├── .gitignore
└── requirements.txt


📦 **Repositorio:** [https://github.com/mariadelrosario98/PROYECTOFINAL_MMDS](https://github.com/mariadelrosario98/PROYECTOFINAL_MMDS)

---

## ⚙️ Herramientas Utilizadas

| Herramienta  | Propósito Principal                                  |
|--------------|------------------------------------------------------|
| **Python**   | Procesamiento base y lectura asincrónica (asyncio). |
| **DuckDB**   | Procesamiento analítico single-node.                |
| **Polars**   | Procesamiento vectorizado columnar.                 |
| **Apache Spark** | Cómputo distribuido y análisis de grafos (GraphFrames). |
| **AWS S3**   | Almacenamiento y lectura distribuida.               |
| **Terraform**| Infraestructura reproducible (EC2 + S3).            |

---

## ⏱️ Rendimiento Comparado

| Motor | Tiempo de Ejecución (s) |
|--------|--------------------------|
| Python | **250.93** |
| DuckDB | **315.60** |
| Polars | **418.50** |

Python fue más rápido por la simplicidad del procesamiento; sin embargo, **Spark** se adoptó por su escalabilidad y capacidad de manejar arquitecturas de Big Data.

---

## 📊 Resultados Globales

| Métrica | Valor |
|----------|--------|
| Nodos | 4,847,571 |
| Aristas | 68,993,773 |
| Densidad | 0.00000587 |
| Grado Promedio | 28.7 |
| Cercanía Promedio | 0.143 |
| Modularidad | 0.72 |
| Componentes Conectados | 84,470 |

**Conclusión parcial:** La red exhibe una estructura de **“mundo pequeño”**, con comunidades locales densamente conectadas y alta modularidad.

---

## 🧮 Modelo de Influencia: PageRank

El **PageRank** identifica los nodos que concentran el flujo de atención en la red.  
Valores altos (≈0.0009) indican **líderes de comunidad** o **referencias globales**.  
Los **nodos puente**, aunque menos rankeados, son esenciales para conectar comunidades.

---

## ⚖️ Implicaciones Éticas y Legales

- **Privacidad:** los datos se procesaron de forma anonimizada.  
- **Sesgo Algorítmico:** se validaron los resultados para evitar distorsiones.  
- **Legalidad:** uso bajo licencias de datasets públicos y fines exclusivamente académicos.  
- **Uso Responsable:** los resultados no deben usarse con fines comerciales o de manipulación social.

---

## 💡 Conclusiones

- La estructura de LiveJournal confirma una red altamente modular con líderes locales.  
- Algunos nodos, aunque conectados a miles de usuarios, muestran **bajo retorno**, posiblemente **bots o cuentas de desinformación**.  
- La metodología es aplicable a **marketing digital**, **detección de influenciadores** o **seguridad en redes sociales**.  

---

## 🔮 Trabajo Futuro

- Implementar **clustering espectral** y análisis dinámico temporal.  
- Migrar a un **clúster Spark real (EMR)** para procesamiento paralelo.  
- Integrar librerías GPU como **cuGraph (NVIDIA)**.  
- Extender el análisis hacia **redes sociales contemporáneas**.

---

## 📚 Referencias

- Blondel, V. D. et al. (2008). *Fast unfolding of communities in large networks.*  
- Borgatti, S. P. (2005). *Centrality and network flow.*  
- Freeman, L. C. (1978). *Centrality in social networks conceptual clarification.*  
- Guimerà, R. & Amaral, L. A. N. (2005). *Functional cartography of complex metabolic networks.*  
- Newman, M. E. J. (2006). *Modularity and community structure in networks.*  
- Page, L. et al. (1999). *The PageRank Citation Ranking: Bringing Order to the Web.*  
- Raghavan, U. N. et al. (2007). *Near linear time algorithm to detect community structures in large-scale networks.*  
- Wasserman, S. & Faust, K. (1994). *Social network analysis: Methods and applications.*

---

