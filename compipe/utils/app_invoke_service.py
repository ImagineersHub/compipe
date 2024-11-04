# launch windows program from docker container
import requests
import json
from typing import List
from pydantic import BaseModel, Field, Optional
from utils.parameters import ARG_APP_INVOKE
from compipe.runtime_env import Environment as env
from utils.singleton import Singleton


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

    TimeoutSeconds: Optional[int] = Field(
        default=None,
        description="Maximum execution time in seconds before termination"
    )

    Hidden: bool = Field(
        default=False,
        description="Whether to hide the program window in launching mode"
    )


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
    ):
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
                data=request.json(),
                headers=headers,
                timeout=30  # Timeout after 30 seconds
            )

            # Raise an exception for bad status codes
            response.raise_for_status()

            # Return response if successful
            return response

        except requests.exceptions.RequestException as e:
            print(f"Error making POST request: {str(e)}")
            raise

        except json.JSONDecodeError as e:
            print(f"Error encoding JSON data: {str(e)}")
            raise

    def execute(self,
                request: ProgramExecutionRequest):

        self.call(request=request,
                  url=self.definition.execute_url)

    def launch(self,
               request: ProgramExecutionRequest):

        self.call(request=request,
                  url=self.definition.launch_url)

    def kill(self,
             request: ProgramExecutionRequest):

        self.call(request=request,
                  url=self.definition.kill_url)
