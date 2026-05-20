---
title: Go
url: https://opencode.ai/docs/go
source: sitemap
fetched_at: 2026-04-17T06:41:06.075923992-03:00
rendered_js: false
word_count: 674
summary: This document introduces OpenCode Go, a low-cost subscription service providing reliable access to curated open coding models via API and TUI integration.
tags:
    - opencode-go
    - subscription-service
    - open-source-models
    - api-access
    - coding-ai
category: guide
---

Low cost subscription for open coding models.

OpenCode Go is a low cost subscription — **$5 for your first month**, then **$10/month** — that gives you reliable access to popular open coding models.

Go works like any other provider in OpenCode. You subscribe to OpenCode Go and get your API key. It’s **completely optional** and you don’t need to use it to use OpenCode.

It is designed primarily for international users, with models hosted in the US, EU, and Singapore for stable global access.

* * *

## [Background](#background)

Open models have gotten really good. They now reach performance close to proprietary models for coding tasks. And because many providers can serve them competitively, they are usually far cheaper.

However, getting reliable, low latency access to them can be difficult. Providers vary in quality and availability.

To fix this, we did a couple of things:

1. We tested a select group of open models and talked to their teams about how to best run them.
2. We then worked with a few providers to make sure these were being served correctly.
3. Finally, we benchmarked the combination of the model/provider and came up with a list that we feel good recommending.

OpenCode Go gives you access to these models for **$5 for your first month**, then **$10/month**.

* * *

## [How it works](#how-it-works)

OpenCode Go works like any other provider in OpenCode.

1. You sign in to [**OpenCode Zen**](https://opencode.ai/auth), subscribe to Go, and copy your API key.
2. You run the `/connect` command in the TUI, select `OpenCode Go`, and paste your API key.
3. Run `/models` in the TUI to see the list of models available through Go.

The current list of models includes:

- **GLM-5**
- **GLM-5.1**
- **Kimi K2.5**
- **MiMo-V2-Pro**
- **MiMo-V2-Omni**
- **MiniMax M2.5**
- **MiniMax M2.7**
- **Qwen3.5 Plus**
- **Qwen3.6 Plus**

The list of models may change as we test and add new ones.

* * *

## [Usage limits](#usage-limits)

OpenCode Go includes the following limits:

- **5 hour limit** — $12 of usage
- **Weekly limit** — $30 of usage
- **Monthly limit** — $60 of usage

Limits are defined in dollar value. This means your actual request count depends on the model you use. Cheaper models like Qwen3.5 Plus allow for more requests, while higher-cost models like GLM-5.1 allow for fewer.

The table below provides an estimated request count based on typical Go usage patterns:

Modelrequests per 5 hourrequests per weekrequests per monthGLM-5.18802,1504,300GLM-51,1502,8805,750Kimi K2.51,8504,6309,250MiMo-V2-Pro1,2903,2256,450MiMo-V2-Omni2,1505,45010,900Qwen3.6 Plus3,3008,20016,300MiniMax M2.73,4008,50017,000MiniMax M2.56,30015,90031,800Qwen3.5 Plus10,20025,20050,500

Estimates are based on observed average request patterns:

- GLM-5/5.1 — 700 input, 52,000 cached, 150 output tokens per request
- Kimi K2.5 — 870 input, 55,000 cached, 200 output tokens per request
- MiniMax M2.7/M2.5 — 300 input, 55,000 cached, 125 output tokens per request
- MiMo-V2-Pro — 350 input, 41,000 cached, 250 output tokens per request
- MiMo-V2-Omni — 1000 input, 60,000 cached, 140 output tokens per request
- Qwen3.5 Plus — 410 input, 47,000 cached, 140 output tokens per request
- Qwen3.6 Plus — 500 input, 57,000 cached, 190 output tokens per request

You can track your current usage in the [**console**](https://opencode.ai/auth).

Usage limits may change as we learn from early usage and feedback.

* * *

### [Usage beyond limits](#usage-beyond-limits)

If you also have credits on your Zen balance, you can enable the **Use balance** option in the console. When enabled, Go will fall back to your Zen balance after you’ve reached your usage limits instead of blocking requests.

* * *

## [Endpoints](#endpoints)

You can also access Go models through the following API endpoints.

ModelModel IDEndpointAI SDK PackageGLM-5.1glm-5.1`https://opencode.ai/zen/go/v1/chat/completions``@ai-sdk/openai-compatible`GLM-5glm-5`https://opencode.ai/zen/go/v1/chat/completions``@ai-sdk/openai-compatible`Kimi K2.5kimi-k2.5`https://opencode.ai/zen/go/v1/chat/completions``@ai-sdk/openai-compatible`MiMo-V2-Promimo-v2-pro`https://opencode.ai/zen/go/v1/chat/completions``@ai-sdk/openai-compatible`MiMo-V2-Omnimimo-v2-omni`https://opencode.ai/zen/go/v1/chat/completions``@ai-sdk/openai-compatible`MiniMax M2.7minimax-m2.7`https://opencode.ai/zen/go/v1/messages``@ai-sdk/anthropic`MiniMax M2.5minimax-m2.5`https://opencode.ai/zen/go/v1/messages``@ai-sdk/anthropic`Qwen3.6 Plusqwen3.6-plus`https://opencode.ai/zen/go/v1/chat/completions``@ai-sdk/alibaba`Qwen3.5 Plusqwen3.5-plus`https://opencode.ai/zen/go/v1/chat/completions``@ai-sdk/alibaba`

The [model id](https://opencode.ai/docs/config/#models) in your OpenCode config uses the format `opencode-go/<model-id>`. For example, for Kimi K2.5, you would use `opencode-go/kimi-k2.5` in your config.

* * *

## [Privacy](#privacy)

The plan is designed primarily for international users, with models hosted in the US, EU, and Singapore for stable global access. Our providers follow a zero-retention policy and do not use your data for model training.

* * *

## [Goals](#goals)

We created OpenCode Go to:

1. Make AI coding **accessible** to more people with a low cost subscription.
2. Provide **reliable** access to the best open coding models.
3. Curate models that are **tested and benchmarked** for coding agent use.
4. Have **no lock-in** by allowing you to use any other provider with OpenCode as well.