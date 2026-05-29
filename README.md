# Newsroom Infrastructure for AI Experimentation

**Dataharvest 2026**

Jonathan Soma

Small local demos for OCR, text-to-speech, semantic PDF search, and Streamlit data browsing.

**[View the workshop materials](https://jsoma.github.io/workshop-newsroom-ai-infra/)**

[Open in Codespaces](https://codespaces.new/jsoma/workshop-newsroom-ai-infra?ref=main) | [View slides](https://jsoma.github.io/workshop-newsroom-ai-infra/ai-experimentation.pdf) | [Download PPTX](https://jsoma.github.io/workshop-newsroom-ai-infra/ai-experimentation.pptx)

## Materials

### 01. OCR

Journalists often deal with scanned texts, but the best tools are locked behind code. How can we help non-technical users try out our favorite libaries without forcing them through installing Python and running notebooks?

#### OCR with Gradio: simple

A tiny PDF OCR interface using RapidOCR.

Try: [Open in Colab](https://colab.research.google.com/github/jsoma/workshop-newsroom-ai-infra/blob/main/docs/01-ocr/01-gradio-ocr-simple-ANSWERS.ipynb) | [Colab (code-along)](https://colab.research.google.com/github/jsoma/workshop-newsroom-ai-infra/blob/main/docs/01-ocr/01-gradio-ocr-simple.ipynb) | [Codespaces](https://codespaces.new/jsoma/workshop-newsroom-ai-infra?ref=main) | [Download .ipynb](https://jsoma.github.io/workshop-newsroom-ai-infra/01-ocr/01-gradio-ocr-simple-ANSWERS.ipynb) | [Read online](https://jsoma.github.io/workshop-newsroom-ai-infra/01-ocr/01-gradio-ocr-simple-ANSWERS.html)

#### OCR with Gradio: fancy

A richer OCR interface comparing RapidOCR with GLM-OCR.

Try: [Open in Colab](https://colab.research.google.com/github/jsoma/workshop-newsroom-ai-infra/blob/main/docs/01-ocr/01-gradio-ocr-fancy-ANSWERS.ipynb) | [Colab (code-along)](https://colab.research.google.com/github/jsoma/workshop-newsroom-ai-infra/blob/main/docs/01-ocr/01-gradio-ocr-fancy.ipynb) | [Codespaces](https://codespaces.new/jsoma/workshop-newsroom-ai-infra?ref=main) | [Download .ipynb](https://jsoma.github.io/workshop-newsroom-ai-infra/01-ocr/01-gradio-ocr-fancy-ANSWERS.ipynb) | [Read online](https://jsoma.github.io/workshop-newsroom-ai-infra/01-ocr/01-gradio-ocr-fancy-ANSWERS.html)

### 02. Text-to-speech

Newsrooms' C-suites have *loved* auto-generated podcasts recently, but the rest of the publication is often split. How can we let everyone have a hand in demoing the product to show its strengths and weaknesses?

#### Text-to-speech with Gradio: simple

A small Kokoro ONNX text-to-speech demo.

Try: [Open in Colab](https://colab.research.google.com/github/jsoma/workshop-newsroom-ai-infra/blob/main/docs/02-text-to-speech/02-gradio-tts-simple-ANSWERS.ipynb) | [Colab (code-along)](https://colab.research.google.com/github/jsoma/workshop-newsroom-ai-infra/blob/main/docs/02-text-to-speech/02-gradio-tts-simple.ipynb) | [Codespaces](https://codespaces.new/jsoma/workshop-newsroom-ai-infra?ref=main) | [Download .ipynb](https://jsoma.github.io/workshop-newsroom-ai-infra/02-text-to-speech/02-gradio-tts-simple-ANSWERS.ipynb) | [Read online](https://jsoma.github.io/workshop-newsroom-ai-infra/02-text-to-speech/02-gradio-tts-simple-ANSWERS.html)

#### Text-to-speech with Gradio: fancy

A larger TTS demo with Kokoro ONNX and MMS options.

Try: [Open in Colab](https://colab.research.google.com/github/jsoma/workshop-newsroom-ai-infra/blob/main/docs/02-text-to-speech/02-gradio-tts-fancy-ANSWERS.ipynb) | [Colab (code-along)](https://colab.research.google.com/github/jsoma/workshop-newsroom-ai-infra/blob/main/docs/02-text-to-speech/02-gradio-tts-fancy.ipynb) | [Codespaces](https://codespaces.new/jsoma/workshop-newsroom-ai-infra?ref=main) | [Download .ipynb](https://jsoma.github.io/workshop-newsroom-ai-infra/02-text-to-speech/02-gradio-tts-fancy-ANSWERS.ipynb) | [Read online](https://jsoma.github.io/workshop-newsroom-ai-infra/02-text-to-speech/02-gradio-tts-fancy-ANSWERS.html)

### 03. PDF search

Semantic search is a useful tool for investigative work, but you don't always want to upload all of your docs into a Google product. Can a home-grown version work just as well?

#### PDF Search: notebook version

A notebook walkthrough that reads local PDFs, embeds each page, and ranks semantic search results. This will only work on codespaces!

Try: [Open in Colab](https://colab.research.google.com/github/jsoma/workshop-newsroom-ai-infra/blob/main/docs/03-pdf-search/03-streamlit-pdf-search-manual-ANSWERS.ipynb) | [Colab (code-along)](https://colab.research.google.com/github/jsoma/workshop-newsroom-ai-infra/blob/main/docs/03-pdf-search/03-streamlit-pdf-search-manual.ipynb) | [Codespaces](https://codespaces.new/jsoma/workshop-newsroom-ai-infra?ref=main) | [Download .ipynb](https://jsoma.github.io/workshop-newsroom-ai-infra/03-pdf-search/03-streamlit-pdf-search-manual-ANSWERS.ipynb) | [Read online](https://jsoma.github.io/workshop-newsroom-ai-infra/03-pdf-search/03-streamlit-pdf-search-manual-ANSWERS.html)

#### PDF Search: Streamlit app

Semantic search over local PDFs using sentence-transformer embeddings.

Try: [Codespaces](https://codespaces.new/jsoma/workshop-newsroom-ai-infra?ref=main) | [Download .py](https://jsoma.github.io/workshop-newsroom-ai-infra/03-pdf-search/03-streamlit-pdf-search.py) | [Read code](https://jsoma.github.io/workshop-newsroom-ai-infra/03-pdf-search/03-streamlit-pdf-search.html)

### 04. Transfer data

Tired of doing data analysis for all of your coworkers? Give them the tools to browse the data directly themselves!

[Download materials](https://jsoma.github.io/workshop-newsroom-ai-infra/04-transfer-data/04-transfer-data-materials.zip)

#### Analyzing Real Estate transfers the normal way

A notebook that opens up a CSV and does a little light analysis.

Try: [Open in Colab](https://colab.research.google.com/github/jsoma/workshop-newsroom-ai-infra/blob/main/docs/04-transfer-data/04-transfers-ANSWERS.ipynb) | [Colab (code-along)](https://colab.research.google.com/github/jsoma/workshop-newsroom-ai-infra/blob/main/docs/04-transfer-data/04-transfers.ipynb) | [Codespaces](https://codespaces.new/jsoma/workshop-newsroom-ai-infra?ref=main) | [Download .ipynb](https://jsoma.github.io/workshop-newsroom-ai-infra/04-transfer-data/04-transfers-ANSWERS.ipynb) | [Read online](https://jsoma.github.io/workshop-newsroom-ai-infra/04-transfer-data/04-transfers-ANSWERS.html)

#### Real Estate Transfers Browser: simple version

A simple Streamlit browser for local property transfer data.

Try: [Codespaces](https://codespaces.new/jsoma/workshop-newsroom-ai-infra?ref=main) | [Download .py](https://jsoma.github.io/workshop-newsroom-ai-infra/04-transfer-data/04-streamlit-transfers-simple.py) | [Read code](https://jsoma.github.io/workshop-newsroom-ai-infra/04-transfer-data/04-streamlit-transfers-simple.html)

#### Real Estate Transfers Browser: fancy version

A fuller Streamlit transfer-data app with charts, filters, and summaries.

Try: [Codespaces](https://codespaces.new/jsoma/workshop-newsroom-ai-infra?ref=main) | [Download .py](https://jsoma.github.io/workshop-newsroom-ai-infra/04-transfer-data/04-streamlit-transfers-fancy.py) | [Read code](https://jsoma.github.io/workshop-newsroom-ai-infra/04-transfer-data/04-streamlit-transfers-fancy.html)

### 05. Evaluations

Use [Braintrust](https://www.braintrust.dev/) for evaluation workflows, then use the CSV files here as small local datasets to test with.

Download the CSVs from the section's **Download materials** link.

[Download materials](https://jsoma.github.io/workshop-newsroom-ai-infra/05-evaluations/05-evaluations-materials.zip)

### 06. Structured outputs

#### OpenRouter + Pydantic AI

Use Pydantic AI with OpenRouter to ask questions and request structured outputs.

Try: [Open in Colab](https://colab.research.google.com/github/jsoma/workshop-newsroom-ai-infra/blob/main/docs/06-structured-outputs/06-openrouter-pydantic-ANSWERS.ipynb) | [Colab (code-along)](https://colab.research.google.com/github/jsoma/workshop-newsroom-ai-infra/blob/main/docs/06-structured-outputs/06-openrouter-pydantic.ipynb) | [Codespaces](https://codespaces.new/jsoma/workshop-newsroom-ai-infra?ref=main) | [Download .ipynb](https://jsoma.github.io/workshop-newsroom-ai-infra/06-structured-outputs/06-openrouter-pydantic-ANSWERS.ipynb) | [Read online](https://jsoma.github.io/workshop-newsroom-ai-infra/06-structured-outputs/06-openrouter-pydantic-ANSWERS.html)
