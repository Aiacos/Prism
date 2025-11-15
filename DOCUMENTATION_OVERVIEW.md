# Prism Pipeline - Documentazione Linux

## 📚 Panoramica Documenti

Questa directory contiene la documentazione completa per il supporto Linux di Prism Pipeline.

---

## 📖 Guide per Utenti

### 🚀 [QUICKSTART.md](QUICKSTART.md) (4.3 KB)
**Per chi**: Utenti che vogliono installare Prism velocemente
**Contenuto**:
- Installazione rapida in 4 passi
- Comandi essenziali
- Primi passi con Prism
- Risoluzione problemi comuni
- **Lingua**: Italiano

### 📘 [INSTALL_LINUX.md](INSTALL_LINUX.md) (8.5 KB)
**Per chi**: Utenti che vogliono una guida dettagliata
**Contenuto**:
- Requisiti di sistema completi
- Installazione dipendenze per ogni distribuzione
- Metodi di installazione (utente vs sistema)
- Integrazione DCC dettagliata
- Configurazione XDG
- Troubleshooting esteso
- **Lingua**: Italiano

---

## 🔧 Guide per Sviluppatori

### 💻 [CLAUDE.md](CLAUDE.md) (13 KB)
**Per chi**: Sviluppatori che vogliono contribuire al progetto
**Contenuto**:
- Onboarding per nuovi sviluppatori
- Architettura del progetto
- Convenzioni di codice
- Struttura file e moduli
- Pattern comuni
- Come estendere Prism

### 🧰 [PlatformUtils_README.md](PlatformUtils_README.md) (5.7 KB)
**Per chi**: Sviluppatori che usano il modulo PlatformUtils
**Contenuto**:
- API reference completa
- Metodi cross-platform
- Esempi d'uso
- XDG compliance
- Desktop file creation
- DCC detection

### 📚 [LINUX_DEVELOPMENT_HISTORY.md](LINUX_DEVELOPMENT_HISTORY.md) (20 KB)
**Per chi**: Sviluppatori interessati alla storia tecnica
**Contenuto**:
- Storia completa dello sviluppo Linux
- Analisi iniziale del codebase
- Decisioni tecniche e rationale
- Fasi di implementazione dettagliate
- Report dei test
- Fix Python 3.14
- Metriche di qualità del codice
- Lessons learned

---

## 📋 Struttura Documentazione

```
Prism/
├── README.md                          # 1.5 KB - Introduzione progetto
├── QUICKSTART.md                      # 4.3 KB - ⭐ Installazione rapida
├── INSTALL_LINUX.md                   # 8.5 KB - ⭐ Guida completa utente
├── CLAUDE.md                          # 13 KB  - Developer onboarding
├── PlatformUtils_README.md            # 5.7 KB - Module reference
└── LINUX_DEVELOPMENT_HISTORY.md       # 20 KB  - Storia tecnica
```

**Totale documentazione**: ~52 KB

---

## 🎯 Quale Documento Leggere?

### Voglio installare Prism velocemente
→ **[QUICKSTART.md](QUICKSTART.md)**

### Voglio una guida completa per l'installazione
→ **[INSTALL_LINUX.md](INSTALL_LINUX.md)**

### Voglio contribuire al codice
→ **[CLAUDE.md](CLAUDE.md)**

### Voglio usare PlatformUtils nel mio codice
→ **[PlatformUtils_README.md](PlatformUtils_README.md)**

### Voglio capire come è stato sviluppato il supporto Linux
→ **[LINUX_DEVELOPMENT_HISTORY.md](LINUX_DEVELOPMENT_HISTORY.md)**

---

## 🗑️ File Rimossi (Consolidati)

I seguenti file sono stati consolidati in **LINUX_DEVELOPMENT_HISTORY.md**:

- ❌ `LINUX_COMPATIBILITY_ANALYSIS.md` (1886 righe)
- ❌ `LINUX_IMPLEMENTATION_SUMMARY.md` (680 righe)
- ❌ `LINUX_TEST_REPORT.md` (569 righe)
- ❌ `PYTHON_3.14_FIX_SUMMARY.md` (224 righe)

**Totale consolidato**: 3359 righe → 1 file organizzato da 20 KB

---

## 📊 Statistiche Documentazione

| File | Dimensione | Righe | Target | Lingua |
|------|-----------|-------|--------|--------|
| QUICKSTART.md | 4.3 KB | 154 | Users | IT |
| INSTALL_LINUX.md | 8.5 KB | 420 | Users | IT |
| CLAUDE.md | 13 KB | 404 | Developers | EN |
| PlatformUtils_README.md | 5.7 KB | 206 | Developers | EN |
| LINUX_DEVELOPMENT_HISTORY.md | 20 KB | 840 | Developers | EN |

---

## 🔄 Mantenimento

### Quando aggiornare QUICKSTART.md
- Cambio nei comandi di installazione
- Nuove distribuzioni supportate
- Cambio in Python version requirements
- Fix a problemi comuni frequenti

### Quando aggiornare INSTALL_LINUX.md
- Nuove DCC supportate
- Cambio nei percorsi di sistema
- Nuove configurazioni XDG
- Aggiornamenti troubleshooting

### Quando aggiornare CLAUDE.md
- Nuovi moduli aggiunti
- Cambio nell'architettura
- Nuove convenzioni di codice
- Aggiornamenti pattern comuni

### Quando aggiornare LINUX_DEVELOPMENT_HISTORY.md
- Milestone importanti raggiunte
- Fix significativi
- Decisioni tecniche importanti
- Cambio di direzione nel progetto

---

## ✅ Checklist per Nuove Release

Prima di una nuova release:

- [ ] Verificare che QUICKSTART.md sia aggiornato
- [ ] Verificare che INSTALL_LINUX.md contenga tutte le distribuzioni testate
- [ ] Aggiornare version numbers in tutti i documenti
- [ ] Aggiornare "Testato su" con nuove distribuzioni
- [ ] Verificare che tutti i link funzionino
- [ ] Aggiornare tabelle compatibilità Python
- [ ] Controllare screenshot/esempi se presenti

---

**Ultimo aggiornamento**: 2025-11-15
**Branch**: `feature/linux-compatibility`
**Versione Prism**: 2.0.17 + Linux Support
