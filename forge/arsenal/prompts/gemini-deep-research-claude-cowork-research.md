---
name: claude-cowork-research
target: gemini-deep-research
quality: 9/10
date: 2026-03-29
tags: claude, cowork, prompting, plugin, research, llm-context
---

ROLE: You are a Senior AI Systems Researcher specializing in prompt engineering,
LLM interaction design, and collaborative AI tooling documentation.

TASK: Conduct exhaustive research into Claude Cowork — its prompting model,
session capabilities, plugin architecture, and interaction patterns — to produce
a structured knowledge base optimized for use as LLM context material.

SCOPE: Execute dedicated sub-searches targeting each of the following dimensions,
in priority order:

1. Core prompting model — how Claude Cowork sessions differ from standard Claude
   prompting; session structure, turn format, system prompt injection, and context
   window behavior specific to Cowork.

2. Plugin architecture & invocation syntax — how plugins are defined, triggered,
   and parameterized within Cowork; plugin file structure (.plugin format), skill
   routing, and slot-filling mechanics.

3. Skill and tool integration — how skills are invoked within Cowork sessions;
   differences between skill prompts, tool use, and direct user instructions;
   chained skill execution patterns.

4. Collaborative session mechanics — multi-agent or multi-user behaviors if
   applicable; context sharing, handoff patterns, and state persistence across
   turns.

5. Output directory conventions and artifact delivery — how Cowork sessions
   produce structured file outputs; naming conventions, delivery targets, and
   format expectations.

6. Known anti-patterns and failure modes — documented cases where Cowork prompts
   produce degraded output, routing failures, or plugin misfires; repair strategies.

7. Prompt templates and examples — any published or community-documented prompt
   templates specific to Cowork sessions; structural patterns that yield high
   fidelity outcomes.

SOURCE POLICY:
Prioritize: Official Anthropic documentation, Claude Code release notes, GitHub
repositories (anthropics/claude-code and related), technical blogs by Anthropic
engineers, verified developer community resources (e.g., Claude Discord, official
forums), academic or technical papers citing Claude Cowork.
Exclude: SEO content farms, unverified Medium articles, social media speculation,
Reddit threads without linked primary sources, marketing copy without technical
substance.
Conflict resolution: If sources present contradictory prompting conventions or
capability claims, document both versions with source citations, publication dates,
and an assessment of which reflects the most recent authoritative release. Do not
reconcile contradictions by averaging — preserve the divergence explicitly.

UNCERTAINTY PROTOCOL: If specific data for any sub-topic cannot be found in
authoritative sources, state "Data Unavailable" for that section. Do not infer,
extrapolate, or synthesize plausible-sounding content to fill the gap. Accuracy
over completeness — an honest gap is more valuable than a fabricated answer.

REASONING TRACE: Before writing the final report, generate an internal step-by-step
reasoning trace: state your search assumptions, identify any areas where source
quality was low, and flag confidence level (High / Medium / Low) per major section.

OUTPUT FORMAT: Structured Markdown optimized for LLM context ingestion.
Use ## headers per major dimension. Use tables for: capability comparisons,
prompt parameter schemas, plugin invocation syntax, and anti-pattern/repair pairs.
Use code blocks for all prompt templates, plugin structures, and syntax examples.
Front-load the most validated, high-certainty sections. Place uncertainty-flagged
sections at the end under ## Unverified / Low-Confidence Findings.
Target report length: 2000–4000 words. Prioritize density and precision over
completeness — a tight, accurate 2000-word document outperforms a padded 5000-word one.
