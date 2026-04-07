# 🛒 Tri-Agent Shopping Assistant

## Overview

This project implements a multi-agent AI system that decomposes a shopping query into three specialized roles: retrieval, evaluation, and response generation. Instead of relying on a single monolithic model, each agent handles a distinct responsibility, enabling more structured decision-making and modular extensibility.

## Motivation

Traditional recommendation systems either depend on rigid rule-based filtering or opaque end-to-end models that lack interpretability. This project explores whether separating concerns across agents can produce more transparent, adaptable, and controllable recommendations, even if each individual component is relatively simple.

## How It Works

1. **Retrieval Agent** gathers relevant product candidates based on the user query.
2. **Evaluation Agent** filters and ranks options using constraints like price, ratings, or inferred preferences.
3. **Response Agent** synthesizes the final answer into a human-readable recommendation.

## Why This Approach

The goal is not to outperform production-grade recommendation systems, but to experiment with **agent-based reasoning patterns**. By isolating decision stages, the system makes it easier to debug, extend, and reason about failures—something that is often difficult in end-to-end LLM pipelines.

## Limitations

* Ranking is heuristic or prompt-driven rather than mathematically grounded
* Susceptible to LLM inconsistencies and hallucinations
* Lacks user memory and feedback loops

## Future Improvements

* Hybrid ranking (structured scoring + LLM reasoning)
* Iterative agent feedback or critique loops
* Persistent user preference modeling
* Stronger grounding to prevent hallucinations
