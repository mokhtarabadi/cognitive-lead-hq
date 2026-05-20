---
title: File Search
url: https://ai.google.dev/gemini-api/docs/file-search.md.txt
source: llms
fetched_at: 2026-04-29T11:17:24.706897125-03:00
rendered_js: false
word_count: 756
summary: This document provides a guide on using the Gemini API File Search tool to implement Retrieval Augmented Generation (RAG) by uploading or importing documents and configuring chunking parameters.
tags:
  - gemini-api
  - rag
  - file-search
  - data-indexing
  - embedding
  - chunking-configuration
category: guide
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
File Search implements RAG by importing, chunking, and indexing data for fast retrieval based on prompts. Retrieved information provides context for more accurate, relevant model responses.

**Cost structure:**
- File storage and query-time embeddings are **free**
- Indexing embeddings cost [embedding model pricing](https://ai.google.dev/gemini-api/docs/pricing#gemini-embedding) ($0.15 per 1M tokens)
- Regular Gemini input/output token costs apply

## Upload Directly to File Search Store

### Python

```python
from google import genai
from google.genai import types
import time

client = genai.Client()

# File name will be visible in citations
file_search_store = client.file_search_stores.create(config={'display_name': 'your-fileSearchStore-name'})

operation = client.file_search_stores.upload_to_file_search_store(
  file='sample.txt',
  file_search_store_name=file_search_store.name,
  config={
      'display_name' : 'display-file-name',
  }
)

while not operation.done:
    time.sleep(5)
    operation = client.operations.get(operation)

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="""Can you tell me about [insert question]""",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[file_search_store.name]
                )
            )
        ]
    )
)

print(response.text)
```

### JavaScript

```javascript
const { GoogleGenAI } = require('@google/genai');

const ai = new GoogleGenAI({});

async function run() {
  // File name will be visible in citations
  const fileSearchStore = await ai.fileSearchStores.create({
    config: { displayName: 'your-fileSearchStore-name' }
  });

  let operation = await ai.fileSearchStores.uploadToFileSearchStore({
    file: 'file.txt',
    fileSearchStoreName: fileSearchStore.name,
    config: {
      displayName: 'file-name',
    }
  });

  while (!operation.done) {
    await new Promise(resolve => setTimeout(resolve, 5000));
    operation = await ai.operations.get({ operation });
  }

  const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: "Can you tell me about [insert question]",
    config: {
      tools: [
        {
          fileSearch: {
            fileSearchStoreNames: [fileSearchStore.name]
          }
        }
      ]
    }
  });

  console.log(response.text);
}

run();
```

See [`uploadToFileSearchStore` API reference](https://ai.google.dev/api/file-search/file-search-stores#method:-media.uploadtofilesearchstore).

## Importing Files

Upload an existing file, then import it to your file search store:

### Python

```python
from google import genai
from google.genai import types
import time

client = genai.Client()

# File name will be visible in citations
sample_file = client.files.upload(file='sample.txt', config={'name': 'display_file_name'})

file_search_store = client.file_search_stores.create(config={'display_name': 'your-fileSearchStore-name'})

operation = client.file_search_stores.import_file(
    file_search_store_name=file_search_store.name,
    file_name=sample_file.name
)

while not operation.done:
    time.sleep(5)
    operation = client.operations.get(operation)

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="""Can you tell me about [insert question]""",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[file_search_store.name]
                )
            )
        ]
    )
)

print(response.text)
```

### JavaScript

```javascript
const { GoogleGenAI } = require('@google/genai');

const ai = new GoogleGenAI({});

async function run() {
  // File name will be visible in citations
  const sampleFile = await ai.files.upload({
    file: 'sample.txt',
    config: { name: 'file-name' }
  });

  const fileSearchStore = await ai.fileSearchStores.create({
    config: { displayName: 'your-fileSearchStore-name' }
  });

  let operation = await ai.fileSearchStores.importFile({
    fileSearchStoreName: fileSearchStore.name,
    fileName: sampleFile.name
  });

  while (!operation.done) {
    await new Promise(resolve => setTimeout(resolve, 5000));
    operation = await ai.operations.get({ operation });
  }

  const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: "Can you tell me about [insert question]",
    config: {
      tools: [
        {
          fileSearch: {
            fileSearchStoreNames: [fileSearchStore.name]
          }
        }
      ]
    }
  });

  console.log(response.text);
}

run();
```

See [`importFile` API reference](https://ai.google.dev/api/file-search/file-search-stores#method:-filesearchstores.importfile).

## Chunking Configuration

Control chunking strategy by specifying `chunking_config` with max tokens per chunk and max overlap tokens:

### Python

```python
operation = client.file_search_stores.upload_to_file_search_store(
    file_search_store_name=file_search_store.name,
    file_name=sample_file.name,
    config={
        'chunking_config': {
          'white_space_config': {
            'max_tokens_per_chunk': 200,
            'max_overlap_tokens': 20
          }
        }
    }
)

while not operation.done:
    time.sleep(5)
    operation = client.operations.get(operation)

print("Custom chunking complete.")
```

### JavaScript

```javascript
let operation = await ai.fileSearchStores.uploadToFileSearchStore({
  file: 'file.txt',
  fileSearchStoreName: fileSearchStore.name,
  config: {
    displayName: 'file-name',
    chunkingConfig: {
      whiteSpaceConfig: {
        maxTokensPerChunk: 200,
        maxOverlapTokens: 20
      }
    }
  }
});

while (!operation.done) {
  await new Promise(resolve => setTimeout(resolve, 5000));
  operation = await ai.operations.get({ operation });
}
console.log("Custom chunking complete.");
```

## How It Works

File Search uses semantic search to find relevant information. Unlike keyword-based search, it understands meaning and context.

**Process:**
1. **Import file** → Convert to [embeddings](https://ai.google.dev/gemini-api/docs/embeddings) capturing semantic meaning
2. **Store embeddings** → In specialized File Search database
3. **Query** → Convert query to embedding, find most similar document chunks

**No TTL** — embeddings and files persist until manually deleted or model deprecated.

![The indexing and querying process of File Search](https://ai.google.dev/static/gemini-api/docs/images/File-search.png)

- `uploadToFileSearchStore` bypasses File storage, using [`gemini-embedding-001`](https://ai.google.dev/gemini-api/docs/embeddings) directly
- Using Files API to create then import moves process through: Documents → File storage → Embedding model

## File Search Stores

A File Search store is a container for document embeddings. Raw files via File API are deleted after 48 hours; data in File Search stores persists indefinitely.

```python
file_search_store = client.file_search_stores.create(config={'display_name': 'my-file_search-store-123'})

for file_search_store in client.file_search_stores.list():
    print(file_search_store)

my_file_search_store = client.file_search_stores.get(name='fileSearchStores/my-file_search-store-123')

client.file_search_stores.delete(name='fileSearchStores/my-file_search-store-123', config={'force': True})
```

```javascript
const fileSearchStore = await ai.fileSearchStores.create({
  config: { displayName: 'my-file_search-store-123' }
});

const fileSearchStores = await ai.fileSearchStores.list();
for await (const store of fileSearchStores) {
  console.log(store);
}

const myFileSearchStore = await ai.fileSearchStores.get({
  name: 'fileSearchStores/my-file_search-store-123'
});

await ai.fileSearchStores.delete({
  name: 'fileSearchStores/my-file_search-store-123',
  config: { force: true }
});
```

```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/fileSearchStores?key=${GEMINI_API_KEY}" \
    -H "Content-Type: application/json"
    -d '{ "displayName": "My Store" }'

curl "https://generativelanguage.googleapis.com/v1beta/fileSearchStores?key=${GEMINI_API_KEY}" \

curl "https://generativelanguage.googleapis.com/v1beta/fileSearchStores/my-file_search-store-123?key=${GEMINI_API_KEY}"

curl -X DELETE "https://generativelanguage.googleapis.com/v1beta/fileSearchStores/my-file_search-store-123?key=${GEMINI_API_KEY}"
```

## File Search Documents

Manage individual documents: list, get, delete by name.

```python
for document_in_store in client.file_search_stores.documents.list(parent='fileSearchStores/my-file_search-store-123'):
  print(document_in_store)

file_search_document = client.file_search_stores.documents.get(name='fileSearchStores/my-file_search-store-123/documents/my_doc')
print(file_search_document)

client.file_search_stores.documents.delete(name='fileSearchStores/my-file_search-store-123/documents/my_doc')
```

```javascript
const documents = await ai.fileSearchStores.documents.list({
  parent: 'fileSearchStores/my-file_search-store-123'
});
for await (const doc of documents) {
  console.log(doc);
}

const fileSearchDocument = await ai.fileSearchStores.documents.get({
  name: 'fileSearchStores/my-file_search-store-123/documents/my_doc'
});

await ai.fileSearchStores.documents.delete({
  name: 'fileSearchStores/my-file_search-store-123/documents/my_doc'
});
```

```bash
curl "https://generativelanguage.googleapis.com/v1beta/fileSearchStores/my-file_search-store-123/documents?key=${GEMINI_API_KEY}"

curl "https://generativelanguage.googleapis.com/v1beta/fileSearchStores/my-file_search-store-123/documents/my_doc?key=${GEMINI_API_KEY}"

curl -X DELETE "https://generativelanguage.googleapis.com/v1beta/fileSearchStores/my-file_search-store-123/documents/my_doc?key=${GEMINI_API_KEY}"
```

## File Metadata

Add custom metadata (key-value pairs) to filter or provide context:

```python
op = client.file_search_stores.import_file(
    file_search_store_name=file_search_store.name,
    file_name=sample_file.name,
    custom_metadata=[
        {"key": "author", "string_value": "Robert Graves"},
        {"key": "year", "numeric_value": 1934}
    ]
)
```

```javascript
let operation = await ai.fileSearchStores.importFile({
  fileSearchStoreName: fileSearchStore.name,
  fileName: sampleFile.name,
  config: {
    customMetadata: [
      { key: "author", stringValue: "Robert Graves" },
      { key: "year", numericValue: 1934 }
    ]
  }
});
```

Filter search by metadata:

```python
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Tell me about the book 'I, Claudius'",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[file_search_store.name],
                    metadata_filter="author=Robert Graves",
                )
            )
        ]
    )
)

print(response.text)
```

```javascript
const response = await ai.models.generateContent({
  model: "gemini-3-flash-preview",
  contents: "Tell me about the book 'I, Claudius'",
  config: {
    tools: [
      {
        fileSearch: {
          fileSearchStoreNames: [fileSearchStore.name],
          metadataFilter: 'author="Robert Graves"',
        }
      }
    ]
  }
});

console.log(response.text);
```

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key=${GEMINI_API_KEY}" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
            "contents": [{
                "parts":[{"text": "Tell me about the book I, Claudius"}]
            }],
            "tools": [{
                "file_search": {
                    "file_search_store_names":["'$STORE_NAME'"],
                    "metadata_filter": "author = \"Robert Graves\""
                }
            }]
        }' 2> /dev/null > response.json

cat response.json
```

> [!info]
> Filter syntax guidance at [google.aip.dev/160](https://google.aip.dev/160)

## Citations

Access citation info through `grounding_metadata` attribute of the response:

```python
print(response.candidates[0].grounding_metadata)
```

```javascript
console.log(JSON.stringify(response.candidates?.[0]?.groundingMetadata, null, 2));
```

## Custom Metadata in Grounding Data

Access custom metadata in grounding metadata of model response. Each `grounding_chunk` in `retrieved_context` contains this metadata:

```python
for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
    if chunk.retrieved_context:
        print(f"Text: {chunk.retrieved_context.text}")
        if chunk.retrieved_context.custom_metadata:
            for metadata in chunk.retrieved_context.custom_metadata:
                print(f"Metadata Key: {metadata.key}")
                print(f"Value: {metadata.string_value or metadata.numeric_value}")
```

```javascript
const groundingMetadata = response.candidates[0].groundingMetadata;
groundingMetadata.groundingChunks.forEach((chunk) => {
  if (chunk.retrievedContext) {
    console.log(`Text: ${chunk.retrievedContext.text}`);
    if (chunk.retrievedContext.customMetadata) {
      chunk.retrievedContext.customMetadata.forEach((metadata) => {
        console.log(`Metadata Key: ${metadata.key}`);
        console.log(`Value: ${metadata.stringValue || metadata.numericValue}`);
      });
    }
  }
});
```

```json
{
  "candidates": [
    {
      "content": { ... },
      "grounding_metadata": {
        "grounding_chunks": [
          {
            "retrieved_context": {
              "text": "...",
              "title": "...",
              "uri": "...",
              "custom_metadata": [
                { "key": "author", "string_value": "Robert Graves" },
                { "key": "year", "numeric_value": 1934 }
              ]
            }
          }
        ],
        "grounding_supports": [ ... ]
      }
    }
  ]
}
```

## Structured Output

Combine File Search with [structured outputs](https://ai.google.dev/gemini-api/docs/structured-output) starting with Gemini 3 models:

```python
from pydantic import BaseModel, Field

class Money(BaseModel):
    amount: str = Field(description="The numerical part of the amount.")
    currency: str = Field(description="The currency of amount.")

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="What is the minimum hourly wage in Tokyo right now?",
    config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[file_search_store.name]
                        )
                    )
                ],
                response_mime_type="application/json",
                response_schema=Money.model_json_schema()
      )
)
result = Money.model_validate_json(response.text)
print(result)
```

```javascript
import { z } from "zod";

