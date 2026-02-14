"""SVG template: Featured Systems / Projects Constellation (850x220)."""

from generator.utils import wrap_text, deterministic_random, esc, resolve_arm_colors

WIDTH, HEIGHT = 850, 240


def _build_defs(n, card_width, gap, card_colors, theme):
    """Build all defs (filters, gradients, clip paths, CSS)."""
    defs_parts = []

    # Card background gradients
    for i in range(n):
        color = card_colors[i]
        defs_parts.append(f'''    <linearGradient id="card-bg-{i}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{theme['nebula']}" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="{theme['void']}" stop-opacity="0.95"/>
    </linearGradient>''')

    # CSS keyframes
    defs_parts.append('''    <style>
      @keyframes card-appear {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      .proj-title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-weight: 700; font-size: 14px; }
      .proj-desc { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 11px; }
      .tag-text { font-family: monospace; font-size: 9px; font-weight: 600; }
    </style>''')

    return "\n".join(defs_parts)


def _build_project_card(i, proj, arm, color, card_width, card_x, theme):
    """Build a single project card."""
    card_cx = card_x + card_width / 2
    repo_name = proj["repo"].split("/")[-1] if "/" in proj["repo"] else proj["repo"]
    desc = proj.get("description", "")
    max_chars = int(card_width / 7)
    desc_lines = wrap_text(desc, max_chars)

    delay = f"{i * 0.15}s"

    card_parts = []
    card_parts.append(f'  <g opacity="0" style="animation: card-appear 0.6s ease {delay} forwards">')

    # Card container
    card_parts.append(
        f'    <rect x="{card_x}" y="50" width="{card_width}" height="140" rx="10" ry="10" '
        f'fill="url(#card-bg-{i})" stroke="{theme["star_dust"]}" stroke-width="1"/>'
    )

    # Top accent line
    card_parts.append(
        f'    <line x1="{card_x + 20}" y1="50" x2="{card_x + card_width - 20}" y2="50" '
        f'stroke="{color}" stroke-width="2" opacity="0.8"/>'
    )

    # Repository Icon (Circle + Path)
    icon_y = 85
    card_parts.append(
        f'    <circle cx="{card_cx}" cy="{icon_y}" r="18" fill="{color}" opacity="0.1"/>'
    )
    card_parts.append(
        f'    <circle cx="{card_cx}" cy="{icon_y}" r="18" fill="none" stroke="{color}" stroke-width="1.5" opacity="0.3"/>'
    )
    # Simple folder/repo icon path
    card_parts.append(
        f'    <path d="M{card_cx-7} {icon_y-6} h5 l2 3 h5 a2 2 0 0 1 2 2 v7 a2 2 0 0 1 -2 2 h-12 a2 2 0 0 1 -2 -2 v-10 a2 2 0 0 1 2 -2 z" '
        f'fill="none" stroke="{color}" stroke-width="1.5"/>'
    )

    # Project Name
    card_parts.append(
        f'    <text x="{card_cx}" y="{icon_y + 35}" fill="{theme["text_bright"]}" '
        f'class="proj-title" text-anchor="middle">{esc(repo_name)}</text>'
    )

    # Description
    for j, line in enumerate(desc_lines[:2]):
        y_pos = icon_y + 55 + j * 16
        card_parts.append(
            f'    <text x="{card_cx}" y="{y_pos}" fill="{theme["text_dim"]}" '
            f'class="proj-desc" text-anchor="middle">{esc(line)}</text>'
        )

    # Tag (Arm name)
    tag_text = arm["name"].upper()
    tag_width = len(tag_text) * 6 + 12
    tag_x = card_cx - tag_width / 2
    tag_y = 168
    
    card_parts.append(
        f'    <rect x="{tag_x}" y="{tag_y}" width="{tag_width}" height="16" rx="8" '
        f'fill="{color}" opacity="0.15"/>'
    )
    card_parts.append(
        f'    <text x="{card_cx}" y="{tag_y + 11}" fill="{color}" '
        f'class="tag-text" text-anchor="middle">{esc(tag_text)}</text>'
    )

    card_parts.append('  </g>')
    return "\n".join(card_parts)


def render(projects: list, galaxy_arms: list, theme: dict) -> str:
    """Render the projects constellation SVG."""
    all_arm_colors = resolve_arm_colors(galaxy_arms, theme)

    n = min(len(projects), 3)

    # Default if no projects, but styling matched
    if n == 0:
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" rx="16" ry="16"
        fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1"/>
  <text x="{WIDTH / 2}" y="{HEIGHT / 2}" fill="{theme['text_faint']}" font-size="14"
        font-family="monospace" text-anchor="middle" dominant-baseline="middle">NO ACTIVE SYSTEMS DEPLOYED</text>
</svg>'''

    # Layout sizing
    if n == 1:
        card_width = 320
    elif n == 2:
        card_width = 300
    else:
        card_width = 240
        
    total_cards_width = card_width * n
    gap = (WIDTH - total_cards_width) / (n + 1)

    # Resolve colors
    card_arms = []
    card_colors = []
    for i in range(n):
        proj = projects[i]
        arm_idx = proj.get("arm", 0)
        # Wrap safe index
        arm_idx = arm_idx % len(galaxy_arms) if galaxy_arms else 0
        card_arms.append(arm_idx)
        card_colors.append(all_arm_colors[arm_idx])

    defs_str = _build_defs(n, card_width, gap, card_colors, theme)

    card_parts = []
    for i in range(n):
        proj = projects[i]
        arm = galaxy_arms[card_arms[i]]
        color = card_colors[i]
        card_x = gap + i * (card_width + gap)
        card_parts.append(_build_project_card(i, proj, arm, color, card_width, card_x, theme))

    cards_str = "\n".join(card_parts)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>
    {defs_str}
  </defs>

  <!-- Background -->
  <rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" rx="16" ry="16"
        fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1"/>

  <!-- Header -->
  <text x="32" y="32" fill="{theme['axon_amber']}" font-size="11" 
        font-family="monospace" letter-spacing="2" opacity="0.9">FEATURED DEPLOYMENTS</text>

  <!-- Cards -->
  {cards_str}
</svg>'''
