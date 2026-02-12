# 🕵️ Origin-Miner

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/youruser/origin-miner)
[![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)](https://www.python.org/)

**Origin-Miner** is a high-performance Git forensic tool designed to detect non-human code contributions.

---

## 🚀 Key Features

* **Forensic Engine v1.0:** Uses weighted cognitive load, logical complexity, and Shannon entropy to calculate AI probability.
* **Velocity Metrics (LPM):** Tracks Lines Per Minute to detect impossible human typing speeds.
* **Multi-Core Engine:** Parallelized diff analysis for lightning-fast audits on large repositories.
* **Smart Caching:** Persistent SQLite database stores previous audits to avoid redundant computations.

## 📊 Interpreting the Results

| Score Range   | Classification     | Verdict                                |
|:--------------|:-------------------|:---------------------------------------|
| **0% - 25%**  | **Human Logic**    | Standard manual development.           |
| **51% - 75%** | **Suspicious**     | High probability of code injection.    |
| **> 75%**     | **🚨 AI DETECTED** | Statistically impossible human output. |

> **Note on Velocity:** A human typically operates at **10-40 LPM**. Anything consistently over **100 LPM** combined with high complexity is a major red flag.

## 🛠️ Installation

## Clone and Install

```bash
git clone [https://github.com/Hermit-commits-code/origin-check.git](https://github.com/Hermit-commits-code/origin-check.git)
cd origin-check

# Install the tool globally
uv tool install .

# Or run without installing
uv run miner.py --path .
```
