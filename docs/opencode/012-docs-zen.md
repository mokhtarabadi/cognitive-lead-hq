---
title: Zen
url: https://opencode.ai/docs/zen/
source: crawler
fetched_at: 2026-02-14T12:04:43.520768-03:00
rendered_js: false
word_count: 1029
summary: OpenCode Zen is a curated AI gateway providing access to verified coding models through a unified API and billing system. The document details model endpoints, configuration steps, pricing per token, and data privacy policies.
tags:
    - opencode-zen
    - ai-gateway
    - api-endpoints
    - llm-pricing
    - coding-models
    - model-benchmarking
    - data-privacy
category: reference
---

Curated list of models provided by OpenCode.

OpenCode Zen is a list of tested and verified models provided by the OpenCode team.

Zen works like any other provider in OpenCode. You login to OpenCode Zen and get your API key. It’s **completely optional** and you don’t need to use it to use OpenCode.

* * *

## [Background](#background)

There are a large number of models out there but only a few of these models work well as coding agents. Additionally, most providers are configured very differently; so you get very different performance and quality.

So if you are using a model through something like OpenRouter, you can never be sure if you are getting the best version of the model you want.

To fix this, we did a couple of things:

1. We tested a select group of models and talked to their teams about how to best run them.
2. We then worked with a few providers to make sure these were being served correctly.
3. Finally, we benchmarked the combination of the model/provider and came up with a list that we feel good recommending.

OpenCode Zen is an AI gateway that gives you access to these models.

* * *

## [How it works](#how-it-works)

OpenCode Zen works like any other provider in OpenCode.

