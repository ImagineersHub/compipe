# launch windows program from docker container
import requests
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from .parameters import ARG_APP_INVOKE
from compipe.runtime_env import Environment as env
from .singleton import Singleton
from datetime import datetime, timedelta
from .logging import logger
from typing import Dict


class AppInvokeDefinition(BaseModel):
    enable: bool = Field(
        default=False,
        description="Whether to enable the app invoke service"
    )

    host: str = Field(
        default="",
        description="The host address of the app invoke service"
    )

    execute: str = Field(
        default="",
        description="The endpoint for program execution"
    )

    launch: str = Field(
        default="",
        description="The endpoint for program launching"
    )

    kill: str = Field(
        default="",
        description="The endpoint for program termination"
    )

    @property
    def execute_url(self):
        return f"{self.host}/{self.execute}"

    @property
    def launch_url(self):
        return f"{self.host}/{self.launch}"

    @property
    def kill_url(self):
        return f"{self.host}/{self.kill}"


class ProgramExecutionRequest(BaseModel):
    ProgramPath: str = Field(
        default="",
        description="The path to the program to be executed"
    )

    Arguments: List[str] = Field(
        default_factory=list,
        description="List of command-line arguments to pass to the program"
    )

    WorkingDirectory: Optional[str] = Field(
        default=None,
        description="The working directory for the program execution"
    )

    Payload: Dict = Field(
        default_factory=dict,
        description="Additional data to be passed to the program"
    )

    TimeoutSeconds: Optional[int] = Field(
        default=None,
        description="Maximum execution time in seconds before termination"
    )

    Hidden: bool = Field(
        default=False,
        description="Whether to hide the program window in launching mode"
    )


class ProgramExecutionResult(BaseModel):
    success: bool
    exit_code: int = Field(alias='exitCode')
    standard_output: str = Field(default="", alias='standardOutput')
    standard_error: str = Field(default="", alias='standardError')
    start_time: datetime = Field(alias='startTime')
    end_time: datetime = Field(alias='endTime')
    timed_out: bool = Field(alias='timedOut')

    @property
    def duration(self) -> timedelta:
        return self.end_time - self.start_time

    class Config:
        from_attributes = True  # Allows parsing from ORM objects
        json_schema_extra = {
            "example": {
                "success": True,
                "exit_code": 0,
                "standard_output": "Program output",
                "standard_error": "",
                "start_time": "2024-01-01T10:00:00",
                "end_time": "2024-01-01T10:00:05",
                "timed_out": False
            }
        }


class AppInvokeService(metaclass=Singleton):

    def __init__(self):
        super().__init__()
        self.definition = AppInvokeDefinition(
            **env().get_value_by_path([ARG_APP_INVOKE])
        )

    @property
    def enabled(self):
        return self.definition.enable

    def call(
            self,
            url: str,
            request: ProgramExecutionRequest,
            timeout: Optional[int] = None
    ) -> ProgramExecutionResult:
        """
        Send a POST request to a REST API endpoint.
        """

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            # Send POST request
            response = requests.post(
                url=url,
                json=request.dict(),  # Use json parameter to serialize the dictionary
                headers=headers,
                timeout=timeout  # seconds, no timeout by default
            )

            # Raise an exception for bad status codes
            response_json = json.loads(response.text)

            if response.status_code != 200:
                logger.error(response_json.get("error"))
                response.raise_for_status()

            response_content = ProgramExecutionResult.parse_obj(
                response_json.get("data"))
            if not response_content.success:
                logger.error(response_content.standard_error)
                raise Exception(response_content.standard_error)

            # TODO: reformat complex output logs
            logger.debug(response_content.standard_output)

            return response_content.standard_output

        except requests.exceptions.RequestException as e:
            print(f"Error making POST request: {str(e)}")
            raise

        except json.JSONDecodeError as e:
            print(f"Error encoding JSON data: {str(e)}")
            raise

    def execute(
        self,
        request: ProgramExecutionRequest,
        timeout: Optional[int] = None
    ) -> ProgramExecutionResult:

        return self.call(request=request,
                         url=self.definition.execute_url,
                         timeout=timeout)

    def launch(
        self,
        request: ProgramExecutionRequest
    ) -> ProgramExecutionResult:

        return self.call(request=request,
                         url=self.definition.launch_url)

    def kill(
        self,
        request: ProgramExecutionRequest
    ) -> ProgramExecutionResult:

        return self.call(request=request,
                         url=self.definition.kill_url)
