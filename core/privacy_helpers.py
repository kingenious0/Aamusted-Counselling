def name_to_initials(name_input):
    """
    Standardize student names into initials for GTEC privacy compliance.
    Example: 'Ama Osei' -> 'A.O.'
    Example: 'Ama Osei (12)' -> 'A.O. (12)'
    """
    if not name_input:
        return "N/A"
    
    import re
    # Preserve existing numeric ID suffix if present: e.g. "A. (14)"
    suffix = ""
    match_id = re.search(r'\s*\(\d+\)$', name_input)
    if match_id:
        suffix = match_id.group(0)
        name_input = name_input[:match_id.start()]
    
    # Strip dots and split into parts
    raw = name_input.replace('.', ' ').strip()
    parts = [p.strip() for p in raw.split() if p.strip()]
    
    # Collect initials
    letters = [p[0].upper() for p in parts if p and p[0].isalpha()]
    
    if not letters:
        # Fallback if no letters found (e.g. only numbers/symbols)
        return name_input[:2].upper() + suffix
        
    return ".".join(letters) + "." + suffix
