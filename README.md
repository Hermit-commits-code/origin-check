# 🕵️ Origin-Miner

[![Version](https://img.shields.io/badge/version-0.6.0-blue.svg)](https://github.com/youruser/origin-miner)
[![Python](https://img.shields.io/badge/python-3.14+-yellow.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/tests-7%20passed-brightgreen.svg)](tests/)

**Origin-Miner** is a high-performance Git forensic tool designed to detect non-human code contributions. By analyzing commit velocity, file entropy, and semantic intelligence, it flags suspicious "robotic" patterns in project history.

---

## 🚀 Key Features

* **Semantic Intelligence:** Detects AI-signature patterns through documentation-to-logic ratios.
* **Multi-Core Engine:** Parallelized diff analysis using Python's `ProcessPoolExecutor` for lightning-fast audits.
* **Forensic Triage:** Visual terminal tables with color-coded risk assessment.
* **Data Persistence:** Export detailed forensic reports in JSON format for long-term auditing.

## 🛠️ Installation

```bash
# Using uv (recommended)
uv tool install .
