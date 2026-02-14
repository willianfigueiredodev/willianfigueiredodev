"""SVG template: Language Telemetry + Focus Sectors radar (dynamic height)."""

import math

from generator.utils import calculate_language_percentages, esc, svg_arc_path, resolve_arm_colors

WIDTH = 850


def _build_language_bars(lang_data, theme, left_x, start_y):
    """Build the language bar elements (left side of the card)."""
    bar_lines = []
    # Slightly wider bars
    bar_max_width = 220

    for i, lang in enumerate(lang_data):
        y = start_y + i * 28  # More spacing
        bar_w = max(4, (lang["percentage"] / 100) * bar_max_width)
        delay = f"{i * 0.1}s"

        bar_lines.append(f'''    <g transform="translate({left_x}, {y})">
      <text x="0" y="0" fill="{theme['text_dim']}" font-size="12" font-weight="600" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" dominant-baseline="middle">{esc(lang['name'])}</text>
      
      <!-- Background track -->
      <rect x="120" y="-5" width="{bar_max_width}" height="10" rx="5" fill="{theme['star_dust']}" opacity="0.3"/>
      
      <!-- Progress bar -->
      <rect x="120" y="-5" width="{bar_w}" height="10" rx="5" fill="{lang['color']}" opacity="0.9">
        <animate attributeName="width" from="0" to="{bar_w}" dur="1s" begin="{delay}" fill="freeze"/>
      </rect>
      
      <text x="{120 + bar_max_width + 10}" y="0" fill="{theme['text_faint']}" font-size="11" font-family="monospace" dominant-baseline="middle">{lang['percentage']}%</text>
    </g>''')

    return "\n".join(bar_lines)


def _build_radar_grid(rcx, rcy, grid_rings, theme):
    """Build the concentric dashed circles of the radar grid."""
    parts = []
    for ring_r in grid_rings:
        parts.append(
            f'    <circle cx="{rcx}" cy="{rcy}" r="{ring_r}" '
            f'fill="none" stroke="{theme["text_faint"]}" '
            f'stroke-width="1" stroke-dasharray="2,4" opacity="0.15"/>'
        )
    return "\n".join(parts)


def _build_radar_sectors(sector_data, rcx, rcy, radius, theme):
    """Build arc sectors and boundary lines for the radar."""
    parts = []

    # Arc sectors (filled pie slices)
    for sec in sector_data:
        d = svg_arc_path(rcx, rcy, radius, sec["start_deg"], sec["end_deg"])
        parts.append(
            f'    <path d="{d}" fill="{sec["color"]}" fill-opacity="0.08" '
            f'stroke="{sec["color"]}" stroke-opacity="0.2" stroke-width="0.5"/>'
        )

    return "\n".join(parts)


def _build_radar_needle(rcx, rcy, radius, theme):
    """Build the rotating radar needle group."""
    scan_color = theme.get("synapse_cyan", "#2dd4bf")

    needle = (
        f'    <g>'
        f'\n      <!-- Sweep gradient (simulated with arc) -->'
        f'\n      <path d="{svg_arc_path(rcx, rcy, radius, 300, 360)}" fill="{scan_color}" fill-opacity="0.05"/>'
        f'\n      <line x1="{rcx}" y1="{rcy}" x2="{rcx}" y2="{rcy - radius}" '
        f'stroke="{scan_color}" stroke-width="1.5" opacity="0.4"/>'
        f'\n      <animateTransform attributeName="transform" type="rotate" '
        f'from="0 {rcx} {rcy}" to="360 {rcx} {rcy}" '
        f'dur="6s" repeatCount="indefinite"/>'
        f'\n    </g>'
    )
    return needle


