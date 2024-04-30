from typing import List
import os, re, subprocess, zipfile, json

# The decky plugin module is located at decky-loader/plugin
# For easy intellisense checkout the decky-loader code one directory up
# or add the `decky-loader/plugin` path to `python.analysis.extraPaths` in `.vscode/settings.json`
import decky_plugin
from settings import SettingsManager


settings = SettingsManager(name="settings", settings_directory=decky_plugin.DECKY_PLUGIN_SETTINGS_DIR)

class Plugin:
    _BW_CLI_PATH = os.path.join(decky_plugin.DECKY_PLUGIN_DIR, "bin", "bw")

    session_id = None

    @classmethod
    def _extract_session_id(self, lines):
        for line in lines:
            x = re.search(r'export BW_SESSION=\"([^\"]+)\"', line)
            if x is not None:
                return x.group(1)
            
    @classmethod
    def _check_output(self, command: List[str]):
        cmd = [self._BW_CLI_PATH] + command
        if(self.session_id is not None):
            cmd.append("--session=%s" % self.session_id)
        decky_plugin.logger.info("Calling bw: %s [%d]", command[0], len(command))
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            
    @classmethod
    def _check_output_json(self, command: List[str]):
        return json.loads(self._check_output(command))

    async def status(self):
        return self._check_output_json(["status"])

    async def login(self, email: str, password: str, authCode: str=None):
        cmd = ["login", email, password]
        if authCode:
            cmd.append("--method")
            cmd.append("0")
            cmd.append("--code")
            cmd.append(authCode)
        
        result = self._check_output(cmd)
        if 'You are logged in!' in result:
            self.session_id = self._extract_session_id(result)
            return 'logged_in'
        decky_plugin.logger.error("Something went wrong logging in.")
        
        if result:
            decky_plugin.logger.error(result)
            return result
        
        return 'unknown'

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        decky_plugin.logger.info("Hello World!")

    # Function called first during the unload process, utilize this to handle your plugin being removed
    async def _unload(self):
        decky_plugin.logger.info("Goodbye World!")
        pass

    # Migrations that should be performed before entering `_main()`.
    async def _migration(self):
        decky_plugin.logger.info("Migrating")
        settings.read()

        current_version = settings.getSetting('bw_cli_version')

        bw_zip_path = os.path.join(decky_plugin.DECKY_PLUGIN_DIR, "bin", "bw-linux-2024.3.1.zip")
        if (os.path.isfile(bw_zip_path) and current_version != '2024.3.1') or (not os.path.exists(self._BW_CLI_PATH) and os.path.isfile(bw_zip_path)):
            decky_plugin.logger.info("Updating BitWarden CLI Binary")
            with zipfile.ZipFile(bw_zip_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.join(decky_plugin.DECKY_PLUGIN_DIR, "bin"))
            os.remove(bw_zip_path)
            settings.setSetting('bw_cli_version', '2024.3.1')
            settings.commit()
        if not os.path.exists(self._BW_CLI_PATH):
            decky_plugin.logger.warn("BitWarden CLI not found")
        elif not os.access(self._BW_CLI_PATH, os.X_OK):
            os.chmod(self._BW_CLI_PATH, 0o0774)
