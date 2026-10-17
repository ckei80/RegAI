# RegAI — AI-Assisted Regulatory Evidence Assessment

RegAI is a working MVP exploring how AI can help assess regulatory requirements against website evidence.

The goal is to turn regulatory text and website content into structured, traceable assessments that help people identify what the available evidence supports, where it is insufficient, and where potential gaps may exist.

**Core workflow:** Regulation → Interpretation → Evidence → Assessment → Finding

## The Problem

Assessing whether an organisation's website addresses regulatory requirements can involve manually reviewing complex regulatory text, searching through lengthy privacy policies, and comparing requirements against scattered evidence.

RegAI explores how AI-assisted analysis can make this process more structured, repeatable, and transparent while keeping the underlying evidence available for human review.

## Current Capabilities

* Extract and structure regulatory requirements.
* Preserve original regulatory text alongside AI-generated interpretations.
* Import and process website content.
* Retrieve evidence relevant to selected requirements.
* Assess multiple requirements using an AI provider.
* Generate explanations and evidence references for assessment results.
* Support local AI models through an OpenAI-compatible API, as well as an OpenAI provider.
* Run controlled evaluation cases to test assessment behaviour.

## Assessment Approach

RegAI uses three assessment outcomes:

* **SUPPORTED** — Available evidence supports the requirement being addressed. This does not establish legal compliance.
* **INSUFFICIENT** — Relevant evidence exists, but it is not sufficient to support a conclusion.
* **POTENTIAL_GAP** — Available evidence indicates a possible missing disclosure or contradiction. This is not a definitive finding of a legal breach.

A key design principle is that a lack of retrieved evidence should not automatically be treated as proof of non-compliance.

## System Architecture

<img width="1376" height="768" alt="RegAI_Arc" src="https://github.com/user-attachments/assets/2f003a32-8924-49ac-b250-2e73c36c5cb1" />

## Evaluation

In a controlled evaluation using 10 predefined ExampleShop scenarios, RegAI passed all 10 cases following an adjustment to the final assessment criteria.

The experiment highlighted an important product lesson: retrieving relevant evidence is not enough. The assessment stage must also apply appropriate criteria when deciding what that evidence supports.

This result applies only to the defined test cases. It should not be interpreted as a general accuracy rate or proof of regulatory compliance.

## Current Limitations

RegAI is an evolving MVP, not a production compliance platform or legal advice system.

## Product Direction

The next stage focuses on improving evidence traceability, expanding evaluation coverage, and making the workflow more useful for human reviewers.

The longer-term vision is an AI-assisted system that connects regulatory requirements to their interpretations, supporting evidence, and reviewable assessment findings.

---

*Built as a hands-on AI product development project exploring retrieval, LLM-based assessment, evaluation, and human oversight.*