def _build_radar_labels_and_dots(sector_data, galaxy_arms, rcx, rcy, radius, theme):
    """Build labels at outer edge and dots per item for each sector."""
    parts = []

    # Labels at outer edge of each sector midpoint
    for sec in sector_data:
        mid_deg = (sec["start_deg"] + sec["end_deg"]) / 2
        mid_rad = math.radians(mid_deg - 90)
        label_r = radius + 24
        lx = rcx + label_r * math.cos(mid_rad)
        ly = rcy + label_r * math.sin(mid_rad)

        # Determine text-anchor based on position
        if abs(lx - rcx) < 5:
            anchor = "middle"
        elif lx > rcx:
            anchor = "start"
        else:
            anchor = "end"

        parts.append(
            f'    <text x="{lx:.1f}" y="{ly:.1f}" fill="{sec["color"]}" '
            f'font-size="10" font-weight="600" font-family="sans-serif" text-anchor="{anchor}" '
            f'dominant-baseline="middle">{esc(sec["name"])}</text>'
        )

    # Dots: one per item per sector
    radii_cycle = [25, 45, 65]
    for sec_i, sec in enumerate(sector_data):
        arm = galaxy_arms[sec_i]
        items = arm.get("items", [])
        item_count = len(items)
        edge_pad = 14
        for j, item in enumerate(items):
            usable_start = sec["start_deg"] + edge_pad
            usable_end = sec["end_deg"] - edge_pad
            
            if item_count <= 1:
                item_angle = (usable_start + usable_end) / 2
            else:
                item_angle = usable_start + (usable_end - usable_start) * j / (item_count - 1)
            
            item_rad = math.radians(item_angle - 90)
            dot_r = radii_cycle[j % 3]
            dx = rcx + dot_r * math.cos(item_rad)
            dy = rcy + dot_r * math.sin(item_rad)
            
            # Simple pulse
            parts.append(
                f'    <circle cx="{dx:.1f}" cy="{dy:.1f}" r="3.5" '
                f'fill="{sec["color"]}" opacity="0.6">'
                f'\n      <animate attributeName="opacity" values="0.4;0.9;0.4" '
                f'dur="3s" begin="{j * 0.5}s" repeatCount="indefinite"/>'
                f'\n    </circle>'
            )

    return "\n".join(parts)


def render(languages, galaxy_arms, theme, exclude, max_display) -> str:
    """Render the tech stack SVG."""
    lang_data = calculate_language_percentages(languages, exclude, max_display)

    # Left side: Language bars
    left_x = 40
    start_y = 80
    bars_str = _build_language_bars(lang_data, theme, left_x, start_y)

    # Right side: Focus Sectors radar
    all_arm_colors = resolve_arm_colors(galaxy_arms, theme)

    # Build sector data
    # Build sector data
    sector_data = []
    num_arms = len(galaxy_arms)
    angle_per_sec = 360 / num_arms if num_arms > 0 else 360

    for i, arm in enumerate(galaxy_arms):
        color = all_arm_colors[i]
        items = arm.get("items", [])
        start_deg = i * angle_per_sec + 2
        end_deg = (i + 1) * angle_per_sec - 2
        
        sector_data.append({
            "name": arm["name"],
            "color": color,
            "items": len(items),
            "start_deg": start_deg,
            "end_deg": end_deg,
        })

    # Radar geometry
    radius = 70
    rcx = 650
    rcy = 120
    grid_rings = [25, 45, 65]

    # Dynamic height
    lang_height = start_y + len(lang_data) * 28 + 30
    radar_height = 240
    height = max(240, lang_height)

    # Build radar SVG elements
    radar_parts = []
    radar_parts.append(_build_radar_grid(rcx, rcy, grid_rings, theme))
    radar_parts.append(_build_radar_sectors(sector_data, rcx, rcy, radius, theme))
    radar_parts.append(_build_radar_needle(rcx, rcy, radius, theme))
    radar_parts.append(_build_radar_labels_and_dots(sector_data, galaxy_arms, rcx, rcy, radius, theme))

    radar_str = "\n".join(radar_parts)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <defs>
    <style>
      .section-title {{ fill: {theme['axon_amber']}; font-size: 11px; font-family: monospace; letter-spacing: 2px; opacity: 0.9; }}
    </style>
  </defs>

  <!-- Card background -->
  <rect x="0" y="0" width="{WIDTH}" height="{height}" rx="16" ry="16"
        fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1"/>

  <!-- Left: Language Telemetry -->
  <text x="40" y="40" class="section-title">TOP LANGUAGES</text>

  <!-- Vertical divider -->
  <line x1="450" y1="30" x2="450" y2="{height - 30}" stroke="{theme['star_dust']}" stroke-width="1" opacity="0.3"/>

  <!-- Right: Focus Sectors -->
  <text x="490" y="40" class="section-title">FOCUS AREAS</text>

  {bars_str}

  {radar_str}
</svg>'''
