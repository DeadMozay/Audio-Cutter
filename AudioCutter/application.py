"""
Your favorite Audio Cutter.
Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Artist : Alfredo Hernández
Website : https://github.com/bil-elmoussaoui/Audio-Cutter
Licence : The script is released under GPL, uses a modified script
     form Chromium project released under BSD license
This file is part of AudioCutter.
AudioCutter is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
AudioCutter is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with AudioCutter. If not, see <http://www.gnu.org/licenses/>.
"""

from gettext import gettext as _
from .widgets import Window, AboutDialog, ShortuctsWindow, SettingsWindow
from .modules import Logger, Settings
from .utils import show_app_menu

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gdk, Gio, Gtk, GLib

class Application(Gtk.Application):
    """Main Application Object."""

    def __init__(self):
        Gtk.Application.__init__(self,
                                 application_id="org.gnome.AudioCutter",
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        GLib.set_application_name(_("Audio Cutter"))
        GLib.set_prgname("Audio Cutter")
        self.app_menu = Gio.Menu()
        self._setup_css()

    def do_startup(self):
        """startup signal handler."""
        Gtk.Application.do_startup(self)
        self._setup_app_menu()

    def do_activate(self):
        """activate signal handler."""
        window = Window.get_default()
        window.set_application(self)
        self.add_window(window)
        window.show_all()

    def _setup_css(self):
        """Setup the CSS."""
        css_file = Gio.File.new_for_uri('resource:///org/gnome/AudioCutter/style.css')
        cssProvider = Gtk.CssProvider()
        screen = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        cssProvider.load_from_file(css_file)
        styleContext.add_provider_for_screen(screen, cssProvider,
                                                Gtk.STYLE_PROVIDER_PRIORITY_USER)
        Logger.debug("Loading css file {}".format(css_file))


    def _setup_app_menu(self):
        """Create the appmenu."""
        # Settings
        settings_content = Gio.Menu.new()
        settings_content.append_item(Gio.MenuItem.new(_("Settings"),
                                     "app.settings"))
        settings_section = Gio.MenuItem.new_section(None, settings_content)
        self.app_menu.append_item(settings_section)

        # Help section
        help_content = Gio.Menu.new()
        help_content.append_item(Gio.MenuItem.new(_("Night Mode"),
                                                  "app.night_mode"))
        if Gtk.get_major_version() >= 3 and Gtk.get_minor_version() >= 20:
            help_content.append_item(Gio.MenuItem.new(_("Shortcuts"),
                                                      "app.shortcuts"))

        help_content.append_item(Gio.MenuItem.new(_("About"), "app.about"))
        help_content.append_item(Gio.MenuItem.new(_("Quit"), "app.quit"))
        help_section = Gio.MenuItem.new_section(None, help_content)
        self.app_menu.append_item(help_section)
        # Settings action
        self.settings_action = Gio.SimpleAction.new("settings", None)
        self.settings_action.connect("activate", self._on_settings)
        self.add_action(self.settings_action)

        # Night Mode action

        is_night_mode = GLib.Variant.new_boolean(Settings.get_default().is_night_mode)

        action = Gio.SimpleAction.new_stateful("night_mode", None,
                                               is_night_mode)
        action.connect("change-state", self._on_night_mode)
        self.add_action(action)

        # Shortcuts action
        if Gtk.get_major_version() >= 3 and Gtk.get_minor_version() >= 20:
            action = Gio.SimpleAction.new("shortcuts", None)
            action.connect("activate", self._on_shortcuts)
            self.add_action(action)

        #About action
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self._on_about)
        self.add_action(action)

        # Quit action
        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self._on_quit)
        self.add_action(action)
        if not show_app_menu():
            self.set_app_menu(self.app_menu)
            Logger.debug("Adding GNOME app menu")

    def _on_night_mode(self, action, *args):
        """Switch the night mode on/off."""
        settings = Settings.get_default()
        is_night_mode = not settings.is_night_mode
        action.set_state(GLib.Variant.new_boolean(is_night_mode))
        settings.is_night_mode = is_night_mode
        Gtk.Settings.get_default().set_property(
            "gtk-application-prefer-dark-theme", is_night_mode)

    def _on_shortcuts(self, *args):
        """Shows keyboard shortcuts."""
        shortcuts = ShortuctsWindow()
        shortcuts.set_transient_for(Window.get_default())
        shortcuts.show()

    def _on_about(self, *args):
        """Shows about dialog."""
        dialog = AboutDialog()
        dialog.set_transient_for(Window.get_default())
        dialog.run()
        dialog.destroy()

    def _on_settings(self, *args):
        """Opens the settings dialog."""
        settings_window = SettingsWindow()
        settings_window.set_transient_for(Window.get_default())
        settings_window.show_window()

    def _on_quit(self, *args):
        """Quit the application."""
        window = Window.get_default()
        window.destroy()
        self.quit()