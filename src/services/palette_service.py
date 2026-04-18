import pandas as pd
from src.utils.helpers import detect_column

def build_palette_html(palette_df, max_items=12):
    if palette_df is None or palette_df.empty:
        return """
        <div class="beauty-tip">
            Không có dữ liệu bảng màu.
        </div>
        """

    color_name_col = detect_column(
        palette_df,
        ["Color Name", "color_name", "name", "color", "colour", "Color"]
    )
    hex_col = detect_column(
        palette_df,
        ["hexadecimal value", "hex", "hex code", "hexadecimal", "Hex"]
    )

    if color_name_col is None or hex_col is None:
        return """
        <div class="beauty-tip">
            File palette chưa có đúng cột tên màu hoặc mã màu hex.
        </div>
        """

    sample_colors = palette_df.head(max_items)

    html = '<div class="palette-grid">'
    for _, row in sample_colors.iterrows():
        color_name = str(row[color_name_col]).replace("_", " ").title()
        hex_color = str(row[hex_col]).strip()

        html += f'<div class="palette-card"><div class="palette-color" style="background:{hex_color};"></div><div class="palette-name">{color_name}</div><div class="palette-hex">{hex_color}</div></div>'
    html += '</div>'
    return html
