import os, re, subprocess, zipfile

# The decky plugin module is located at decky-loader/plugin
# For easy intellisense checkout the decky-loader code one directory up
# or add the `decky-loader/plugin` path to `python.analysis.extraPaths` in `.vscode/settings.json`
import decky_plugin
from settings import SettingsManager


settings = SettingsManager(name="settings", settings_directory=decky_plugin.DECKY_PLUGIN_SETTINGS_DIR)

class Plugin:
    _BW_CLI_PATH = os.path.join(decky_plugin.DECKY_PLUGIN_DIR, "bin", "bw")

    login_process = None
    session_id = None


    def _extract_session_id(self, lines):
        for line in lines:
            x = re.search(r'export BW_SESSION=\"([^\"]+)\"', line)
            if x is not None:
                return x.group(1)



    async def login(self, email: str, password: str):
        if self.login_process is not None:
            self.login_process.kill()
        self.login_process = subprocess.Popen([self._BW_CLI_PATH, "login", email, password], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        err = self.login_process.stderr.readline().strip()
        if err is not '':
            return err

        lines = self.login_process.stdout.readlines()
        for line in lines:
            if 'You are logged in!' in line:
                self.session_id = self._extract_session_id(lines)
                self.login_process.wait()
                self.login_process = None
                return 'logged_in'
            
            if 'Two-step login code:' in line:
                return 'two_step_request'
            
        decky_plugin.logger.error("Something went wrong logging in.")
        decky_plugin.logger.error(lines)
        self.login_process.kill()
        self.login_process = None
        
        return 'unknown'
    
    async def two_step(self, code: str):
        if self.login_process is not None:
            out, err = self.login_process.communicate(code.encode())
            if err is not '':
                return err
            
            if 'You are logged in!' in out:
                self.session_id = self._extract_session_id([out])
                self.login_process.wait()
                self.login_process = None
                return 'logged_in'
            
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
        if os.path.isfile(bw_zip_path) and current_version != '2024.3.1':
            decky_plugin.logger.info("Updating BitWarden CLI Binary")
            with zipfile.ZipFile(bw_zip_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.join(decky_plugin.DECKY_PLUGIN_DIR, "bin"))
            os.remove(bw_zip_path)
            settings.setSetting('bw_cli_version', '2024.3.1')
            settings.commit()
        if not os.path.exists(self._BW_CLI_PATH):
            decky_plugin.logger.warn("BitWarden CLI not found")
