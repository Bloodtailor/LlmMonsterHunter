

MYSQL_SERVICE_NAMES = [
    # Official MySQL Installer services (newest first)
    "MySQL93", "MySQL92", "MySQL91", "MySQL90",
    "MySQL84", "MySQL83", "MySQL82", "MySQL81", "MySQL80",
    "MySQL79", "MySQL78", "MySQL77", "MySQL76", "MySQL75",
    "MySQL57", "MySQL56", "MySQL55"
]
MYSQL_LOCATIONS = [
    # === PRIMARY DRIVES ===
    # Official MySQL Installer locations
    "C:\\Program Files\\MySQL",
    "C:\\Program Files (x86)\\MySQL",
    
    # Standalone installations
    "C:\\mysql", "C:\\MySQL",
    
    # === WEB DEVELOPMENT STACKS ===
    # XAMPP variations (most common)
    "C:\\xampp\\mysql", "C:\\XAMPP\\mysql",
    "C:\\xampp-php\\mysql", "C:\\xampp-php7\\mysql", "C:\\xampp-php8\\mysql",
    
    # WAMP variations
    "C:\\wamp\\bin\\mysql", "C:\\wamp64\\bin\\mysql",
    "C:\\wamp32\\bin\\mysql", "C:\\WampServer\\bin\\mysql",
    "C:\\wampserver\\bin\\mysql", "C:\\wampserver64\\bin\\mysql",
    
    # Laragon variations
    "C:\\laragon\\bin\\mysql", "C:\\Laragon\\bin\\mysql",
    "C:\\laragon\\mysql", "C:\\Laragon\\mysql",
    
    # MAMP variations
    "C:\\MAMP\\bin\\mysql", "C:\\mamp\\bin\\mysql",
    "C:\\MAMP\\mysql", "C:\\mamp\\mysql",
    
    # AppServ variations
    "C:\\AppServ\\MySQL", "C:\\AppServ\\mysql",
    "C:\\AppServ\\bin\\mysql",
    
    # === ALTERNATIVE DRIVE LETTERS ===
    # D: Drive installations
    "D:\\xampp\\mysql", "D:\\XAMPP\\mysql",
    "D:\\wamp\\bin\\mysql", "D:\\wamp64\\bin\\mysql",
    "D:\\laragon\\bin\\mysql", "D:\\Laragon\\bin\\mysql",
    "D:\\mysql", "D:\\MySQL",
    "D:\\Program Files\\MySQL",
    "D:\\Program Files (x86)\\MySQL",
    "D:\\Server\\MySQL", "D:\\Server\\mysql",
    
    # E: Drive installations
    "E:\\xampp\\mysql", "E:\\XAMPP\\mysql",
    "E:\\wamp\\bin\\mysql", "E:\\wamp64\\bin\\mysql",
    "E:\\mysql", "E:\\MySQL",
    "E:\\Program Files\\MySQL",
    
    # F: Drive installations (less common but still used)
    "F:\\xampp\\mysql", "F:\\mysql", "F:\\MySQL",
    
    # === DOCKER DESKTOP LOCATIONS ===
    "C:\\ProgramData\\DockerDesktop\\mysql",
    "C:\\Users\\{username}\\AppData\\Local\\Docker\\mysql",
    
    # === LEGACY/UNUSUAL LOCATIONS ===
    # Old MySQL installer locations
    "C:\\Program Files\\MySQL AB\\MySQL Server 5.7",
    "C:\\Program Files\\MySQL AB\\MySQL Server 5.6",
    "C:\\Program Files (x86)\\MySQL AB\\MySQL Server 5.7",
]
NODEJS_LOCATIONS = [
    # Visual Studio 2022 (all editions)
    "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community",
    "C:\\Program Files\\Microsoft Visual Studio\\2022\\Professional", 
    "C:\\Program Files\\Microsoft Visual Studio\\2022\\Enterprise",
    "C:\\Program Files\\Microsoft Visual Studio\\2022\\Preview",
    "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools",
    
    # Visual Studio 2019 (all editions)
    "C:\\Program Files\\Microsoft Visual Studio\\2019\\Community",
    "C:\\Program Files\\Microsoft Visual Studio\\2019\\Professional",
    "C:\\Program Files\\Microsoft Visual Studio\\2019\\Enterprise", 
    "C:\\Program Files\\Microsoft Visual Studio\\2019\\Preview",
    "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools",
    
    # Visual Studio 2017 (legacy but still used)
    "C:\\Program Files\\Microsoft Visual Studio\\2017\\Community",
    "C:\\Program Files\\Microsoft Visual Studio\\2017\\Professional",
    "C:\\Program Files\\Microsoft Visual Studio\\2017\\Enterprise",
    "C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\BuildTools",
    
    # Alternative drive installations
    "D:\\Microsoft Visual Studio\\2022\\Community",
    "D:\\Microsoft Visual Studio\\2019\\Community",
    "D:\\Microsoft Visual Studio\\2017\\Community",
    
    # Legacy year-only paths (older detection patterns)
    "C:\\Program Files\\Microsoft Visual Studio\\2022",
    "C:\\Program Files\\Microsoft Visual Studio\\2019",
    "C:\\Program Files\\Microsoft Visual Studio\\2017"
]
SDK_LOCATIONS = [
    # Windows 10/11 SDK (most common)
    "C:\\Program Files (x86)\\Windows Kits\\10",
    "C:\\Program Files\\Windows Kits\\10",
    
    # Windows 8.1 SDK (legacy but still used)
    "C:\\Program Files (x86)\\Windows Kits\\8.1",
    "C:\\Program Files\\Windows Kits\\8.1",
    
    # Windows 8.0 SDK (older legacy)
    "C:\\Program Files (x86)\\Windows Kits\\8.0",
    "C:\\Program Files\\Windows Kits\\8.0",
    
    # Legacy Microsoft SDKs
    "C:\\Program Files (x86)\\Microsoft SDKs\\Windows\\v10.0",
    "C:\\Program Files\\Microsoft SDKs\\Windows\\v10.0",
    "C:\\Program Files (x86)\\Microsoft SDKs\\Windows",
    "C:\\Program Files\\Microsoft SDKs\\Windows",
    
    # Alternative drive installations
    "D:\\Windows Kits\\10",
    "D:\\Windows Kits\\8.1",
    
    # Visual Studio installer locations
    "C:\\Program Files (x86)\\Microsoft Visual Studio\\Shared\\Windows Kits\\10",
    "C:\\Program Files\\Microsoft Visual Studio\\Shared\\Windows Kits\\10",
    
    # Standalone SDK installer locations
    "C:\\Program Files (x86)\\Windows SDKs\\10",
    "C:\\Program Files\\Windows SDKs\\10"
]
VS_LOCATIONS = [
    # Visual Studio 2022 (all editions)
    ("VS Community 2022", "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community"),
    ("VS Professional 2022", "C:\\Program Files\\Microsoft Visual Studio\\2022\\Professional"),
    ("VS Enterprise 2022", "C:\\Program Files\\Microsoft Visual Studio\\2022\\Enterprise"),
    ("VS Preview 2022", "C:\\Program Files\\Microsoft Visual Studio\\2022\\Preview"),
    ("VS Build Tools 2022", "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools"),
    
    # Visual Studio 2019 (all editions)
    ("VS Community 2019", "C:\\Program Files\\Microsoft Visual Studio\\2019\\Community"),
    ("VS Professional 2019", "C:\\Program Files\\Microsoft Visual Studio\\2019\\Professional"),
    ("VS Enterprise 2019", "C:\\Program Files\\Microsoft Visual Studio\\2019\\Enterprise"),
    ("VS Preview 2019", "C:\\Program Files\\Microsoft Visual Studio\\2019\\Preview"),
    ("VS Build Tools 2019", "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools"),
    
    # Visual Studio 2017 (legacy but still used)
    ("VS Community 2017", "C:\\Program Files\\Microsoft Visual Studio\\2017\\Community"),
    ("VS Professional 2017", "C:\\Program Files\\Microsoft Visual Studio\\2017\\Professional"),
    ("VS Enterprise 2017", "C:\\Program Files\\Microsoft Visual Studio\\2017\\Enterprise"),
    ("VS Build Tools 2017", "C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\BuildTools"),
    
    # Alternative drive installations
    ("VS 2022 (D: drive)", "D:\\Microsoft Visual Studio\\2022\\Community"),
    ("VS 2019 (D: drive)", "D:\\Microsoft Visual Studio\\2019\\Community"),
    
    # Legacy paths (older installers)
    ("Visual Studio 2022", "C:\\Program Files\\Microsoft Visual Studio\\2022"),
    ("Visual Studio 2019", "C:\\Program Files\\Microsoft Visual Studio\\2019"),
    ("Visual Studio 2017", "C:\\Program Files\\Microsoft Visual Studio\\2017")
]