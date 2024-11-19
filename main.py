import os
import time
from pathlib import Path
from uuid import UUID

import pydicom
from encord.orm.storage import (
    CustomerProvidedDicomSeriesDicomFileMetadata,
    DataUploadDicomSeries,
    DataUploadDicomSeriesDicomFile,
    DataUploadItems,
)
from encord.user_client import EncordUserClient

REQUIRED_DICOM_TAGS = [
    "00080018",  # SOPInstanceUID
    "00100020",  # PatientID
    "00180050",  # SliceThickness
    "00181114",  # EstimatedRadiographicMagnificationFactor
    "00181164",  # ImagerPixelSpacing
    "0020000D",  # StudyInstanceUID
    "0020000E",  # SeriesInstanceUID
    "00200013",  # InstanceNumber
    "00200032",  # ImagePositionPatient
    "00200037",  # ImageOrientationPatient
    "00209113",  # PlanePositionSequence
    "00209116",  # PlaneOrientationSequence
    "00280004",  # PhotometricInterpretation
    "00280008",  # NumberOfFrames
    "00280010",  # Rows
    "00280011",  # Columns
    "00280030",  # PixelSpacing
    "00281050",  # WindowCenter
    "00281051",  # WindowWidth
    "00289110",  # PixelMeasuresSequence
    "52009229",  # SharedFunctionalGroupsSequence
    "52009230",  # PerFrameFunctionalGroupsSequence
]


def get_integration_uuid(user_client: EncordUserClient, title: str) -> UUID:
    integrations = [x for x in user_client.get_cloud_integrations() if x.title == title]

    if len(integrations) == 0:
        raise ValueError(
            f"get_integration_uuid error, no integration found with {title=}"
        )

    if len(integrations) > 1:
        raise ValueError(
            f"get_integration_uuid error, multiple integrations found with {title=}"
        )

    return UUID(integrations[0].id)


def pydicom_dataset_to_metadata_tags(pydicom_dataset: pydicom.Dataset) -> dict:
    tags = pydicom_dataset.to_json_dict()

    return {x: tags.get(x) for x in REQUIRED_DICOM_TAGS}


def main(
    ssh_private_key_path: Path,
    cloud_integration_title: str,
    dicom_dir: Path,
):
    if not ssh_private_key_path.is_file():
        raise ValueError(f"{ssh_private_key_path=} does not exist")

    if not dicom_dir.is_dir():
        raise ValueError(f"{dicom_dir=} does not exist")

    user_client = EncordUserClient.create_with_ssh_private_key(
        ssh_private_key_path=ssh_private_key_path,
    )
    storage_folder = user_client.create_storage_folder(
        name=f"dicom data folder {int(time.time())}"
    )
    integration_uuid = get_integration_uuid(user_client, cloud_integration_title)

    print(f"main-log: found integration {integration_uuid=} ")

    dicom_series_map = {
        dicom_series_path.name: [
            dicom_file_path.name
            for dicom_file_path in sorted(dicom_series_path.iterdir())
        ]
        for dicom_series_path in sorted(dicom_dir.iterdir())
    }

    print(f"main-log: found dicom series {len(dicom_series_map)=} ")

    upload_job_uuid = storage_folder.add_private_data_to_folder_start(
        str(integration_uuid),
        DataUploadItems(
            dicom_series=[
                DataUploadDicomSeries(
                    title=f"dicom series - {dicom_series_name}",
                    dicom_files=[
                        DataUploadDicomSeriesDicomFile(  # type: ignore[call-arg]
                            url=f"https://custom-direct-access-url.com/{dicom_series_name}/{dicom_file}",
                            title=f"dicom file - {dicom_series_name}/{dicom_file}",
                            dicom_metadata=CustomerProvidedDicomSeriesDicomFileMetadata(
                                tags=pydicom_dataset_to_metadata_tags(
                                    pydicom.dcmread(
                                        dicom_dir / dicom_series_name / dicom_file,
                                        force=True,
                                    ),
                                ),
                            ),
                        )
                        for dicom_file in dicom_series_map[dicom_series_name]
                    ],
                )
                for dicom_series_name in dicom_series_map
            ],
        ),
        True,
    )

    print(f"main-log: {upload_job_uuid=} upload job started")

    res = storage_folder.add_private_data_to_folder_get_result(upload_job_uuid)

    print(f"main-log: {upload_job_uuid=} upload job done")
    print(f"main-log: {res.status=} {res.units_done_count=} {res.units_error_count=}")

    for item_success in res.items_with_names:
        print(
            f"main-log: dicom series integrated successfully "
            f"{item_success.item_uuid=} {item_success.name=}"
        )

    for item_error in res.unit_errors:
        print(
            f"main-log: dicom series integration error "
            f"{item_error.error=} {item_error.object_urls=}"
        )


if __name__ == "__main__":
    ssh_private_key_path = Path(os.environ["ENCORD_SSH_KEY_FILE"]).resolve()
    # type of Encord integration: direct - client only
    cloud_integration_title = os.environ["CLOUD_INTEGRATION_TITLE"]
    dicom_dir = Path(os.environ["DICOM_DIR"]).resolve()

    main(
        ssh_private_key_path,
        cloud_integration_title,
        dicom_dir,
    )
