import os
import sys

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# If you are in a subfolder, this moves up ONE level to the root
root_dir = os.path.dirname(current_dir)

# Add root to path
sys.path.append(root_dir)

from dotenv import load_dotenv
load_dotenv()

from pypdf import PdfReader
from docx import Document as DocxDocument
from ai_clients import get_chroma_client, embed

# Same client and collection as your original script
client = get_chroma_client()
collection = client.get_or_create_collection("my_issue_logs")


# ── 1. FILE READERS ──────────────────────────────────────────

def read_txt(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def read_pdf(filepath: str) -> str:
    reader = PdfReader(filepath)
    return "\n".join(page.extract_text() for page in reader.pages)

def read_docx(filepath: str) -> str:
    doc = DocxDocument(filepath)
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())

def read_file(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".txt":
        return read_txt(filepath)
    elif ext == ".pdf":
        return read_pdf(filepath)
    elif ext == ".docx":
        return read_docx(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


# ── 2. CHUNKING ──────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50) -> list:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


# ── 3. DUPLICATE CHECK ───────────────────────────────────────

def is_already_loaded(filename: str) -> bool:
    results = collection.get(where={"source": filename})
    return len(results["ids"]) > 0


# ── 4. LOAD DOCUMENT ─────────────────────────────────────────

def load_document(filepath: str, category: str = "general"):
    filename = os.path.basename(filepath)

    print(f"\n📄 Loading: {filename}")

    # Read file
    content = read_file(filepath)
    print(f"   Total characters: {len(content)}")

    # Chunk it
    chunks = chunk_text(content)
    print(f"   Total chunks: {len(chunks)}")

    # Build lists - same pattern as your original docs list
    ids        = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
    embeddings = [embed(chunk) for chunk in chunks]
    documents  = chunks
    metadatas  = [{"source": filename, "category": category, "chunk_index": i} for i in range(len(chunks))]

    # Add to ChromaDB - same as your original collection.add()
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    print(f"✅ Added {len(chunks)} chunks from {filename} to ChromaDB")


def load_document_safe(filepath: str, category: str = "general"):
    filename = os.path.basename(filepath)
    if is_already_loaded(filename):
        print(f"⏭️  Skipping {filename} - already loaded")
        return
    load_document(filepath, category)


def load_folder(folder_path: str, category: str = "general"):
    supported = [".txt", ".pdf", ".docx"]
    files = [
        f for f in os.listdir(folder_path)
        if os.path.splitext(f)[1].lower() in supported
    ]

    if not files:
        print(f"No supported files found in {folder_path}")
        return

    print(f"\n📁 Found {len(files)} files in {folder_path}")
    for filename in files:
        filepath = os.path.join(folder_path, filename)
        try:
            load_document_safe(filepath, category)
        except Exception as e:
            print(f"❌ Failed to load {filename}: {e}")

    print(f"\n🎉 All files processed!")


# ── 5. RUN ───────────────────────────────────────────────────
#below only run when testing, otherwise the call is based on code calling this function.
if __name__ == "__main__":

    # Option A - single file
    load_document_safe(
        filepath=os.path.join(root_dir, "data", "test.txt"),
        category="work"
    )

    # Option B - entire folder
    # load_folder(
    #     folder_path=os.path.join(root_dir, "data"),
    #     category="work"
    # )