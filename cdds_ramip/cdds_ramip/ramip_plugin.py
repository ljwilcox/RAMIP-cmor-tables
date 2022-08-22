"""
A Sample module for Adding a new project to CDDS.

This will require MIP tables and CVs and an appropriate request JSON file.

Note that this module must be installed somehow, e.g. through inclusion in
a .pth file in your local python site-packages directory
($HOME/.local/python3.8/site-packages/cdds.pth)
"""
import logging
import os

from typing import Type, Dict, Any

from cdds_common.cdds_plugins.attributes import DefaultGlobalAttributes
from cdds_common.cdds_plugins.base.base_models import BaseModelStore, BaseModelParameters, ModelId
from cdds_common.cdds_plugins.cmip6.cmip6_grid import Cmip6GridLabel
from cdds_common.cdds_plugins.cmip6.cmip6_models import (
    UKESM1_0_LL_Params, HadGEM3_GC31_LL_Params)
import cdds_common.cdds_plugins.cmip6 as cmip6

from cdds_common.cdds_plugins.common import LoadResults
from cdds_common.cdds_plugins.grid import GridLabel
from cdds_common.cdds_plugins.models import ModelParameters
from cdds_common.cdds_plugins.plugins import CddsPlugin
from cdds_common.cdds_plugins.streams import StreamInfo


class RamipPlugin(CddsPlugin):

    def __init__(self):
        super(RamipPlugin, self).__init__('RAMIP')

    def models_parameters(self, model_id: str) -> ModelParameters:
        models_store = RamipModelStore.instance()
        return models_store.get(model_id)

    def overload_models_parameters(self, source_dir: str) -> None:
        models_store = RamipModelStore.instance()
        models_store.overload_params(source_dir)

    def grid_labels(self) -> Type[GridLabel]:
        # Use CMIP6 settings for grid labels
        return Cmip6GridLabel

    def stream_info(self) -> StreamInfo:
        # Not needed
        return None

    def global_attributes(self, request: Dict[str, Any]) -> DefaultGlobalAttributes:
        return DefaultGlobalAttributes(request)


class RamipModelId(ModelId):
    """
    Represents the ID of a Ramip model.
    """

    def get_json_file(self) -> str:
        """
        Returns the json file name for a model containing the model ID as identifier.

        :return: Json file name for the model with current ID
        :rtype: str
        """
        return '{}.json'.format(self.value)

    UKESM1_0_LL = 'UKESM1-0-LL'



class RamipModelStore(BaseModelStore):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        models_to_include = [
            UKESM1_0_LL_Params()
        ]
        super(RamipModelStore, self).__init__(models_to_include)

    @classmethod
    def create_instance(cls) -> 'RamipModelsStore':
        return RamipModelStore()

    def _load_default_params(self) -> None:
        local_dir = os.path.dirname(os.path.abspath(cmip6.__file__))
        # alternative
        #local_dir = os.path.dirname(os.path.abspath(__file__))
        # then the file <local_dir>/data/model/<source_id>.json must exist
        default_dir = os.path.join(local_dir, 'data/model')
        results = self.overload_params(default_dir)
        self._process_load_results(results)

    def _process_load_results(self, results: LoadResults) -> None:
        if results.unloaded:
            template = ('Failed to load model parameters for model "{}" from '
                        'file: "{}"')
            error_messages = [
                template.format(model_id, path)
                for model_id, path in results.unloaded.items()
            ]
            self.logger.critical('\n'.join(error_messages))
            raise RuntimeError('\n'.join(error_messages))
