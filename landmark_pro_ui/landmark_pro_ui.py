import reflex as rx
import os
import sys
import time

# Ensure your local src folder is accessible for engine imports
sys.path.append(os.getcwd())
from src.engine import LandmarkEngine

# --- APP CONFIGURATION ---
MODEL_PATH = './models/landmark_model.h5'
CLASS_NAMES = ["Burj Khalifa", "Eiffel Tower", "Red Fort", "Taj Mahal", "Great Wall of China"]
ai_guide = LandmarkEngine(MODEL_PATH, CLASS_NAMES)

class State(rx.State):
    """The app state managing landmark analysis, language, and theme."""
    # AI Results
    landmark_name: str = "Awaiting Image..."
    history_en: str = "Analysis will appear here."
    history_hi: str = "विश्लेषण यहाँ दिखाई देगा।"
    is_analyzing: bool = False
    image_path: str = ""
    
    # UI Toggles
    show_hindi: bool = False
    is_dark_mode: bool = True

    def toggle_language(self):
        self.show_hindi = not self.show_hindi

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode

    @rx.var
    def current_theme(self) -> dict:
        """Dynamically switch colors based on theme state."""
        if self.is_dark_mode:
            return {
                "bg": "#121212",
                "card_bg": "rgba(30, 41, 59, 0.7)",
                "text": "#E0E0E0",
                "subtext": "#9CA3AF",
                "border": "#1E293B",
                "accent": "#4F46E5"
            }
        else:
            return {
                "bg": "#F3F4F6",
                "card_bg": "rgba(255, 255, 255, 0.9)",
                "text": "#111827",
                "subtext": "#4B5563",
                "border": "#D1D5DB",
                "accent": "#3730A3"
            }

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handles unique file saving to prevent browser caching issues."""
        self.is_analyzing = True
        self.landmark_name = "Analyzing Image..."
        yield 
        
        for file in files:
            try:
                upload_data = await file.read()
                
                # IMPORTANT: We save to 'assets' at the project root
                # os.getcwd() will point to 'Google Landmark Image Classification'
                assets_dir = os.path.join(os.getcwd(), "assets")
                
                if not os.path.exists(assets_dir):
                    os.makedirs(assets_dir)
                
                # UNIQUE FILENAME: Prevents showing the previous scan's image
                file_id = int(time.time())
                unique_name = f"scan_{file_id}.png"
                temp_file_path = os.path.join(assets_dir, unique_name)
                
                with open(temp_file_path, "wb") as f:
                    f.write(upload_data)
                
                # Update the path with the unique name (Reflex serves /assets/ as /)
                self.image_path = f"/{unique_name}"
                
                # AI Engine Execution
                name, conf = ai_guide.predict(upload_data)
                
                if name == "Uncertain":
                    result = ai_guide.predict_with_vision(upload_data)
                    self.landmark_name = result.get('name', 'Unknown')
                    self.history_en = result.get('english', 'No history found.')
                    self.history_hi = result.get('hindi', 'कोई इतिहास नहीं मिला।')
                else:
                    self.landmark_name = name
                    self.history_en = ai_guide.get_expert_response(name)
                    self.history_hi = "विवरण केवल विजन मोड में उपलब्ध है।" 
            
            except Exception as e:
                self.landmark_name = "Error"
                self.history_en = f"Analysis failed: {str(e)}"
        
        self.is_analyzing = False

def index() -> rx.Component:
    return rx.box(
        # Header Section
        rx.hstack(
            rx.heading("🌍 Landmark.AI", size="7", color=State.current_theme["accent"]),
            rx.spacer(),
            rx.hstack(
                # Language Switcher
                rx.text("EN", size="2", color=State.current_theme["text"]),
                rx.switch(is_checked=State.show_hindi, on_change=State.toggle_language),
                rx.text("हिन्दी", size="2", color=State.current_theme["text"]),
                
                rx.divider(orientation="vertical", height="20px", margin_x="10px"),
                
                # Theme Switcher
                rx.icon(tag="sun", size=20, color=State.current_theme["text"]),
                rx.switch(is_checked=State.is_dark_mode, on_change=State.toggle_theme),
                rx.icon(tag="moon", size=20, color=State.current_theme["text"]),
                
                spacing="3",
                align="center",
            ),
            width="100%",
            padding="2em",
        ),
        
        rx.center(
            rx.vstack(
                rx.text(
                    "Identify world landmarks instantly with Hybrid AI.", 
                    size="4", 
                    color=State.current_theme["subtext"]
                ),
                
                # Upload Zone
                rx.upload(
                    rx.vstack(
                        rx.icon(tag="upload", size=40, color=State.current_theme["accent"]),
                        rx.text("Drag & Drop Photo", font_weight="bold", color=State.current_theme["text"]),
                        rx.text("Optimized for high-res images", size="1", color=State.current_theme["subtext"]),
                        spacing="2",
                    ),
                    on_drop=State.handle_upload,
                    border=f"2px dashed {State.current_theme['accent']}",
                    padding="5em",
                    border_radius="xl",
                    background=State.current_theme["card_bg"],
                    backdrop_filter="blur(10px)",
                    _hover={"cursor": "pointer", "opacity": 0.8}
                ),

                # Result Content
                rx.cond(
                    State.is_analyzing,
                    rx.vstack(
                        rx.spinner(size="3", color=State.current_theme["accent"]),
                        rx.text(State.landmark_name, color=State.current_theme["accent"]),
                    ),
                    rx.card(
                        rx.vstack(
                            rx.cond(
                                State.image_path != "",
                                rx.image(
                                    src=State.image_path,
                                    width="100%",
                                    height="auto",
                                    border_radius="md",
                                    margin_bottom="1em",
                                ),
                            ),
                            rx.badge(State.landmark_name, color_scheme="indigo", variant="solid", size="3"),
                            rx.divider(border_color=State.current_theme["border"]),
                            rx.text(
                                rx.cond(State.show_hindi, State.history_hi, State.history_en),
                                size="3", 
                                line_height="1.6",
                                color=State.current_theme["text"]
                            ),
                            align="start",
                            spacing="4",
                        ),
                        width="100%",
                        background=State.current_theme["card_bg"],
                        border=f"1px solid {State.current_theme['border']}",
                        padding="2em",
                        shadow="lg",
                    ),
                ),
                spacing="8",
                width="100%",
                max_width="600px",
            ),
            padding_top="5em",
        ),
        min_height="100vh",
        background=State.current_theme["bg"],
        transition="background 0.4s ease",
    )

app = rx.App()
app.add_page(index)