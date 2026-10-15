from datetime import datetime, timezone
from pathlib import Path

from nicegui import run, ui
from openai import OpenAI

from regai.config import (
    PROVIDER_DEFAULTS,
    load_ai_config,
    save_ai_config,
)

from regai.assessment import assess_regulatory_requirement
from regai.embeddings import LocalEmbeddingProvider
from regai.evidence_ingestion import fetch_web_page
from regai.evidence_processing import process_evidence_source
from regai.evidence_retrieval import EvidenceRetriever
from regai.evidence_store import EvidenceStore
from regai.regulatory_models import RegulatoryRequirement
from regai.regulatory_store import RegulatoryStore

APP_NAME = "RegAI"
EVIDENCE_STORE_PATH = (
    Path.home()
    / "AppData"
    / "Roaming"
    / APP_NAME
    / "evidence.json"
)

evidence_store = EvidenceStore(EVIDENCE_STORE_PATH)

REGULATORY_STORE_PATH = (
    Path.home()
    / "AppData"
    / "Roaming"
    / APP_NAME
    / "regulations.json"
)

regulatory_store = RegulatoryStore(REGULATORY_STORE_PATH)

APP_DESCRIPTION = (
    "AI-assisted regulatory evidence assessment. "
    "Turn regulatory requirements and supporting evidence "
    "into traceable assessment findings."
)


def create_header():
    with ui.header().classes("items-center justify-between"):
        ui.label(APP_NAME).classes("text-2xl font-bold")
        ui.label("Local application").classes(
            "text-sm px-3 py-1 rounded-full bg-green-100 text-green-800"
        )


def create_navigation():
    with ui.column().classes(
        "w-56 p-4 gap-2 border-r border-gray-200"
    ):
        ui.label("WORKSPACE").classes(
            "text-xs font-bold text-gray-500 mb-2"
        )

        ui.button(
            "Home",
            on_click=lambda: ui.navigate.to("/"),
        ).props("flat").classes("w-full justify-start")

        ui.button(
            "Assessment",
            on_click=lambda: ui.navigate.to("/assessment"),
        ).props("flat").classes("w-full justify-start")

        ui.button(
            "Documents",
            on_click=lambda: ui.navigate.to("/documents"),
        ).props("flat").classes("w-full justify-start")

        ui.button(
            "Settings",
            on_click=lambda: ui.navigate.to("/settings"),
        ).props("flat").classes("w-full justify-start")


@ui.page("/")
def home_page():
    create_header()

    with ui.row().classes("w-full min-h-screen"):
        create_navigation()

        with ui.column().classes("flex-1 p-8 gap-6"):
            ui.label("Welcome to RegAI").classes("text-4xl font-bold")

            ui.label(APP_DESCRIPTION).classes(
                "text-lg text-gray-600 max-w-3xl"
            )

            with ui.card().classes("w-full max-w-3xl p-6"):
                ui.label("Your regulatory workspace").classes(
                    "text-xl font-semibold"
                )

                ui.label(
                    "RegAI is being developed to assess regulatory "
                    "requirements against available evidence while "
                    "preserving the sources behind each finding."
                ).classes("text-gray-600")

                ui.separator()

                ui.label("Planned workflow").classes(
                    "text-lg font-semibold"
                )

                with ui.column().classes("gap-2"):
                    for step in [
                        "1. Select or import regulatory requirements",
                        "2. Import supporting documents",
                        "3. Assess evidence against each requirement",
                        "4. Review findings and supporting sources",
                    ]:
                        ui.label(step).classes("text-gray-700")

            with ui.row().classes("w-full max-w-3xl gap-4"):
                with ui.card().classes("flex-1"):
                    ui.label("Assessment").classes(
                        "text-lg font-semibold"
                    )
                    ui.label(
                        "The assessment workflow is not yet connected."
                    ).classes("text-gray-600")
                    ui.button(
                        "Open assessment",
                        on_click=lambda: ui.navigate.to("/assessment"),
                    )

                with ui.card().classes("flex-1"):
                    ui.label("Documents").classes(
                        "text-lg font-semibold"
                    )
                    ui.label(
                        "Document import is not yet implemented."
                    ).classes("text-gray-600")
                    ui.button(
                        "Manage documents",
                        on_click=lambda: ui.navigate.to("/documents"),
                    )


