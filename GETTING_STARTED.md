# Getting Started

> **New here?**
>
> If this is your first visit, follow this guide from start to finish.
> In about 10 minutes you'll create and validate your first contribution to the
> Italian Knowledge Graph.

Italian Knowledge Graph runs locally on your computer. This guide takes you
from downloading the project to preparing and importing your first guided
contribution.

## 1. Prerequisites

You need:

- Python 3.10 or newer;
- Windows, macOS, or Linux;
- a web browser;
- Microsoft Word or another DOCX-compatible editor.

Git is optional. You need it only if you choose to clone the repository instead
of downloading a ZIP archive.

The editor and ontology operate locally. No ontology data is sent to cloud
services.

## 2. Get the Project

### Clone with Git

```bash
git clone https://github.com/stonamatteo-a11y/italian-knowledge-graph.git
cd italian-knowledge-graph
```

### Download a ZIP

1. Open the Italian Knowledge Graph repository on GitHub.
2. Select **Code**, then **Download ZIP**.
3. Extract the archive.
4. Open a terminal in the extracted `italian-knowledge-graph` directory.

## 3. Start the UI

The launcher checks Python and the local project before starting. If required
Python packages are missing, follow its error message or install the project
manually with:

```bash
python -m pip install -e .
```

### Windows

Double-click:

```text
start-ikg.bat
```

Alternatively, use PowerShell:

```powershell
.\start-ikg.ps1
```

### macOS

Authorize the launchers once:

```bash
chmod +x start-ikg.sh start-ikg.command
```

Then double-click `start-ikg.command` in Finder or run:

```bash
./start-ikg.command
```

The Terminal alternative is:

```bash
./start-ikg.sh
```

### Linux

```bash
chmod +x start-ikg.sh
./start-ikg.sh
```

The launcher starts the local editor and opens your default browser
automatically at `http://127.0.0.1:7777`.

## 4. Explore the Knowledge Graph

The left panel contains the ontology hierarchy.

- Expand a branch to browse its children.
- Use Search to find an ID, Label, or Description.
- Select a node to view its details in the editor.

## 5. Create Your First Contribution

Choose a domain or branch in the hierarchy, then follow this flow:

```text
Select a domain
        ↓
📦 Crea pacchetto di contributo
        ↓
Choose the number of nodes
        ↓
Generate the package
```

Choose the fields you want to review, select a node limit, review the summary,
and select **📦 Crea pacchetto di contributo**.

The generated ZIP contains `contribution.docx`, `README.txt`, and
`metadata.json`.

## 6. Complete the DOCX

1. Open `contribution.docx`.
2. Fill in any fields marked **Da compilare**.
3. Do not change fields marked **Protetto**.
4. Use the final proposal section if you want to suggest a new entry.
5. Save the document as DOCX.

You may leave fields empty when you do not want to contribute to them.

## 7. Import the Contribution

Return to the editor and follow this flow:

```text
Importa Ontologia
        ↓
Select contribution.docx
        ↓
Preview
        ↓
Validator
        ↓
Import
```

The Preview shows detected nodes, proposed changes, warnings, and blocking
errors. Review this information before confirming.

No ontology change is applied without passing through validation.

## 8. Validator

The deterministic Validator checks:

- record structure and required properties;
- hierarchy and parent references;
- identifiers and duplicates;
- supported relationships;
- consistency rules and required content constraints.

The Validator produces the same result for the same input and is the
authoritative acceptance mechanism for structural changes.

The Knowledge Quality Center provides additional diagnostic quality analysis.
Its score does not replace the Validator.

## 9. Find Help

- [`README.md`](README.md) provides the project overview and command reference.
- [`MANIFESTO.md`](MANIFESTO.md) explains the project's vision and principles.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) describes contribution and development
  guidelines.
- Use [GitHub Issues](https://github.com/stonamatteo-a11y/italian-knowledge-graph/issues)
  to report bugs.
- GitHub Discussions can be used for community questions when enabled.

## 10. First Contribution Complete

**Congratulations!**

You have completed your first Italian Knowledge Graph contribution.

Thank you for helping improve structured knowledge.
