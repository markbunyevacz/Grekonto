# Gemini Structured Outputs Integration

This document describes the integration of Google Gemini 3 Pro Preview with structured outputs for PDF invoice and form extraction.

## Overview

The Gemini integration uses the [structured outputs feature](https://ai.google.dev/gemini-api/docs/structured-outputs) with Pydantic models to extract structured data from PDF documents. This provides:

- **Guaranteed schema compliance**: Responses always match the defined Pydantic model
- **Type safety**: Automatic validation and type conversion
- **Rich extraction**: Can extract complex nested structures (items, line items, etc.)
- **Flexible**: Easy to extend with custom Pydantic models for different document types

## Installation

The required dependencies are already in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Required packages:
- `google-genai>=1.0.0` - Google Gemini API SDK
- `pydantic>=2.0.0` - Data validation and structured outputs

## Configuration

### Environment Variables

Set the following environment variables:

```bash
# Required for Gemini extraction
GOOGLE_API_KEY=your_api_key_here

# Optional: Model selection (default: gemini-3-pro-preview)
GEMINI_MODEL_ID=gemini-3-pro-preview

# Optional: Choose OCR provider (default: azure)
# Set to "gemini" to use Gemini, "azure" to use Azure Document Intelligence
OCR_PROVIDER=gemini
```

### Getting an API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and set it as `GOOGLE_API_KEY`

## Usage

### Basic Invoice Extraction

```python
from shared.gemini_extractor import GeminiExtractor

# Initialize extractor
extractor = GeminiExtractor(api_key="your_key", model_id="gemini-3-pro-preview")

# Read PDF
with open("invoice.pdf", "rb") as f:
    pdf_content = f.read()

# Extract data
result = extractor.extract_from_invoice(pdf_content, filename="invoice.pdf")

# Access results
print(f"Company: {result['company']}")
print(f"Date: {result['date']}")
print(f"Total: {result['total']}")
print(f"Invoice Number: {result.get('invoice_number')}")
print(f"Items: {result.get('items', [])}")
```

### Custom Form Extraction

You can define custom Pydantic models for different form types:

```python
from pydantic import BaseModel, Field
from shared.gemini_extractor import GeminiExtractor

class CustomForm(BaseModel):
    form_number: str = Field(description="The form number")
    start_date: str = Field(description="Effective date")
    beginning_of_year: float = Field(description="Plan liabilities beginning of year")
    end_of_year: float = Field(description="Plan liabilities end of year")

extractor = GeminiExtractor(api_key="your_key")
result = extractor.extract_from_form(
    document_content=pdf_content,
    form_schema=CustomForm,
    filename="form.pdf"
)
```

### Testing

Use the provided test script:

```bash
export GOOGLE_API_KEY=your_key
python test_gemini_extractor.py path/to/invoice.pdf
```

## Integration with Processing Pipeline

The Gemini extractor is integrated into the document processing pipeline. To use it:

1. Set `OCR_PROVIDER=gemini` in your environment
2. Set `GOOGLE_API_KEY` with your API key
3. The queue worker will automatically use Gemini for extraction

The extracted data format is compatible with the existing Azure OCR format, so no changes are needed to downstream processing.

## Data Format

The extractor returns data in SROIE-compatible format:

```python
{
    "company": "Vendor Name",      # Normalized text
    "date": "DD/MM/YYYY",           # Normalized date
    "address": "Full Address",      # Normalized text
    "total": "1234.56",             # Normalized amount (2 decimals)
    "confidence": 0.95,             # Confidence score (0-1)
    "invoice_number": "INV-123",    # Optional: Invoice number
    "items": [                      # Optional: Line items
        {
            "description": "Item description",
            "quantity": 2.0,
            "gross_worth": 100.0
        }
    ],
    "total_gross_worth": 200.0      # Optional: Total gross worth
}
```

## Model Selection

Available Gemini models:

- `gemini-3-pro-preview` - Latest preview model (recommended for structured outputs)
- `gemini-2.5-pro` - Stable production model
- `gemini-2.5-flash` - Faster, lower cost (free tier: 1,500 requests/day)
- `gemini-2.5-flash-lite` - Lightweight version

**Note**: Structured outputs work best with `gemini-3-pro-preview` or `gemini-2.5-pro`.

## Cost Considerations

- **File uploads**: Free (files stored for 48 hours)
- **Token usage**: Varies by model and document size
- **Free tier**: Gemini 2.5 Flash offers 1,500 requests/day for free

Check token usage:
```python
token_count = client.models.count_tokens(model=model_id, contents=uploaded_file)
print(f"Tokens: {token_count.total_tokens}")
```

## Comparison: Azure vs Gemini

| Feature | Azure Document Intelligence | Gemini Structured Outputs |
|---------|----------------------------|---------------------------|
| Schema compliance | Field-level confidence | Guaranteed schema match |
| Custom fields | Predefined models | Fully customizable Pydantic models |
| Line items | Basic extraction | Rich nested structures |
| Cost | Pay per page | Pay per token (free tier available) |
| Speed | Fast | Moderate (API call overhead) |
| Accuracy | High for standard invoices | High, with better context understanding |

## Troubleshooting

### API Key Issues
```
ValueError: GOOGLE_API_KEY environment variable or api_key parameter required
```
**Solution**: Set the `GOOGLE_API_KEY` environment variable.

### File Upload Errors
```
Error uploading file to Gemini API
```
**Solution**: Check file size (max 2GB), network connectivity, and API key validity.

### Schema Validation Errors
```
Pydantic validation error
```
**Solution**: The model ensures schema compliance. Check that your Pydantic model fields match the document structure.

### Model Not Found
```
Model gemini-3-pro-preview not found
```
**Solution**: Use a supported model like `gemini-2.5-pro` or `gemini-2.5-flash`.

## References

- [Gemini Cookbook - PDF Structured Outputs](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Pdf_structured_outputs_on_invoices_and_forms.ipynb)
- [Google Genai Python SDK](https://googleapis.github.io/python-genai/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
