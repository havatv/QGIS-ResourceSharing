# coding=utf-8
import os
# Use pathlib instead of os.path?
# from pathlib import Path
import fnmatch
import shutil
from processing.tools.system import userFolder, mkdir

# Worth a try? Should probably be present if the Processing R
# Provider plugin is installed.
# from processing_r.processing.utils import RUtils

from resource_sharing.resource_handler.base import BaseResourceHandler

from qgis.core import QgsApplication, QgsMessageLog, Qgis

R_SCRIPTS_FOLDER = 'R_SCRIPTS_FOLDER'
RSCRIPTS = 'rscripts'


class RScriptHandler(BaseResourceHandler):
    """Handler for R script resources."""
    IS_DISABLED = False

    def __init__(self, collection_id):
        """Constructor of the base class."""
        BaseResourceHandler.__init__(self, collection_id)

    @classmethod
    def dir_name(cls):
        return 'rscripts'

    def install(self):
        """Install the R scripts of the collection.

        We copy the R scripts (*.rsx and *.rsx.help) that exist in
        the rscripts dir to the user's R script directory and refresh
        the provider.
        """
        # Check if the dir exists, return silently if it doesn't
        # if Path(self.resource_dir).exists():
        if not os.path.exists(self.resource_dir):
            return

        # Get all the R script files under self.resource_dir
        R_files = []
        for item in os.listdir(self.resource_dir):
            # file_path = self.resource_dir / item)
            file_path = os.path.join(self.resource_dir, item)
            if fnmatch.fnmatch(file_path, '*.rsx'):
                R_files.append(file_path)
            if fnmatch.fnmatch(file_path, '*.rsx.help'):
                R_files.append(file_path)

        valid = 0
        for R_file in R_files:
            # Install the R script file silently
            try:
                shutil.copy(R_file, self.RScripts_folder())
                valid += 1
            except OSError as e:
                QgsMessageLog.logMessage("Could not copy script '" +
                                         str(R_file) + "'\n" + str(e),
                                         "QGIS Resource Sharing",
                                         Qgis.Warning)
        if valid > 0:
            self.refresh_Rscript_provider()

    def uninstall(self):
        """Uninstall the r scripts from processing toolbox."""
        # if not Path(self.resource_dir).exists():
        if not os.path.exists(self.resource_dir):
            return
        # Remove the R script files that are present in this collection
        for item in os.listdir(self.resource_dir):
            # file_path = self.resource_dir / item)
            file_path = os.path.join(self.resource_dir, item)
            if fnmatch.fnmatch(file_path, '*%s*' % self.collection_id):
                script_path = os.path.join(self.RScripts_folder(), item)
                if os.path.exists(script_path):
                    os.remove(script_path)

        self.refresh_Rscript_provider()

    def refresh_Rscript_provider(self):
        """Refresh the R script provider."""
        r_provider = QgsApplication.processingRegistry().providerById("r")
        if r_provider is not None:
            r_provider.refreshAlgorithms()

    def default_rscripts_folder(self):
        """Return the default R scripts folder."""
        # folder = userFolder() / RSCRIPTS
        folder = str(os.path.join(userFolder(), RSCRIPTS))
        mkdir(folder)
        # return folder.absolute()
        return os.path.abspath(folder)

    def RScripts_folder(self):
        """Return the default R scripts folder."""
        # Perphaps better to use RUtils.default_scripts_folder()?
        # return RUtils.default_scripts_folder()
        # Local:
        return self.default_rscripts_folder()