def create_placeholder_page(path: str, title: str, description: str):
    @ui.page(path)
    def placeholder_page():
        create_header()

        with ui.row().classes("w-full min-h-screen"):
            create_navigation()

            with ui.column().classes("flex-1 max-w-3xl p-8 gap-4"):
                ui.label(title).classes("text-3xl font-bold")
                ui.label(description).classes("text-gray-600")

                ui.separator()

                ui.label(
                    "This functionality has not been implemented yet."
                ).classes("text-amber-800 bg-amber-50 p-4 rounded")


def create_settings_page():
    config = load_ai_config()

    provider = ui.select(
        options={
            "lm_studio": "LM Studio",
            "openai": "OpenAI",
        },
        value=config.provider,
        label="AI provider",
    ).classes("w-full")

    endpoint = ui.input(
        label="API endpoint",
        value=config.base_url,
    ).classes("w-full")

    model = ui.input(
        label="Model",
        value=config.model,
    ).classes("w-full")

    api_key = ui.input(
        label="API key",
        password=True,
        password_toggle_button=True,
    ).classes("w-full")

    ui.label(
        "Leave the API key blank to keep the saved key unchanged."
    ).classes("text-sm text-gray-500")

    status = ui.label("").classes("text-sm")

    def update_provider_defaults():
        defaults = PROVIDER_DEFAULTS[provider.value]
        endpoint.value = defaults["base_url"]
        model.value = defaults["model"]

    provider.on_value_change(
        lambda _: update_provider_defaults()
    )

    def save_settings():
        try:
            save_ai_config(
                provider=provider.value,
                base_url=endpoint.value,
                model=model.value,
                api_key=api_key.value,
            )

            api_key.value = ""
            status.set_text("Settings saved successfully.")
            status.classes(
                remove="text-red-700",
                add="text-green-700",
            )
            ui.notify("Settings saved successfully.", type="positive")

        except Exception as error:
            status.set_text(f"Could not save settings: {error}")
            status.classes(
                remove="text-green-700",
                add="text-red-700",
            )
            ui.notify("Could not save settings.", type="negative")

    def test_connection():
        try:
            save_ai_config(
                provider=provider.value,
                base_url=endpoint.value,
                model=model.value,
                api_key=api_key.value,
            )

            api_key.value = ""

            config = load_ai_config()

            client = OpenAI(
                base_url=config.base_url,
                api_key=config.api_key,
                timeout=15.0,
            )

            response = client.chat.completions.create(
                model=config.model,
                messages=[
                    {
                        "role": "user",
                        "content": "Reply with OK.",
                    }
                ],
                max_completion_tokens=256,
            )

            if response.choices and response.choices[0].message.content:
                status.set_text(
                    f"Connection successful. Model: {config.model}"
                )
                status.classes(
                    remove="text-red-700",
                    add="text-green-700",
                )
                ui.notify(
                    "AI connection successful.",
                    type="positive",
                )
            else:
                status.set_text(
                    "The model responded, but returned no text."
                )
                status.classes(
                    remove="text-green-700",
                    add="text-red-700",
                )

        except Exception as error:
            config = load_ai_config()

            details = str(error)

            if config.api_key:
                details = details.replace(
                    config.api_key,
                    "[REDACTED]",
                )

            details = details[:500]

            status.set_text(
                f"Connection failed ({type(error).__name__}): "
                f"{details}"
            )
            status.classes(
                remove="text-green-700",
                add="text-red-700",
            )

            ui.notify(
                f"Connection failed: {type(error).__name__}",
                type="negative",
            )

    ui.button(
        "Save settings",
        on_click=save_settings,
    ).props("color=primary")

    ui.button(
        "Test connection",
        on_click=test_connection,
    ).props("outline")

    ui.separator()

    ui.label(
    "Saving settings stores your configuration. "
    "Use Test connection to verify that the selected AI provider responds."
    ).classes("text-sm text-gray-500")


