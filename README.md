# Encord DICOM Direct Access Integration Demo

This project demonstrates how to integrate DICOM series metadata with Encord using the Python client library. It shows how to read DICOM files, extract required metadata tags, and upload them through Encord's SDK.

## Project Structure

```
.
├── dicom-data/                          # Sample DICOM series files
│   ├── sample-dicom-series-0-correct/   # Valid DICOM series
│   ├── sample-dicom-series-1-correct/   # Valid DICOM series
│   └── sample-dicom-series-2-invalid/   # Invalid DICOM series (mismatched StudyInstanceUID)
├── main.py                              # Main integration script
├── main.sh                              # Shell script to run the integration
├── pyproject.toml                       # Poetry project configuration
└── poetry.lock                          # Poetry dependencies lock file
```

## Prerequisites

- Python 3.11+
- Poetry for dependency management
- Encord SSH private key for authentication
- Direct client-only cloud integration configured in Encord

## Setup

1. Install dependencies using Poetry:
```bash
poetry install
```

2. Set up your SSH key:
   - Copy `encord-dicom-metadata-upload-private-key.ed25519.example` to `encord-dicom-metadata-upload-private-key.ed25519`
   - Replace the content with your actual Encord SSH private key

3. Configure your cloud integration in Encord:
   - Create a direct client-only integration
   - Name it 'dicom-metadata-upload-integration' (or update `CLOUD_INTEGRATION_TITLE` in `main.sh`)

## Usage

1. Place your DICOM series in the `dicom-data` directory:
   - Each series should be in its own subdirectory
   - Files within a series must have consistent StudyInstanceUID values

2. Run the integration:
```bash
bash main.sh
```

## Example Output

The script will output progress information like this:
```
main-log: found integration integration_uuid=UUID('8d1e3397-a16c-4968-86b3-a0b852f0f683')
main-log: found dicom series len(dicom_series_map)=3
main-log: upload_job_uuid=UUID('6e321e47-c18e-4a81-893b-dc42667997af') upload job started
main-log: upload_job_uuid=UUID('6e321e47-c18e-4a81-893b-dc42667997af') upload job done
main-log: res.status=<LongPollingStatus.DONE: 'DONE'> res.units_done_count=2 res.units_error_count=1
main-log: dicom series integrated successfully item_success.item_uuid=UUID('8b3e06fe-8e79-4159-a7de-6124b156534d') item_success.name='dicom series - sample-dicom-series-0-correct'
main-log: dicom series integrated successfully item_success.item_uuid=UUID('03db66b5-b6ef-4e6a-8b38-86cbdf648848') item_success.name='dicom series - sample-dicom-series-1-correct'
main-log: dicom series integration error item_error.error="The value of DICOM tag 'StudyInstanceUID' should be consistent across files in a series. Got [1.3.6.1.4.1.5962.99.1.1761388472.1291962045.1616669124536.2592.0] from 'dicom file - sample-dicom-series-2-invalid/sample-dicom-series-2-invalid-1.dcm' and [1.3.6.1.4.1.5962.99.1.5128099.2103784727.1533308485539.4.0] from other files in the series." item_error.object_urls=['https://custom-direct-access-url.com/sample-dicom-series-2-invalid/sample-dicom-series-2-invalid-0.dcm', 'https://custom-direct-access-url.com/sample-dicom-series-2-invalid/sample-dicom-series-2-invalid-1.dcm']
```

### Success and Error Handling

- Successful uploads will show:
```
main-log: dicom series integrated successfully item_success.item_uuid=UUID('8b3e06fe-8e79-4159-a7de-6124b156534d') item_success.name='dicom series - sample-dicom-series-0-correct'
```

- Failed uploads will show detailed error messages:
```
main-log: dicom series integration error item_error.error="The value of DICOM tag 'StudyInstanceUID' should be consistent across files in a series. Got [1.3.6.1.4.1.5962.99.1.1761388472.1291962045.1616669124536.2592.0] from 'dicom file - sample-dicom-series-2-invalid/sample-dicom-series-2-invalid-1.dcm' and [1.3.6.1.4.1.5962.99.1.5128099.2103784727.1533308485539.4.0] from other files in the series." item_error.object_urls=['https://custom-direct-access-url.com/sample-dicom-series-2-invalid/sample-dicom-series-2-invalid-0.dcm', 'https://custom-direct-access-url.com/sample-dicom-series-2-invalid/sample-dicom-series-2-invalid-1.dcm']
```

## DICOM Metadata Validation (happening during data upload)

### 1. StudyInstanceUID Validation
- Our system automatically verifies that all DICOM files within a series share the same StudyInstanceUID
- You'll receive a detailed error message identifying any files with mismatched StudyInstanceUIDs

### 2. Required Tags Verification
Our validation automatically confirms the presence of all critical DICOM tags:
- StudyInstanceUID (0020,000D)
- SeriesInstanceUID (0020,000E)
- SOPInstanceUID (0008,0018)
- PatientID (0010,0020)
- Columns & Rows for image dimensions

If any tags are missing, our system will provide a precise error message indicating which tag is absent from which file.

### 3. UID Validation
Our system automatically:
- Validates that all UIDs are within the 1-64 character limit
- Accepts non-standard UID formats while maintaining compatibility
- Reports any invalid characters or length violations

### 4. SOPInstanceUID Uniqueness Check
- Our validation automatically detects duplicate SOPInstanceUIDs within a series
- You'll receive error message if duplicates are found

## Spatial Information Validation

### 5. Image Dimension Consistency
Our system automatically:
- Verifies consistent width/height across all images in a series
- Flags any files with different matrix sizes
- Ensures 3D volume reconstruction compatibility

### 6. Spatial Metadata Verification
We automatically validate the presence of:
- Image Position Patient
- Image Orientation Patient
- Pixel Spacing
- Slice Thickness

Our system will alert you if any spatial metadata is missing or incorrect.

### 7. Slice Spacing Analysis
Our validation:
- Automatically measures Z-axis spacing between slices
- Verifies 97% of spacings fall within tolerance
- Alerts you to any irregular spacing that could affect 3D reconstruction

### 8. Orientation Validation
- Automatic verification of image orientation vector consistency
- Detection of accidentally flipped or rotated acquisitions
- Ensures MPR view compatibility

## Multi-frame DICOM Validation

### 9. Frame Validation
Our system automatically:
- Verifies NumberOfFrames tag validity
- Checks frame indexing consistency
- Alerts you to any frame sequence issues

### 10. Window Settings Verification
- Automatic validation of Window Width/Center consistency
- Built-in calculation of optimal global window settings
- Notification of any display parameter inconsistencies

Our comprehensive validation system ensures your DICOM data meets all required standards without manual checking. You'll receive clear notifications and guidance if any issues are detected.
