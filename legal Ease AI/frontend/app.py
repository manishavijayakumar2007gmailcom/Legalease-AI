import os
import sys
from datetime import date

import requests
import streamlit as st
from dotenv import load_dotenv


# ---------------------------------------------------------
# Make project root available
# ---------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:

    sys.path.insert(
        0,
        PROJECT_ROOT,
    )


from services.document_export import (
    export_docx,
    export_pdf,
    export_txt,
)

from services.text_utils import (
    format_html_preview,
)


load_dotenv(
    os.path.join(
        PROJECT_ROOT,
        ".env",
    )
)


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        text-align: center;
        color: #666666;
        font-size: 18px;
        margin-bottom: 25px;
    }

    .preview-box {
        background: #ffffff;
        color: #111111;
        border: 1px solid #dddddd;
        border-radius: 12px;
        padding: 30px;
        max-height: 650px;
        overflow-y: auto;
        line-height: 1.7;
    }

    .preview-box h3 {
        margin-top: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

logo_path = os.path.join(
    PROJECT_ROOT,
    "assets",
    "logo.svg",
)

if os.path.exists(logo_path):

    st.image(
        logo_path,
        width=230,
    )

st.markdown(
    '<div class="main-title">LegalEase</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Legal Document Generator'
    '</div>',
    unsafe_allow_html=True,
)


st.info(
    "LegalEase creates AI-assisted legal document drafts. "
    "Review generated documents with a qualified legal "
    "professional before using them for legal purposes."
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:

    st.header(
        "Document Settings"
    )

    document_type = st.selectbox(
        "Document Type",
        [
            "Employment Contract",
            "Lease Agreement",
            "Non-Disclosure Agreement",
            "Service Agreement",
            "Partnership Agreement",
            "Freelance Work Contract",
            "Employment Offer Letter",
            "Legal Notice",
            "General Agreement",
            "Custom Legal Document",
        ],
    )

    jurisdiction = st.text_input(
        "Jurisdiction",
        value="India",
    )

    effective_date = st.date_input(
        "Effective Date",
        value=date.today(),
    )

    st.divider()

    st.caption(
        "Backend:"
    )

    st.code(
        BACKEND_URL
    )


# ---------------------------------------------------------
# Input Section
# ---------------------------------------------------------

st.header(
    "Create Your Legal Document"
)

col1, col2 = st.columns(2)

with col1:

    parties = st.text_area(
        "Parties Involved",
        placeholder=(
            "Example:\n"
            "Jane Doe (Service Provider)\n"
            "TechNova Inc. (Client)"
        ),
        height=150,
    )


with col2:

    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Enter terms separated by semicolons.\n\n"
            "Example:\n"
            "Payment within 30 days; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),
        height=150,
    )


additional_instructions = st.text_area(
    "Additional Instructions",
    placeholder=(
        "Optional instructions for the AI.\n"
        "Example: Include a detailed confidentiality clause."
    ),
    height=120,
)


# ---------------------------------------------------------
# Generate
# ---------------------------------------------------------

generate_button = st.button(
    "✨ Generate Document",
    type="primary",
    use_container_width=True,
)


if generate_button:

    if not parties.strip():

        st.error(
            "Please enter the parties involved."
        )

        st.stop()

    if not terms.strip():

        st.error(
            "Please enter the terms and conditions."
        )

        st.stop()

    payload = {

        "document_type": document_type,

        "parties": parties,

        "terms": terms,

        "effective_date": str(
            effective_date
        ),

        "jurisdiction": jurisdiction,

        "additional_instructions":
            additional_instructions,
    }

    with st.spinner(
        "Generating your legal document..."
    ):

        try:

            response = requests.post(
                f"{BACKEND_URL}/generate",
                json=payload,
                timeout=180,
            )

            if response.status_code == 200:

                data = response.json()

                if data.get("success"):

                    st.session_state[
                        "document_text"
                    ] = data.get(
                        "document",
                        "",
                    )

                    st.success(
                        "Document generated successfully!"
                    )

                else:

                    st.error(
                        "The backend did not return a document."
                    )

            else:

                try:

                    error_data = (
                        response.json()
                    )

                    detail = error_data.get(
                        "detail",
                        "Unknown backend error",
                    )

                except Exception:

                    detail = response.text

                st.error(
                    f"Backend error: {detail}"
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "Cannot connect to the FastAPI backend.\n\n"
                "Please start the backend using:\n"
                "uvicorn backend.main:app --reload"
            )

        except requests.exceptions.Timeout:

            st.error(
                "The request timed out. "
                "Please check the Gemini API or try again."
            )

        except Exception as exc:

            st.error(
                f"Unexpected error: {exc}"
            )


# ---------------------------------------------------------
# Generated Document
# ---------------------------------------------------------

if "document_text" in st.session_state:

    st.divider()

    st.header(
        "Generated Document"
    )

    edited_document = st.text_area(
        "Edit Document",
        value=st.session_state[
            "document_text"
        ],
        height=600,
        key="editable_document",
    )

    st.session_state[
        "document_text"
    ] = edited_document

    # -----------------------------------------------------
    # Preview
    # -----------------------------------------------------

    st.subheader(
        "Document Preview"
    )

    preview_html = format_html_preview(
        edited_document
    )

    st.markdown(
        f"""
        <div class="preview-box">
            {preview_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # Downloads
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "Download Document"
    )

    txt_data = export_txt(
        edited_document
    )

    docx_data = export_docx(
        edited_document,
        document_type=document_type,
        terms=terms,
    )

    pdf_data = export_pdf(
        edited_document,
        document_type=document_type,
    )

    download_col1, download_col2, download_col3 = (
        st.columns(3)
    )

    with download_col1:

        st.download_button(
            "📄 Download TXT",
            data=txt_data,
            file_name="legalease_document.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with download_col2:

        st.download_button(
            "📝 Download DOCX",
            data=docx_data,
            file_name="legalease_document.docx",
            mime=(
                "application/"
                "vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            use_container_width=True,
        )

    with download_col3:

        st.download_button(
            "📕 Download PDF",
            data=pdf_data,
            file_name="legalease_document.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.divider()

st.caption(
    "LegalEase | AI-Assisted Legal Document Generator"
)