@ui.page("/settings")
def settings_page():
    create_header()

    with ui.row().classes("w-full min-h-screen"):
        create_navigation()

        with ui.column().classes("flex-1 max-w-3xl p-8 gap-4"):
            ui.label("Settings").classes("text-3xl font-bold")

            ui.label(
                "Configure the AI provider used by RegAI."
            ).classes("text-gray-600")

            with ui.card().classes("w-full p-6 gap-4"):
                create_settings_page()


@ui.page("/assessment")
def assessment_page():
    create_header()

    with ui.row().classes("w-full min-h-screen"):
        create_navigation()

        with ui.column().classes("flex-1 p-8 gap-6"):
            ui.label("Assessment").classes("text-3xl font-bold")

            ui.label(
                "Assess selected regulatory requirements against saved evidence sources."
            ).classes("text-gray-600")

            regulatory_documents = [
                document
                for document in [
                    regulatory_store.get_document("gdpr_sample")
                ]
                if document is not None
            ]

            evidence_sources = evidence_store.get_sources()

            if not regulatory_documents:
                ui.label(
                    "No regulatory documents are available. "
                    "Import a regulatory document before assessing."
                ).classes("text-amber-800 bg-amber-50 p-4 rounded")

            elif not evidence_sources:
                ui.label(
                    "No evidence sources are available. "
                    "Import a webpage on the Documents page first."
                ).classes("text-amber-800 bg-amber-50 p-4 rounded")

            else:
                regulatory_document = ui.select(
                    options={
                        document.source: document.title
                        for document in regulatory_documents
                    },
                    value=regulatory_documents[0].source,
                    label="Regulatory document",
                ).classes("w-full max-w-2xl")

                evidence_source_select = ui.select(
                    options={
                        source.url: (
                            source.chunks[0].page_title
                            if source.chunks
                            and source.chunks[0].page_title
                            else source.url
                        )
                        for source in evidence_sources
                    },
                    value=[source.url for source in evidence_sources[:1]],
                    label="Evidence sources",
                    multiple=True,
                ).classes("w-full max-w-2xl")

                requirement_select = ui.select(
                    options={},
                    value=[],
                    label="Requirements to assess",
                    multiple=True,
                ).classes("w-full max-w-2xl")

                result_area = ui.column().classes(
                    "w-full max-w-5xl gap-4"
                )

                def update_requirements():
                    document = regulatory_store.get_document(
                        regulatory_document.value
                    )

                    if document is None:
                        requirement_select.options = {}
                        requirement_select.value = []
                        requirement_select.update()
                        return

                    requirement_select.options = {
                        requirement.requirement_id: (
                            f"Article {requirement.section} — "
                            f"{requirement.analysis.topic}"
                        )
                        for requirement in document.requirements
                    }

                    requirement_select.value = []
                    requirement_select.update()

                regulatory_document.on_value_change(
                    lambda _: update_requirements()
                )

                update_requirements()

                def select_all_requirements():
                    requirement_select.value = list(
                        requirement_select.options.keys()
                    )
                    requirement_select.update()

                def clear_requirement_selection():
                    requirement_select.value = []
                    requirement_select.update()

                with ui.row().classes("gap-2"):
                    ui.button(
                        "Select all requirements",
                        on_click=select_all_requirements,
                    ).props("outline")

                    ui.button(
                        "Clear selection",
                        on_click=clear_requirement_selection,
                    ).props("outline")

                async def run_assessment():
                    result_area.clear()

                    document = regulatory_store.get_document(
                        regulatory_document.value
                    )

                    if document is None:
                        with result_area:
                            ui.label(
                                "The selected regulatory document "
                                "could not be loaded."
                            ).classes("text-red-700")
                        return

                    selected_ids = set(
                        requirement_select.value or []
                    )

                    selected_requirements = [
                        requirement
                        for requirement in document.requirements
                        if requirement.requirement_id in selected_ids
                    ]

                    if not selected_requirements:
                        with result_area:
                            ui.label(
                                "Select at least one requirement to assess."
                            ).classes(
                                "text-amber-800 bg-amber-50 p-4 rounded"
                            )
                        return

                    selected_urls = set(
                        evidence_source_select.value or []
                    )

                    selected_sources = [
                        source
                        for source in evidence_store.get_sources()
                        if source.url in selected_urls
                    ]

                    evidence_chunks = [
                        chunk
                        for source in selected_sources
                        for chunk in source.chunks
                    ]

                    if not evidence_chunks:
                        with result_area:
                            ui.label(
                                "The selected evidence sources contain "
                                "no stored evidence sections."
                            ).classes(
                                "text-amber-800 bg-amber-50 p-4 rounded"
                            )
                        return

                    with result_area:
                        ui.label(
                            f"Assessing {len(selected_requirements)} "
                            f"requirements against "
                            f"{len(evidence_chunks)} evidence sections..."
                        ).classes("text-gray-600")

                    try:
                        def perform_assessment():
                            embedding_provider = LocalEmbeddingProvider()

                            retriever = EvidenceRetriever(
                                embedding_provider=embedding_provider,
                                chunks=evidence_chunks,
                            )

                            results = []

                            for requirement in selected_requirements:
                                try:
                                    result = assess_regulatory_requirement(
                                        requirement=requirement,
                                        evidence_retriever=retriever,
                                    )
                                    results.append((requirement, result, None))
                                except Exception as error:
                                    results.append(
                                        (requirement, None, error)
                                    )

                            return results

                        results = await run.io_bound(
                            perform_assessment
                        )

                        result_area.clear()

                        status_labels = {
                            "supported": "Supported",
                            "insufficient": "Insufficient evidence",
                            "potential_gap": "Potential gap",
                        }

                        status_counts = {
                            "supported": 0,
                            "insufficient": 0,
                            "potential_gap": 0,
                            "not_assessed": 0,
                        }

                        for _, result, error in results:
                            if error is not None or result is None:
                                status_counts["not_assessed"] += 1
                            else:
                                status_counts[result.assessment.value] += 1

                        with result_area:
                            ui.separator()

                            ui.label(
                                "Assessment report"
                            ).classes("text-2xl font-semibold")

                            ui.label(
                                f"Regulatory document: {document.title}"
                            ).classes("text-gray-600")

                            ui.label(
                                f"Requirements assessed: {len(results)}"
                            ).classes("text-gray-600")

                            ui.label(
                                f"Evidence sections available: "
                                f"{len(evidence_chunks)}"
                            ).classes("text-gray-600")

                            with ui.row().classes("w-full gap-3"):
                                for status, count in status_counts.items():
                                    label = (
                                        "Not assessed"
                                        if status == "not_assessed"
                                        else status_labels[status]
                                    )

                                    with ui.card().classes(
                                        "p-4 min-w-36"
                                    ):
                                        ui.label(label).classes(
                                            "text-sm text-gray-600"
                                        )
                                        ui.label(str(count)).classes(
                                            "text-2xl font-bold"
                                        )

                            ui.separator()

                            ui.label(
                                "Individual findings"
                            ).classes("text-xl font-semibold")

                            for requirement, result, error in results:
                                if error is not None:
                                    status = "Not assessed"
                                    explanation = (
                                        f"Assessment failed "
                                        f"({type(error).__name__}): "
                                        f"{str(error)[:300]}"
                                    )
                                elif result is None:
                                    status = "Not assessed"
                                    explanation = (
                                        "No evidence candidates were "
                                        "available for assessment."
                                    )
                                else:
                                    status = status_labels[
                                        result.assessment.value
                                    ]
                                    explanation = result.explanation

                                with ui.expansion(
                                    f"Article {requirement.section} — "
                                    f"{requirement.analysis.topic} — "
                                    f"{status}"
                                ).classes("w-full"):
                                    ui.label(
                                        f"Requirement ID: "
                                        f"{requirement.requirement_id}"
                                    ).classes("text-sm text-gray-600")

                                    ui.label(
                                        "Original regulatory text"
                                    ).classes("font-semibold")

                                    ui.label(
                                        requirement.original_text
                                    ).classes("whitespace-pre-wrap")

                                    ui.label(
                                        "Interpretation"
                                    ).classes("font-semibold")

                                    ui.label(
                                        requirement.analysis.interpretation
                                    ).classes("whitespace-pre-wrap")

                                    ui.label(
                                        "Assessment explanation"
                                    ).classes("font-semibold")

                                    ui.label(
                                        explanation
                                    ).classes("whitespace-pre-wrap")

                            ui.separator()

                            ui.label(
                                "Evidence sources included in this run"
                            ).classes("text-xl font-semibold")

                            for source in selected_sources:
                                with ui.expansion(
                                    source.url
                                ).classes("w-full"):
                                    for chunk in source.chunks:
                                        with ui.expansion(
                                            chunk.section_heading
                                            or "Untitled section"
                                        ).classes("w-full"):
                                            ui.label(
                                                chunk.text
                                            ).classes("whitespace-pre-wrap")

                                            ui.label(
                                                f"Evidence ID: {chunk.chunk_id}"
                                            ).classes(
                                                "text-xs text-gray-500"
                                            )

                                            ui.label(
                                                f"Source URL: {chunk.source_url}"
                                            ).classes(
                                                "text-sm text-gray-600"
                                            )

                    except Exception as error:
                        result_area.clear()

                        with result_area:
                            ui.label(
                                f"Assessment run failed "
                                f"({type(error).__name__}): "
                                f"{str(error)[:300]}"
                            ).classes(
                                "text-red-700 bg-red-50 p-4 rounded"
                            )

                ui.button(
                    "Run assessment",
                    on_click=run_assessment,
                ).props("color=primary")

                ui.label(
                    "Assessments are AI-generated findings, not legal "
                    "determinations of compliance. 'Not assessed' means "
                    "no assessment result was produced; it is not a "
                    "regulatory finding."
                ).classes("text-sm text-gray-500")

    create_header()