1. You sign in to [**OpenCode Zen**](https://opencode.ai/auth), add your billing details, and copy your API key.
2. You run the `/connect` command in the TUI, select OpenCode Zen, and paste your API key.
3. Run `/models` in the TUI to see the list of models we recommend.

You are charged per request and you can add credits to your account.

* * *

## [Endpoints](#endpoints)

You can also access our models through the following API endpoints.

ModelModel IDEndpointAI SDK PackageGPT 5.2gpt-5.2`https://opencode.ai/zen/v1/responses``@ai-sdk/openai`GPT 5.2 Codexgpt-5.2-codex`https://opencode.ai/zen/v1/responses``@ai-sdk/openai`GPT 5.1gpt-5.1`https://opencode.ai/zen/v1/responses``@ai-sdk/openai`GPT 5.1 Codexgpt-5.1-codex`https://opencode.ai/zen/v1/responses``@ai-sdk/openai`GPT 5.1 Codex Maxgpt-5.1-codex-max`https://opencode.ai/zen/v1/responses``@ai-sdk/openai`GPT 5.1 Codex Minigpt-5.1-codex-mini`https://opencode.ai/zen/v1/responses``@ai-sdk/openai`GPT 5gpt-5`https://opencode.ai/zen/v1/responses``@ai-sdk/openai`GPT 5 Codexgpt-5-codex`https://opencode.ai/zen/v1/responses``@ai-sdk/openai`GPT 5 Nanogpt-5-nano`https://opencode.ai/zen/v1/responses``@ai-sdk/openai`Claude Sonnet 4.5claude-sonnet-4-5`https://opencode.ai/zen/v1/messages``@ai-sdk/anthropic`Claude Sonnet 4claude-sonnet-4`https://opencode.ai/zen/v1/messages``@ai-sdk/anthropic`Claude Haiku 4.5claude-haiku-4-5`https://opencode.ai/zen/v1/messages``@ai-sdk/anthropic`Claude Haiku 3.5claude-3-5-haiku`https://opencode.ai/zen/v1/messages``@ai-sdk/anthropic`Claude Opus 4.6claude-opus-4-6`https://opencode.ai/zen/v1/messages``@ai-sdk/anthropic`Claude Opus 4.5claude-opus-4-5`https://opencode.ai/zen/v1/messages``@ai-sdk/anthropic`Claude Opus 4.1claude-opus-4-1`https://opencode.ai/zen/v1/messages``@ai-sdk/anthropic`Gemini 3 Progemini-3-pro`https://opencode.ai/zen/v1/models/gemini-3-pro``@ai-sdk/google`Gemini 3 Flashgemini-3-flash`https://opencode.ai/zen/v1/models/gemini-3-flash``@ai-sdk/google`MiniMax M2.5minimax-m2.5`https://opencode.ai/zen/v1/chat/completions``@ai-sdk/openai-compatible`MiniMax M2.5 Freeminimax-m2.5-free`https://opencode.ai/zen/v1/chat/completions``@ai-sdk/openai-compatible`MiniMax M2.1minimax-m2.1`https://opencode.ai/zen/v1/chat/completions``@ai-sdk/openai-compatible`GLM 5glm-5`https://opencode.ai/zen/v1/chat/completions``@ai-sdk/openai-compatible`GLM 4.7glm-4.7`https://opencode.ai/zen/v1/chat/completions``@ai-sdk/openai-compatible`GLM 4.6glm-4.6`https://opencode.ai/zen/v1/chat/completions``@ai-sdk/openai-compatible`Kimi K2.5kimi-k2.5`https://opencode.ai/zen/v1/chat/completions``@ai-sdk/openai-compatible`Kimi K2.5 Freekimi-k2.5-free`https://opencode.ai/zen/v1/chat/completions``@ai-sdk/openai-compatible`Kimi K2 Thinkingkimi-k2-thinking`https://opencode.ai/zen/v1/chat/completions``@ai-sdk/openai-compatible`Kimi K2kimi-k2`https://opencode.ai/zen/v1/chat/completions``@ai-sdk/openai-compatible`Qwen3 Coder 480Bqwen3-coder`https://opencode.ai/zen/v1/chat/completions``@ai-sdk/openai-compatible`Big Picklebig-pickle`https://opencode.ai/zen/v1/chat/completions``@ai-sdk/openai-compatible`

The [model id](https://opencode.ai/docs/config/#models) in your OpenCode config uses the format `opencode/<model-id>`. For example, for GPT 5.2 Codex, you would use `opencode/gpt-5.2-codex` in your config.

* * *

### [Models](#models)

You can fetch the full list of available models and their metadata from:

```

https://opencode.ai/zen/v1/models
```

* * *

## [Pricing](#pricing)

We support a pay-as-you-go model. Below are the prices **per 1M tokens**.

ModelInputOutputCached ReadCached WriteBig PickleFreeFreeFree-MiniMax M2.5 FreeFreeFreeFree-MiniMax M2.5$0.30$1.20$0.06-MiniMax M2.1$0.30$1.20$0.10-GLM 5$1.00$3.20$0.20-GLM 4.7$0.60$2.20$0.10-GLM 4.6$0.60$2.20$0.10-Kimi K2.5 FreeFreeFreeFree-Kimi K2.5$0.60$3.00$0.08-Kimi K2 Thinking$0.40$2.50--Kimi K2$0.40$2.50--Qwen3 Coder 480B$0.45$1.50--Claude Sonnet 4.5 (≤ 200K tokens)$3.00$15.00$0.30$3.75Claude Sonnet 4.5 (&gt; 200K tokens)$6.00$22.50$0.60$7.50Claude Sonnet 4 (≤ 200K tokens)$3.00$15.00$0.30$3.75Claude Sonnet 4 (&gt; 200K tokens)$6.00$22.50$0.60$7.50Claude Haiku 4.5$1.00$5.00$0.10$1.25Claude Haiku 3.5$0.80$4.00$0.08$1.00Claude Opus 4.6 (≤ 200K tokens)$5.00$25.00$0.50$6.25Claude Opus 4.6 (&gt; 200K tokens)$10.00$37.50$1.00$12.50Claude Opus 4.5$5.00$25.00$0.50$6.25Claude Opus 4.1$15.00$75.00$1.50$18.75Gemini 3 Pro (≤ 200K tokens)$2.00$12.00$0.20-Gemini 3 Pro (&gt; 200K tokens)$4.00$18.00$0.40-Gemini 3 Flash$0.50$3.00$0.05-GPT 5.2$1.75$14.00$0.175-GPT 5.2 Codex$1.75$14.00$0.175-GPT 5.1$1.07$8.50$0.107-GPT 5.1 Codex$1.07$8.50$0.107-GPT 5.1 Codex Max$1.25$10.00$0.125-GPT 5.1 Codex Mini$0.25$2.00$0.025-GPT 5$1.07$8.50$0.107-GPT 5 Codex$1.07$8.50$0.107-GPT 5 NanoFreeFreeFree-

You might notice *Claude Haiku 3.5* in your usage history. This is a [low cost model](https://opencode.ai/docs/config/#models) that’s used to generate the titles of your sessions.

The free models:

- Kimi K2.5 Free is available on OpenCode for a limited time. The team is using this time to collect feedback and improve the model.
- MiniMax M2.5 Free is available on OpenCode for a limited time. The team is using this time to collect feedback and improve the model.
- Big Pickle is a stealth model that’s free on OpenCode for a limited time. The team is using this time to collect feedback and improve the model.

[Contact us](mailto:contact@anoma.ly) if you have any questions.

* * *

### [Auto-reload](#auto-reload)

If your balance goes below $5, Zen will automatically reload $20.

You can change the auto-reload amount. You can also disable auto-reload entirely.

* * *

### [Monthly limits](#monthly-limits)

You can also set a monthly usage limit for the entire workspace and for each member of your team.

For example, let’s say you set a monthly usage limit to $20, Zen will not use more than $20 in a month. But if you have auto-reload enabled, Zen might end up charging you more than $20 if your balance goes below $5.

* * *

## [Privacy](#privacy)

All our models are hosted in the US. Our providers follow a zero-retention policy and do not use your data for model training, with the following exceptions:

- Big Pickle: During its free period, collected data may be used to improve the model.
- Kimi K2.5 Free: During its free period, collected data may be used to improve the model.
- MiniMax M2.5 Free: During its free period, collected data may be used to improve the model.
- OpenAI APIs: Requests are retained for 30 days in accordance with [OpenAI’s Data Policies](https://platform.openai.com/docs/guides/your-data).
- Anthropic APIs: Requests are retained for 30 days in accordance with [Anthropic’s Data Policies](https://docs.anthropic.com/en/docs/claude-code/data-usage).

* * *

## [For Teams](#for-teams)

Zen also works great for teams. You can invite teammates, assign roles, curate the models your team uses, and more.

Managing your workspace is currently free for teams as a part of the beta. We’ll be sharing more details on the pricing soon.

* * *

### [Roles](#roles)

You can invite teammates to your workspace and assign roles:

- **Admin**: Manage models, members, API keys, and billing
- **Member**: Manage only their own API keys

Admins can also set monthly spending limits for each member to keep costs under control.

* * *

### [Model access](#model-access)

Admins can enable or disable specific models for the workspace. Requests made to a disabled model will return an error.

This is useful for cases where you want to disable the use of a model that collects data.

* * *

### [Bring your own key](#bring-your-own-key)

You can use your own OpenAI or Anthropic API keys while still accessing other models in Zen.

When you use your own keys, tokens are billed directly by the provider, not by Zen.

For example, your organization might already have a key for OpenAI or Anthropic and you want to use that instead of the one that Zen provides.

* * *

## [Goals](#goals)

We created OpenCode Zen to:

1. **Benchmark** the best models/providers for coding agents.
2. Have access to the **highest quality** options and not downgrade performance or route to cheaper providers.
3. Pass along any **price drops** by selling at cost; so the only markup is to cover our processing fees.
4. Have **no lock-in** by allowing you to use it with any other coding agent. And always let you use any other provider with OpenCode as well.