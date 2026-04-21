from dataclasses import dataclass

from .pipeline_action import PipelineAction


@dataclass
class FileWriteAction(PipelineAction):
    write_path: str
    file_name: str
