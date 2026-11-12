"""OpenGL helpers for 2D HUD overlay (GLUT-compatible, no pygame)."""

from __future__ import annotations

from OpenGL.GL import (
    GL_BLEND,
    GL_DEPTH_TEST,
    GL_LINEAR,
    GL_MODELVIEW,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_PROJECTION,
    GL_RGBA,
    GL_SRC_ALPHA,
    GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_TRIANGLE_FAN,
    GL_UNSIGNED_BYTE,
    glBegin,
    glBindTexture,
    glBlendFunc,
    glDisable,
    glEnable,
    glEnd,
    glGenTextures,
    glLoadIdentity,
    glMatrixMode,
    glOrtho,
    glPopMatrix,
    glPushMatrix,
    glTexCoord2f,
    glTexImage2D,
    glTexParameteri,
    glVertex2f,
)


def _render_text_bitmap(lines: list[str]) -> bytes:
    """Render simple monospace-style text to RGBA pixel buffer."""
    char_w, char_h = 8, 16
    padding = 10
    line_h = 20
    width = max(len(line) for line in lines) * char_w + padding * 2
    height = len(lines) * line_h + padding * 2
    pixels = bytearray(width * height * 4)

    def set_pixel(x: int, y: int, r: int, g: int, b: int, a: int = 255) -> None:
        if 0 <= x < width and 0 <= y < height:
            idx = (y * width + x) * 4
            pixels[idx : idx + 4] = bytes((r, g, b, a))

    # Background
    for y in range(height):
        for x in range(width):
            set_pixel(x, y, 0, 0, 0, 150)

    # Simple 5x7 bitmap font for ASCII 32-126
    font: dict[str, list[str]] = {
        " ": ["     ", "     ", "     ", "     ", "     ", "     ", "     "],
        "+": ["  #  ", "  #  ", "#####", "  #  ", "  #  ", "     ", "     "],
        "-": ["     ", "     ", " ### ", "     ", "     ", "     ", "     "],
        ".": ["     ", "     ", "     ", "     ", "     ", "  #  ", "  #  "],
        "/": ["    #", "   # ", "  #  ", " #   ", "#    ", "     ", "     "],
        ":": ["     ", "  #  ", "     ", "     ", "  #  ", "     ", "     "],
        "0": [" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "],
        "1": ["  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
        "2": [" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"],
        "3": [" ### ", "#   #", "    #", " ### ", "    #", "#   #", " ### "],
        "4": ["   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "],
        "5": ["#####", "#    ", "#    ", "#### ", "    #", "#   #", " ### "],
        "6": [" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "],
        "7": ["#####", "    #", "   # ", "  #  ", " #   ", " #   ", " #   "],
        "8": [" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "],
        "9": [" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "],
        "C": [" ### ", "#   #", "#    ", "#    ", "#    ", "#   #", " ### "],
        "D": ["#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "],
        "E": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"],
        "F": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "],
        "H": ["#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
        "L": ["#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"],
        "M": ["#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"],
        "N": ["#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"],
        "O": [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
        "P": ["#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "],
        "R": ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
        "S": [" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "],
        "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
        "U": ["#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
        "W": ["#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"],
        "a": ["     ", "     ", " ### ", "    #", " ####", "#   #", " ####"],
        "c": ["     ", "     ", " ### ", "#    ", "#    ", "#    ", " ### "],
        "d": ["    #", "    #", " ####", "#   #", "#   #", "#   #", " ####"],
        "e": ["     ", "     ", " ### ", "#   #", "#### ", "#    ", " ### "],
        "g": ["     ", "     ", " ####", "#   #", " ####", "    #", " ### "],
        "h": ["#    ", "#    ", "# ## ", "##  #", "#   #", "#   #", "#   #"],
        "i": ["  #  ", "     ", " ##  ", "  #  ", "  #  ", "  #  ", " ### "],
        "l": [" ##  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
        "m": ["     ", "     ", "## # ", "# # #", "# # #", "#   #", "#   #"],
        "n": ["     ", "     ", "# ## ", "##  #", "#   #", "#   #", "#   #"],
        "o": ["     ", "     ", " ### ", "#   #", "#   #", "#   #", " ### "],
        "p": ["     ", "     ", "#### ", "#   #", "#   #", "#### ", "#    "],
        "q": ["     ", "     ", " ####", "#   #", "#   #", " ####", "    #"],
        "r": ["     ", "     ", "# ## ", "##  ", "#    ", "#    ", "#    "],
        "s": ["     ", "     ", " ####", "#    ", " ### ", "    #", "#### "],
        "t": ["  #  ", "  #  ", "#####", "  #  ", "  #  ", "  #  ", "  ## "],
        "u": ["     ", "     ", "#   #", "#   #", "#   #", "#  ##", " ####"],
        "v": ["     ", "     ", "#   #", "#   #", "#   #", " # # ", "  #  "],
        "w": ["     ", "     ", "#   #", "#   #", "# # #", "# # #", " # # "],
        "x": ["     ", "     ", "#   #", " # # ", "  #  ", " # # ", "#   #"],
        "y": ["     ", "     ", "#   #", "#   #", " ####", "    #", " ### "],
        "z": ["     ", "     ", "#####", "   # ", "  #  ", " #   ", "#####"],
        "|": ["  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
        "(": ["   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "],
        ")": [" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "],
        "[": [" ### ", " #   ", " #   ", " #   ", " #   ", " #   ", " ### "],
        "]": [" ### ", "   # ", "   # ", "   # ", "   # ", "   # ", " ### "],
        "←": ["  #  ", " #   ", "#####", "  #  ", "  #  ", "     ", "     "],
        "→": ["  #  ", "   # ", "#####", "  #  ", "  #  ", "     ", "     "],
        "↑": ["  #  ", " ### ", "#####", "  #  ", "  #  ", "     ", "     "],
        "↓": ["  #  ", "  #  ", "#####", " ### ", "  #  ", "     ", "     "],
    }

    def draw_char(cx: int, cy: int, ch: str) -> None:
        glyph = font.get(ch, font[" "])
        for row, pattern in enumerate(glyph):
            for col, cell in enumerate(pattern):
                if cell == "#":
                    for dy in range(char_h // 7):
                        for dx in range(char_w // 5):
                            set_pixel(cx + col * (char_w // 5) + dx, cy + row * (char_h // 7) + dy, 230, 230, 240)

    y = padding
    for line in lines:
        x = padding
        for ch in line:
            draw_char(x, y, ch)
            x += char_w
        y += line_h

    return bytes(pixels), width, height


def draw_text_overlay(width: int, height: int, lines: list[str]) -> None:
    """Render text lines as a transparent 2D overlay without pygame."""
    if not lines:
        return

    texture_data, overlay_w, overlay_h = _render_text_bitmap(lines)

    texture_id = glGenTextures(1)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGBA, overlay_w, overlay_h, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data
    )

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, width, height, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glBegin(GL_TRIANGLE_FAN)
    glTexCoord2f(0.0, 0.0)
    glVertex2f(0.0, 0.0)
    glTexCoord2f(1.0, 0.0)
    glVertex2f(float(overlay_w), 0.0)
    glTexCoord2f(1.0, 1.0)
    glVertex2f(float(overlay_w), float(overlay_h))
    glTexCoord2f(0.0, 1.0)
    glVertex2f(0.0, float(overlay_h))
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glDisable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)
    glDisable(GL_BLEND)
