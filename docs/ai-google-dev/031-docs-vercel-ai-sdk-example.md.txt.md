---
title: Market Research Agent with Gemini and the AI SDK by Vercel
url: https://ai.google.dev/gemini-api/docs/vercel-ai-sdk-example.md.txt
source: llms
fetched_at: 2026-04-29T11:17:07.791637174-03:00
rendered_js: false
word_count: 218
summary: This guide demonstrates how to build a Node.js application using the AI SDK to perform automated market research with Gemini, extract structured data, and generate visual reports.
tags:
    - ai-sdk
    - typescript
    - gemini-api
    - market-analysis
    - data-extraction
    - chartjs
    - puppeteer
category: tutorial
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
The [AI SDK by Vercel](https://ai-sdk.dev) builds AI-powered applications in TypeScript. This guide creates a Node.js app that uses the AI SDK with Gemini API to perform automated market trend analysis, extract structured data for charts, and generate an HTML report saved as PDF.

## Prerequisites

- Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)
- [Node.js](https://nodejs.org/en/download) 18+
- Package manager: `npm`, `pnpm`, or `yarn`

> [!NOTE]
> The AI SDK also works with browser-based frameworks like [Next.js](https://nextjs.org/).

## Set up your application

```bash
# All package managers
mkdir market-trend-app
cd market-trend-app

# npm
npm init -y

# pnpm
pnpm init

# yarn
yarn init -y
```

## Install dependencies

### Core SDK

```bash
# npm
npm install ai @ai-sdk/google zod
npm install -D @types/node tsx typescript && npx tsc --init

# pnpm
pnpm add ai @ai-sdk/google zod
pnpm add -D @types/node tsx typescript

# yarn
yarn add ai @ai-sdk/google zod
yarn add -D @types/node tsx typescript && yarn tsc --init
```

> [!IMPORTANT]
> In generated `tsconfig.json`, comment out: `"verbatimModuleSyntax": true,`

### Rendering (Puppeteer + Chart.js)

```bash
# npm
npm install puppeteer chart.js
npm install -D @types/chart.js

# pnpm
pnpm add puppeteer chart.js
pnpm add -D @types/chart.js

# yarn
yarn add puppeteer chart.js
yarn add -D @types/chart.js
```

Approve Chromium download when prompted.

## Configure API key

```bash
# MacOS/Linux
export GOOGLE_GENERATIVE_AI_API_KEY="YOUR_API_KEY_HERE"

# PowerShell
setx GOOGLE_GENERATIVE_AI_API_KEY "YOUR_API_KEY_HERE"
```

## Create the application

Create `main.ts` in your project directory.

### Quick test

```typescript
import { google } from "@ai-sdk/google";
import { generateText } from "ai";

async function main() {
  const { text } = await generateText({
    model: google("gemini-3-flash-preview"),
    prompt: 'What is plant-based milk?',
  });
  console.log(text);
}

main().catch(console.error);
```

Run:

```bash
# npm
npx tsc && node main.js

# pnpm
pnpm tsx main.ts

# yarn
yarn tsc && node main.js
```

## Step 1: Perform market research with Google Search

Enable [Google Search](https://ai.google.dev/gemini-api/docs/google-search) for real-time data.

```typescript
import { google } from "@ai-sdk/google";
import { generateText } from "ai";

async function main() {
  const { text: marketTrends, sources } = await generateText({
    model: google("gemini-3-flash-preview"),
    tools: {
      google_search: google.tools.googleSearch({}),
    },
    prompt: `Search the web for market trends for plant-based milk in North America for 2024-2025.
    I need to know the market size, key players and their market share, and primary consumer drivers.`,
  });

  console.log("Market trends found:\n", marketTrends);
  // To see the sources, uncomment: console.log("Sources:\n", sources);
}

main().catch(console.error);
```

## Step 2: Extract chart data

Use `generateObject` with a `zod` schema to extract structured data for Chart.js.

```typescript
import { google } from "@ai-sdk/google";
import { generateText, generateObject } from "ai";
import { z } from "zod/v4";
import { ChartConfiguration } from "chart.js";

function createChartConfig({
  labels, data, label, type, colors,
}: {
  labels: string[];
  data: number[];
  label: string;
  type: "bar" | "line";
  colors: string[];
}): ChartConfiguration {
  return {
    type: type,
    data: {
      labels: labels,
      datasets: [{
        label: label,
        data: data,
        borderWidth: 1,
        ...(type === "bar" && { backgroundColor: colors }),
        ...(type === "line" && colors.length > 0 && { borderColor: colors[0] }),
      }],
    },
    options: { animation: { duration: 0 } },
  };
}

async function main() {
  // Step 1: Search market trends
  const { text: marketTrends, sources } = await generateText({
    model: google("gemini-3-flash-preview"),
    tools: { google_search: google.tools.googleSearch({}) },
    prompt: `Search the web for market trends for plant-based milk in North America for 2024-2025...`,
  });

  console.log("Market trends found.");

  // Step 2: Extract chart data
  const { object: chartData } = await generateObject({
    model: google("gemini-3-flash-preview"),
    schema: z.object({
      chartConfigurations: z.array(
        z.object({
          type: z.enum(["bar", "line"]),
          labels: z.array(z.string()),
          data: z.array(z.number()),
          label: z.string(),
          colors: z.array(z.string()),
        }),
      ),
    }),
    prompt: `Given the following market trends text, come up with 1-3 bar or line charts:\n\nMarket Trends:\n${marketTrends}`,
  });

  const chartConfigs = chartData.chartConfigurations.map(createChartConfig);
  console.log("Chart configurations generated.");
}

main().catch(console.error);
```

## Step 3: Generate the final report

Generate an HTML report with Puppeteer, save as PDF.

```typescript
import { google } from "@ai-sdk/google";
import { generateText, generateObject } from "ai";
import { z } from "zod/v4";
import { ChartConfiguration } from "chart.js";
import puppeteer from "puppeteer";

// ... createChartConfig helper from Step 2

async function main() {
  // ... Step 1 and 2 code ...

  // Step 3: Generate HTML report and save as PDF
  const { text: htmlReport } = await generateText({
    model: google("gemini-3-flash-preview"),
    prompt: `You are an expert financial analyst and report writer.
    Your task is to generate a comprehensive market analysis report in HTML format.

    **Instructions:**
    1. Write a full HTML document.
    2. Use the provided "Market Trends" text for the main body with clear headings and paragraphs.
    3. Incorporate "Chart Configurations" using Chart.js. Create unique <canvas> elements and <script> blocks.
    4. Reference "Sources" at the end.
    5. Use only provided information; no placeholders.
    6. Return only raw HTML code.

    **Chart Rendering Snippet:**
    Include in head: <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    For each chart:
    <div style="width: 800px; height: 600px;">
      <canvas id="chart1"></canvas>
    </div>
    <script>new Chart(document.getElementById('chart1'), config);</script>

    **Data:**
    - Market Trends: ${marketTrends}
    - Chart Configurations: ${JSON.stringify(chartConfigs)}
    - Sources: ${JSON.stringify(sources)}`,
  });

  // Strip markdown code block wrapper if present
  const finalHtml = htmlReport.replace(/^```html\n/, "").replace(/\n```$/, "");

  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setContent(finalHtml);
  await page.pdf({ path: "report.pdf", format: "A4" });
  await browser.close();

  console.log("\nReport generated successfully: report.pdf");
}

main().catch(console.error);
```

## Run the application

```bash
# npm
npx tsc && node main.js

# pnpm
pnpm tsx main.ts

# yarn
yarn tsc && node main.js
```

A `report.pdf` file containing your market analysis appears in the project directory.

![Market analysis report](https://ai.google.dev/static/gemini-api/docs/images/market-research-pdf.jpg)

## Further resources

- [AI SDK docs](https://ai-sdk.dev/docs)
- [AI SDK Google Generative AI docs](https://ai-sdk.dev/providers/ai-sdk-providers/google-generative-ai)
- [AI SDK cookbook: Get Started with Gemini](https://ai-sdk.dev/cookbook/guides/gemini)

#topic-market-analysis #topic-data-extraction #topic-ai-sdk
