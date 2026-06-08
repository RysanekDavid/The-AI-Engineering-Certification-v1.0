<p align = "center" draggable="false" ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

<h1 align="center" id="heading">Session 1: Dense Vector Retrieval</h1>

### [Quicklinks]()

| 📰 Module Sheet                                                                 | ⏺️ Recording | 🖼️ Slides | 👨‍💻 Repo       | 📝 Homework | 📁 Feedback |
| :------------------------------------------------------------------------------- | :----------- | :-------- | :------------ | :---------- | :---------- |
| [Dense Vector Retrieval](../00_Docs/Modules/01_Dense_Vector_Retrieval/README.md) |[Recording!](https://us02web.zoom.us/rec/share/sHWvo0Nd1aI0SEhKecOLEX9kFGVJJAdYfsKiuTmm8t85W48Z2lnjpnzTy8jAd8R5.PwuqibGwAZhvDd8c) <br> passcode: `C62n^@Q!`| [Session 1 Slides](https://canva.link/htfqf8i39yejyhn) | You are here! | [Session 1 Assignment](https://forms.gle/Z9qskfVaAvPjn6gz8) | [Feedback 6/2](https://forms.gle/21a2uoL9DVZPwgJP6) |


## 🏗️ How AIM Does Assignments

> 📅 **Assignments will always be released to students as live class begins.** We will never release assignments early.

Each assignment will have a few of the following categories of exercises:

- ❓ **Questions** - these will be questions that you will be expected to gather the answer to. These can appear as general questions, or questions meant to spark a discussion in your breakout rooms.

- 🏗️ **Activities** - these will be work or coding activities meant to reinforce specific concepts or theory components.

- 🚧 **Advanced Builds (optional)** - Take on a challenge. These builds require you to create something with minimal guidance outside of the documentation.

## Main Assignment

In this assignment, you will build a vector RAG application using LangChain v1, OpenAI embeddings, and Qdrant.

The main notebook is:

```text
01_Cat_Health_Vector_RAG_LangChain_Qdrant.ipynb
```

The notebook uses the bundled cat health guideline PDF in `data/cat_health_guidelines.pdf`.

### Setup

From this folder, install the environment with uv:

```bash
uv sync
```

Then open the notebook in Cursor or VS Code and select the Python/Jupyter environment created by uv.

You will also need an OpenAI API key available when running the notebook.

---

## 🏗️ Activity #1: Embedding Similarity

Run the embedding similarity primer in the notebook.

You will compare embeddings for terms like:

- `king`
- `queen`
- `banana`
- `cat`
- `veterinarian`
- `cat health guidelines`

#### ❓Question #1

Why is cosine similarity useful for dense vector retrieval?

##### ✅ Answer:

Cosine similarity measures the angle between two embedding vectors, not their length. That matters because dense embeddings encode meaning through direction in vector space — two texts can express the same idea but with different magnitudes, and cosine still recognizes them as close. In the primer cell I saw `king` vs `queen` score 0.591 while `king` vs `banana` only scored 0.310, which matches my intuition about semantic similarity. For retrieval, cosine gives a stable ranking metric that's not biased by chunk length or model-specific norms.

---

## 🏗️ Activity #2: Build the Vector RAG Pipeline

Run the notebook sections that:

1. Load the PDF into LangChain `Document` objects
2. Split the document into chunks
3. Embed the chunks
4. Store the chunk embeddings in in-memory Qdrant
5. Retrieve relevant chunks with similarity scores
6. Generate an answer grounded in retrieved context

#### ❓Question #2

Why is metadata important for a RAG application?

##### ✅ Answer:

Metadata gives every chunk a verifiable origin — file name, page number, character offset, document type — which unlocks three things that wouldn't work without it:

1. **Citing sources.** Without metadata the model could pull text from anywhere and the user couldn't verify it. My notebook prints `[Source 1] cat_health_guidelines.pdf, page 8, ...` for every retrieved chunk, which is how user trust is built.
2. **Filtering before searching.** If multiple documents are indexed, metadata lets retrieval be restricted (e.g. "only chunks from the 2021 feline guidelines"). Without it the vector store sees one undifferentiated soup.
3. **Debugging retrieval.** When the top hit is wrong, page numbers and `start_index` show exactly which paragraph misfired so chunking or prompting can be fixed.

#### ❓Question #3

What tradeoff do we make when choosing chunk size and chunk overlap?

##### ✅ Answer:

Smaller chunks give more focused embeddings but fragment paragraphs and lose the broader context a question might need. Larger chunks preserve full topical units but their embedding represents a mixed-topic signal that's less precise for narrow queries. Overlap reduces the risk of cutting a key sentence in half at a chunk boundary — but it also duplicates text, which inflates storage and embedding-API cost without adding new information.

Activity #4 made this concrete for me: cutting baseline chunks of 1,000 chars down to 400 dropped my top similarity score from 0.584 to 0.570 and shifted the best hit to a less relevant section, because the cat health guideline already organizes content into self-contained paragraphs that match queries better when kept whole.

#### ❓Question #4

What does a similarity score help you understand, and what does it not prove by itself?

##### ✅ Answer:

A similarity score tells me how close two vectors are in the embedding model's space — useful for *ranking* candidates against each other. What it does NOT tell me on its own:

- Whether the chunk actually contains the answer to the question (vector closeness ≠ semantic correctness).
- Whether the LLM will be able to extract the right answer from it.
- Whether the score is "good" in any absolute sense — different embedding models produce different scales, so 0.58 from `text-embedding-3-small` isn't comparable to 0.58 from another model.

In Activity #4 I saw a variant with a lower top score (0.570) still produce a perfectly reasonable answer — just narrower in scope. The score is a useful relative signal for tuning, not a quality verdict on the final answer.

---

## 🏗️ Activity #3: Vibe Check Retrieval Quality

Run the notebook's vibe check queries and inspect both:

- The retrieved context
- The generated answer

#### ❓Question #5

For the vibe check queries, did the retrieved context seem relevant before generation? Why or why not?

##### ✅ Answer:

For the three on-topic questions (preventive care, symptoms, feeding a healthy adult cat), the retrieved chunks came from the right pages of the guideline and clearly addressed the question — similarity scores sat in the 0.55–0.60 range and the chunk previews lined up with what the answer eventually said. That's what relevant retrieval looks like before generation.

For the "Can my cat help me file my taxes?" query, retrieval still returned the four closest available chunks, but their content had no real connection to the question — they were just the least-bad matches in a corpus that has no tax content at all. The system handled this correctly because the prompt instructs the model to say *"I don't have enough information in the provided cat health guideline PDF to answer that"* when context doesn't cover the question, which is exactly what happened. So: retrieval was relevant where the answer was in the corpus, and the prompt-level safety-net handled the case where it wasn't.

---

## 🏗️ Activity #4: Tune Retrieval

Improve retrieval quality by changing one or more of:

- Chunk size
- Chunk overlap
- Retrieval `k`
- Query wording

Document what changed and whether retrieval improved.

##### Settings Changed:

- Compared the baseline (`chunk_size=1000`, `chunk_overlap=200`, `k=4`) against two variants on the same test question (*"What signs suggest that a cat should be seen by a veterinarian?"*):
  - Variant A — smaller chunks: `chunk_size=400`, `chunk_overlap=80`, `k=4`
  - Variant B — wider retrieval: `chunk_size=1000`, `chunk_overlap=200`, `k=8`

##### Results:

1. **Baseline** — 135 chunks. Top similarity score **0.584**, mean top-4 **0.568**. Top hit on page 8 (pain/anxiety and quality-of-life section). Answer was a broad practical list of warning signs.
2. **Variant A (smaller chunks)** — 345 chunks. Top score dropped to **0.570**, mean to 0.566. Top hit shifted to page 10 (senior-cat-specific content), and the generated answer narrowed almost entirely to senior cats.
3. **Variant B (k=8)** — same 135 chunks, so top score stayed at **0.584**, but mean dropped to **0.556** as chunks 5–8 added noticeably less relevant material. Net effect: baseline beat both variants — the cat guideline is already structured into topical paragraphs, so smaller chunks fragment those units and a larger `k` just dilutes precision without adding new signal.

---

## Optional Deep Dive: RAG From Scratch

If you want to look underneath the library abstractions, run the optional reference notebook:

```text
02_Cat_Health_Vector_RAG_From_Scratch.ipynb
```

It builds the same retrieval pipeline again with only:

- `pypdf` for extracting text from the PDF
- Python standard-library HTTP requests for calling OpenAI
- Handcrafted document, chunking, embedding, similarity-search, vector-store, and generation primitives

This notebook is a reference walkthrough, not an additional assignment. Its purpose is to make the responsibilities hidden by LangChain, Qdrant, and provider SDKs visible.

---

## Submitting Your Homework

### Main Assignment

Follow these steps to prepare and submit your homework:

1. Pull the latest updates from upstream into the main branch of your AIE9 repo:

```bash
git checkout main
git pull upstream main
git push origin main
```

2. Start Cursor from the `01_Dense_Vector_Retrieval` folder.
3. Complete the notebook.
4. Answer the questions in this `README.md`.
5. Add, commit, and push your modified work to your origin repository.

When submitting your homework, provide the GitHub URL to your AIE9 repo.
