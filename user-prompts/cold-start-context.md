# Reusable User Prompt: Intelligent Cold-Start Context Report

**How to use:** Copy the English or Farsi block below, replace `[INSERT FEATURE]` / `[نام ماژول]` with your target module name (e.g., `packages/billing/`, `src/features/auth/`), and paste it into your local OpenCode terminal. OpenCode will use the `code-search` skill to gather the directory tree, extract vertical slice signatures for that module, and read all Core SOP files — producing a complete context report in one shot.

## English

```
Load the code-search skill.
1. Run `custom_context_get_directory_tree` on the root directory.
2. Extract vertical slice signatures for the `[INSERT FEATURE]` module using `custom_context_extract_signatures`.
3. Read ALL Core SOP files by running `custom_context_read_source_files` on: AGENTS.md, DESIGN.md, docs/architecture.md, docs/data_model.md, docs/conventions.md.
4. Compile everything into a single context report.
Do NOT read the report yourself. Return the file path to me.
```

## Farsi (Persian)

```
skill code-search رو لود کن.
1. با `custom_context_get_directory_tree` درخت فایل‌های پروژه رو از روت بگیر.
2. با `custom_context_extract_signatures` امضاهای کدهای ماژول `[نام ماژول]` رو استخراج کن (Vertical Slice).
3. همه فایل‌های اصلی رو با `custom_context_read_source_files` بخون: AGENTS.md, DESIGN.md, docs/architecture.md, docs/data_model.md, docs/conventions.md.
4. همه رو در یک فایل گزارش کانتکست جمع کن.
خودت گزارش رو نخون. فقط مسیر فایل رو به من بده.
```