@ui.page("/documents")
def documents_page():
    create_header()

    with ui.row().classes("w-full min-h-screen"):
        create_navigation()

        with ui.column().classes("flex-1 p-8 gap-6"):
            ui.label("Documents").classes("text-3xl font-bold")

            ui.label(
                "Import a webpage and inspect the evidence extracted from it."
            ).classes("text-gray-600")

            ui.label("Saved sources").classes(
                "text-2xl font-semibold"
            )

            saved_sources = ui.column().classes(
                "w-full max-w-4xl gap-4"
            )

            def refresh_saved_sources():
                saved_sources.clear()

                sources = evidence_store.get_sources()

                if not sources:
                    with saved_sources:
                        ui.label(
                            "No webpages have been imported yet."
                        ).classes("text-gray-500")
                    return

                with saved_sources:
                    for source in sources:
                        with ui.card().classes("w-full"):
                            title = (
                                source.chunks[0].page_title
                                if source.chunks
                                else None
                            )

                            ui.label(
                                title or "Untitled webpage"
                            ).classes("text-lg font-semibold")

                            ui.label(
                                source.url
                            ).classes("text-sm text-gray-600")

                            ui.label(
                                f"Retrieved: {source.retrieval_date} "
                                f"| Evidence sections: {len(source.chunks)}"
                            ).classes("text-sm text-gray-600")

                            with ui.expansion(
                                "View extracted evidence"
                            ).classes("w-full"):
                                for chunk in source.chunks:
                                    ui.separator()

                                    ui.label(
                                        chunk.section_heading
                                        or "Untitled section"
                                    ).classes("font-semibold")

                                    ui.label(chunk.text).classes(
                                        "whitespace-pre-wrap"
                                    )

                                    ui.label(
                                        f"Evidence ID: {chunk.chunk_id}"
                                    ).classes("text-xs text-gray-500")

            refresh_saved_sources()
            ui.separator()

            ui.label("Regulatory documents").classes(
                "text-2xl font-semibold"
            )

            for document in [
                regulatory_store.get_document("gdpr_sample")
            ]:
                if document is not None:
                    with ui.card().classes("w-full max-w-4xl"):
                        ui.label(document.title).classes(
                            "text-lg font-semibold"
                        )

                        ui.label(
                            f"Source ID: {document.source}"
                        ).classes("text-sm text-gray-600")

                        ui.label(
                            f"Effective date: "
                            f"{document.effective_date or 'Not specified'}"
                        ).classes("text-sm text-gray-600")

                        ui.label(
                            f"Requirements: {len(document.requirements)}"
                        ).classes("text-sm text-gray-600")

                        with ui.expansion(
                            "View regulatory requirements"
                        ).classes("w-full"):
                            for requirement in document.requirements:
                                ui.separator()

                                ui.label(
                                    f"Article {requirement.section}"
                                ).classes("font-semibold")

                                ui.label(
                                    requirement.analysis.topic
                                ).classes("text-md font-semibold")

                                ui.label(
                                    requirement.analysis.interpretation
                                ).classes("text-gray-700")

                                ui.label(
                                    requirement.original_text
                                ).classes("text-sm whitespace-pre-wrap")

                                ui.label(
                                    f"Requirement ID: "
                                    f"{requirement.requirement_id}"
                                ).classes("text-xs text-gray-500")

            with ui.card().classes("w-full max-w-4xl p-6 gap-4"):
                url_input = ui.input(
                    label="Webpage URL",
                    placeholder="https://example.com/privacy",
                ).classes("w-full")

                status = ui.label("").classes("text-sm")
                results = ui.column().classes("w-full gap-4")

                async def import_url():
                    url = (url_input.value or "").strip()

                    if not url.startswith(("https://", "http://")):
                        status.set_text(
                            "Enter a valid URL beginning with http:// or https://."
                        )
                        status.classes(
                            remove="text-green-700",
                            add="text-red-700",
                        )
                        return

                    results.clear()
                    status.set_text("Fetching webpage...")
                    status.classes(
                        remove="text-red-700",
                        add="text-gray-600",
                    )

                    try:
                        source = await run.io_bound(
                            fetch_web_page,
                            url,
                        )

                        retrieval_date = datetime.now(
                            timezone.utc
                        ).date().isoformat()

                        chunks = process_evidence_source(
                            source,
                            retrieval_date,
                        )

                        evidence_store.save_source(
                            source_type=source.source_type,
                            url=source.url,
                            retrieval_date=retrieval_date,
                            chunks=chunks,
                        )

                        refresh_saved_sources()

                        with results:
                            ui.label("Imported source").classes(
                                "text-xl font-semibold"
                            )

                            ui.label(
                                f"Final URL: {source.url}"
                            ).classes("text-sm text-gray-600")

                            ui.label(
                                f"Retrieval date: {retrieval_date}"
                            ).classes("text-sm text-gray-600")

                            if chunks and chunks[0].page_title:
                                ui.label(
                                    f"Page title: {chunks[0].page_title}"
                                ).classes("text-sm text-gray-600")

                            ui.label(
                                f"Evidence sections extracted: {len(chunks)}"
                            ).classes("text-lg font-semibold")

                            if not chunks:
                                ui.label(
                                    "The page was fetched, but no evidence "
                                    "sections were extracted."
                                ).classes("text-amber-800")

                            for chunk in chunks:
                                with ui.card().classes("w-full"):
                                    ui.label(
                                        chunk.section_heading
                                        or "Untitled section"
                                    ).classes("text-lg font-semibold")

                                    ui.label(chunk.text).classes(
                                        "whitespace-pre-wrap"
                                    )

                                    ui.label(
                                        f"Evidence ID: {chunk.chunk_id}"
                                    ).classes("text-xs text-gray-500")

                        status.set_text("Webpage imported successfully.")
                        status.classes(
                            remove="text-red-700",
                            add="text-green-700",
                        )

                    except Exception as error:
                        status.set_text(
                            f"Import failed ({type(error).__name__}): "
                            f"{str(error)[:300]}"
                        )
                        status.classes(
                            remove="text-green-700",
                            add="text-red-700",
                        )

                ui.button(
                    "Import URL",
                    on_click=import_url,
                ).props("color=primary")


ui.run(
    title=APP_NAME,
    host="127.0.0.1",
    port=8080,
    reload=False,
    show=True,
)