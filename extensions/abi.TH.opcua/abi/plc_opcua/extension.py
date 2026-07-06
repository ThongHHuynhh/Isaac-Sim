import omni.ext
import omni.ui as ui
from isaacsim.core.api import SimulationContext # For core simulation control

class MyCustomPlugin(omni.ext.IExt):
    # Triggers when the extension is turned on
    def on_startup(self, ext_id):
        self._window = ui.Window("My Custom Plugin Workspace", width=300, height=200)
        
        with self._window.frame:
            with ui.VStack(spacing=10):
                ui.Label("Welcome to your custom Isaac Sim Plugin!")
                
                # Dynamic UI components
                self.action_btn = ui.Button("Spawn Asset", clicked_fn=self._on_button_click)
                self.reset_btn = ui.Button("Reset Stage", clicked_fn=self._on_reset_click)

    def _on_button_click(self):
        # Interact directly with the USD Stage
        print("Spawn Asset Button Clicked!")
        # Insert USD manipulation logic or robot spawning here

    def _on_reset_click(self):
        # Directly control the simulator timeline
        ctx = SimulationContext.instance()
        if ctx:
            ctx.reset()
            print("Simulation stage reset safely.")

    # Triggers when the extension is disabled or closed
    def on_shutdown(self):
        print("Cleaning up plugin resources...")
        if self._window:
            self._window.destroy()
            self._window = None
