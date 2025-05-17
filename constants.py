VALID_ACCURACIES = {'95', '98', '100'}
VALID_MODS = {
    'NM': {'NM', 'nm'},
    'HD': {'HD', 'hd'},
    'HR': {'HR', 'hr'},
    'DT': {'DT', 'dt'},
    'HDHR': {
        'HDHR', 'HRHD', 'hdhr', 'hrhd',
        'HD+HR', 'HR+HD', 'hd+hr', 'hr+hd',
        'HDHR', 'HRHD',
    },
    'HDDT': {
        'HDDT', 'DTHD', 'HD+DT', 'DT+HD',
        'hddt', 'dthd', 'hd+dt', 'dt+hd',
        'DTHD',
        'DT+HD', 'HD+DT',
    },
    'HRDT': {
        'HRDT', 'DTHR', 'HR+DT', 'DT+HR',
        'hrdt', 'dthr', 'hr+dt', 'dt+hr',
        'DTHR', 'THDR',
        'DT+HR', 'HR+DT',
    },
    'HDHRDT': {
        'HDHRDT', 'DTHDHR', 'HDHR+DT', 'DT+HDHR', 'HD+HR+DT',
        'hdhrdt', 'dthdhr', 'hdhr+dt', 'dt+hdhr', 'hd+hr+dt',
        'HDHRDT', 'HRDT+HD', 'DT+HDHR', 'HR+HD+DT', 'DT+HR+HD',
        'HD+DT+HR', 'DT+HD+HR', 'HR+DT+HD',
        'HD+HR+DT', 'HR+HD+DT', 'DT+HD+HR', 'DT+HR+HD', 'HR+DT+HD', 'HD+DT+HR'
    }
}

MOD_COMPONENTS = {'NM', 'HD', 'HR', 'DT'}

def normalize_mod_token(token: str) -> str | None:
    """
    Given an input like 'dthd' or 'dt+hd', returns the canonical mod like 'HDDT'.
    """
    cleaned = token.upper().replace('+', '').strip()
    for canonical, variations in VALID_MODS.items():
        if cleaned in variations:
            return canonical
    return None