const moneySchema = z.object({
  amount: z.string().describe("The numerical part of the amount."),
  currency: z.string().describe("The currency of amount."),
});

async function run() {
  const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: "What is the minimum hourly wage in Tokyo right now?",
    config: {
      tools: [
        {
          fileSearch: {
            fileSearchStoreNames: [file_search_store.name],
          },
        },
      ],
      responseMimeType: "application/json",
      responseJsonSchema: z.toJSONSchema(moneySchema),
    },
  });

  const result = moneySchema.parse(JSON.parse(response.text));
  console.log(result);
}

run();
```

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{
    "contents": [{
      "parts": [{"text": "What is the minimum hourly wage in Tokyo right now?"}]
    }],
    "tools": [
      {
        "fileSearch": {
          "fileSearchStoreNames": ["$FILE_SEARCH_STORE_NAME"]
        }
      }
    ],
    "generationConfig": {
        "responseMimeType": "application/json",
        "responseJsonSchema": {
            "type": "object",
            "properties": {
                "amount": {"type": "string", "description": "The numerical part of the amount."},
                "currency": {"type": "string", "description": "The currency of amount."}
            },
            "required": ["amount", "currency"]
        }
    }
  }'
```

## Supported Models

| Model | File Search |
|---|---|
| [Gemini 3.1 Pro Preview](https://ai.google.dev/gemini-api/docs/gemini-3.1-pro-preview) | ✔️ |
| [Gemini 3.1 Flash-Lite Preview](https://ai.google.dev/gemini-api/docs/gemini-3.1-flash-lite-preview) | ✔️ |
| [Gemini 3 Flash Preview](https://ai.google.dev/gemini-api/docs/models/gemini-3-flash-preview) | ✔️ |
| [Gemini 2.5 Pro](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-pro) | ✔️ |
| [Gemini 2.5 Flash-Lite](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash-lite) | ✔️ |

## Supported Tool Combinations

Gemini 3 models support combining File Search with custom tools (function calling). See [tool combinations](https://ai.google.dev/gemini-api/docs/tool-combination).

## Supported File Types

### Application file types

- `application/dart`, `application/ecmascript`, `application/json`, `application/ms-java`, `application/msword`, `application/pdf`, `application/sql`, `application/typescript`, `application/vnd.curl`, `application/vnd.dart`, `application/vnd.ibm.secure-container`, `application/vnd.jupyter`, `application/vnd.ms-excel`, `application/vnd.oasis.opendocument.text`, `application/vnd.openxmlformats-officedocument.presentationml.presentation`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `application/vnd.openxmlformats-officedocument.wordprocessingml.template`, `application/x-csh`, `application/x-hwp`, `application/x-hwp-v5`, `application/x-latex`, `application/x-php`, `application/x-powershell`, `application/x-sh`, `application/x-shellscript`, `application/x-tex`, `application/x-zsh`, `application/xml`, `application/zip`

### Text file types

- `text/1d-interleaved-parityfec`, `text/RED`, `text/SGML`, `text/cache-manifest`, `text/calendar`, `text/cql`, `text/cql-extension`, `text/cql-identifier`, `text/css`, `text/csv`, `text/csv-schema`, `text/dns`, `text/encaprtp`, `text/enriched`, `text/example`, `text/fhirpath`, `text/flexfec`, `text/fwdred`, `text/gff3`, `text/grammar-ref-list`, `text/hl7v2`, `text/html`, `text/javascript`, `text/jcr-cnd`, `text/jsx`, `text/markdown`, `text/mizar`, `text/n3`, `text/parameters`, `text/parityfec`, `text/php`, `text/plain`, `text/provenance-notation`, `text/prs.fallenstein.rst`, `text/prs.lines.tag`, `text/prs.prop.logic`, `text/raptorfec`, `text/rfc822-headers`, `text/rtf`, `text/rtp-enc-aescm128`, `text/rtploopback`, `text/rtx`, `text/sgml`, `text/shaclc`, `text/shex`, `text/spdx`, `text/strings`, `text/t140`, `text/tab-separated-values`, `text/texmacs`, `text/troff`, `text/tsv`, `text/tsx`, `text/turtle`, `text/ulpfec`, `text/uri-list`, `text/vcard`, `text/vnd.DMClientScript`, `text/vnd.IPTC.NITF`, `text/vnd.IPTC.NewsML`, `text/vnd.a`, `text/vnd.abc`, `text/vnd.ascii-art`, `text/vnd.curl`, `text/vnd.debian.copyright`, `text/vnd.dvb.subtitle`, `text/vnd.esmertec.theme-descriptor`, `text/vnd.exchangeable`, `text/vnd.familysearch.gedcom`, `text/vnd.ficlab.flt`, `text/vnd.fly`, `text/vnd.fmi.flexstor`, `text/vnd.gml`, `text/vnd.graphviz`, `text/vnd.hans`, `text/vnd.hgl`, `text/vnd.in3d.3dml`, `text/vnd.in3d.spot`, `text/vnd.latex-z`, `text/vnd.motorola.reflex`, `text/vnd.ms-mediapackage`, `text/vnd.net2phone.commcenter.command`, `text/vnd.radisys.msml-basic-layout`, `text/vnd.senx.warpscript`, `text/vnd.sosi`, `text/vnd.trolltech.linguist`, `text/vnd.wap.si`, `text/vnd.wap.sl`, `text/vnd.wap.wml`, `text/vnd.wap.wmlscript`, `text/vtt`, `text/wgsl`, `text/x-asm`, `text/x-bibtex`, `text/x-boo`, `text/x-c`, `text/x-c++hdr`, `text/x-c++src`, `text/x-cassandra`, `text/x-chdr`, `text/x-coffeescript`, `text/x-component`, `text/x-csh`, `text/x-csharp`, `text/x-csrc`, `text/x-cuda`, `text/x-d`, `text/x-diff`, `text/x-dsrc`, `text/x-emacs-lisp`, `text/x-erlang`, `text/x-gff3`, `text/x-go`, `text/x-haskell`, `text/x-java`, `text/x-java-properties`, `text/x-java-source`, `text/x-kotlin`, `text/x-lilypond`, `text/x-lisp`, `text/x-literate-haskell`, `text/x-lua`, `text/x-moc`, `text/x-objcsrc`, `text/x-pascal`, `text/x-pcs-gcd`, `text/x-perl`, `text/x-perl-script`, `text/x-python`, `text/x-python-script`, `text/x-r-markdown`, `text/x-rsrc`, `text/x-rst`, `text/x-ruby-script`, `text/x-rust`, `text/x-sass`, `text/x-scala`, `text/x-scheme`, `text/x-script.python`, `text/x-scss`, `text/x-setext`, `text/x-sfv`, `text/x-sh`, `text/x-siesta`, `text/x-sos`, `text/x-sql`, `text/x-swift`, `text/x-tcl`, `text/x-tex`, `text/x-vbasic`, `text/x-vcalendar`, `text/xml`, `text/xml-dtd`, `text/xml-external-parsed-entity`, `text/yaml`

## Limitations

- **Live API** — Not supported in [Live API](https://ai.google.dev/gemini-api/docs/live)
- **Tool incompatibility** — Cannot be combined with [Grounding with Google Search](https://ai.google.dev/gemini-api/docs/google-search), [URL Context](https://ai.google.dev/gemini-api/docs/url-context), etc.

### Rate Limits

| Limit | Value |
|---|---|
| Max file size per document | 100 MB |
| **Total project File Search stores** | |
| Free tier | 1 GB |
| Tier 1 | 10 GB |
| Tier 2 | 100 GB |
| Tier 3 | 1 TB |
| **Recommendation** | Keep each store under 20 GB for optimal retrieval latencies |

> [!note]
> Store size is computed based on input size plus generated/stored embeddings, typically ~3x input data size.

## Pricing

- **Indexing** — Charged for embeddings at [embedding pricing](https://ai.google.dev/gemini-api/docs/pricing#gemini-embedding) ($0.15 per 1M tokens)
- **Storage** — Free
- **Query time** — Free
- **Retrieved tokens** — Charged as regular [context tokens](https://ai.google.dev/gemini-api/docs/tokens)

## What's Next

- API reference for [File Search Stores](https://ai.google.dev/api/file-search/file-search-stores) and File Search [Documents](https://ai.google.dev/api/file-search/documents)