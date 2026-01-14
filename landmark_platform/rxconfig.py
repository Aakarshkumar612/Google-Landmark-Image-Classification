import reflex as rx

config = rx.Config(
    app_name="landmark_platform",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)