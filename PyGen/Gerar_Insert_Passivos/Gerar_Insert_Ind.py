import os

# =============================================================================
# CONSTANTES GLOBAIS
# =============================================================================
MANUFACTURER = "Fastron"
CATEGORY = "Inductor"
SUBCATEGORY = "Wirewound"
MOUNT = "SMD"
UNIT = "H"
TEMP_RANGE = "-40°C ~ 125°C"
REACH = "Yes"
ROHS = "Yes"
CREATED_BY = "Rogerio Fontanario"
DATASHEET_BASE_URL = "https://www.fastrongroup.com/product-downloads/"

METRIC_CODES = {
    "0402": "1005",
    "0603": "1608",
    "0805": "2012",
    "1206": "3216",
    "1210": "3225",
    "1812": "4532",
    "2010": "5025",
    "2512": "6332"
}

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================
def format_current(ma_value):
    """Converte corrente de mA para string no formato adequado (mA ou A)."""
    if ma_value is None:
        return ""
    if ma_value >= 1000:
        a = ma_value / 1000.0
        if a.is_integer():
            return f"{int(a)}A"
        else:
            return f"{a:.1f}A".replace('.0', '')
    else:
        return f"{ma_value}mA"

def format_inductance_value(nh_value):
    """
    Converte valor em nH para string legível com prefixo no lugar do ponto.
    Ex: 2.7 nH → "2n7", 10 nH → "10n", 1.2 µH (1200 nH) → "1u2".
    """
    if nh_value >= 1000:
        # µH
        val_uh = nh_value / 1000.0
        s = f"{val_uh:.1f}"
        if s.endswith('.0'):
            return s[:-2] + 'u'
        else:
            return s.replace('.', 'u')
    else:
        # nH
        s = f"{nh_value:.1f}"
        if s.endswith('.0'):
            return s[:-2] + 'n'
        else:
            return s.replace('.', 'n')

def generate_part_number(model):
    return model

# =============================================================================
# DADOS EXTRAÍDOS DAS TABELAS (por encapsulamento)
# =============================================================================

INDUCTOR_SPECS = {
    "0402": [
        {"model": "0402AS-0N9K-YY", "inductance_nh": 0.9, "tolerance": "10%", "current_ma": 1360, "dcr_ohms": 0.04, "q_min": 11, "test_freq_mhz": 250, "srf_mhz": "6000 min"},
        {"model": "0402AS-1N0K-YY", "inductance_nh": 1.0, "tolerance": "10%", "current_ma": 700, "dcr_ohms": 0.07, "q_min": 11, "test_freq_mhz": 250, "srf_mhz": "6000 min"},
        {"model": "0402AS-1N2K-YY", "inductance_nh": 1.2, "tolerance": "10%", "current_ma": 700, "dcr_ohms": 0.11, "q_min": 11, "test_freq_mhz": 250, "srf_mhz": "6000 min"},
        {"model": "0402AS-1N8K-YY", "inductance_nh": 1.8, "tolerance": "10%", "current_ma": 1040, "dcr_ohms": 0.17, "q_min": 16, "test_freq_mhz": 250, "srf_mhz": "6000 min"},
        {"model": "0402AS-1N9K-YY", "inductance_nh": 1.9, "tolerance": "10%", "current_ma": 1040, "dcr_ohms": 0.17, "q_min": 16, "test_freq_mhz": 250, "srf_mhz": "6000 min"},
        {"model": "0402AS-2N0K-YY", "inductance_nh": 2.0, "tolerance": "10%", "current_ma": 1040, "dcr_ohms": 0.17, "q_min": 16, "test_freq_mhz": 250, "srf_mhz": "6000 min"},
        {"model": "0402AS-2N2K-YY", "inductance_nh": 2.2, "tolerance": "10%", "current_ma": 640, "dcr_ohms": 0.11, "q_min": 14, "test_freq_mhz": 250, "srf_mhz": "6000 min"},
        {"model": "0402AS-2N4K-YY", "inductance_nh": 2.4, "tolerance": "10%", "current_ma": 640, "dcr_ohms": 0.12, "q_min": 16, "test_freq_mhz": 250, "srf_mhz": "6000 min"},
        {"model": "0402AS-2N5K-YY", "inductance_nh": 2.5, "tolerance": "10%", "current_ma": 640, "dcr_ohms": 0.12, "q_min": 16, "test_freq_mhz": 250, "srf_mhz": "6000 min"},
        {"model": "0402AS-2N7K-YY", "inductance_nh": 2.7, "tolerance": "10%", "current_ma": 640, "dcr_ohms": 0.12, "q_min": 16, "test_freq_mhz": 250, "srf_mhz": "6000 min"},
        {"model": "0402AS-2N9K-YY", "inductance_nh": 2.9, "tolerance": "10%", "current_ma": 700, "dcr_ohms": 0.10, "q_min": 16, "test_freq_mhz": 250, "srf_mhz": "6000 min"},
        {"model": "0402AS-3N3K-YY", "inductance_nh": 3.3, "tolerance": "10%", "current_ma": 700, "dcr_ohms": 0.10, "q_min": 20, "test_freq_mhz": 250, "srf_mhz": "6000 min"},
        {"model": "0402AS-3N6K-YY", "inductance_nh": 3.6, "tolerance": "10%", "current_ma": 700, "dcr_ohms": 0.10, "q_min": 19, "test_freq_mhz": 250, "srf_mhz": "6000 min"},
        {"model": "0402AS-3N9K-YY", "inductance_nh": 3.9, "tolerance": "10%", "current_ma": 760, "dcr_ohms": 0.110, "q_min": 19, "test_freq_mhz": 250, "srf_mhz": "4800 min"},
        {"model": "0402AS-4N3K-YY", "inductance_nh": 4.3, "tolerance": "10%", "current_ma": 760, "dcr_ohms": 0.110, "q_min": 21, "test_freq_mhz": 250, "srf_mhz": "4800 min"},
        {"model": "0402AS-4N7K-YY", "inductance_nh": 4.7, "tolerance": "10%", "current_ma": 640, "dcr_ohms": 0.130, "q_min": 15, "test_freq_mhz": 250, "srf_mhz": "4775 min"},
        {"model": "0402AS-5N1J-YY", "inductance_nh": 5.1, "tolerance": "5%", "current_ma": 800, "dcr_ohms": 0.083, "q_min": 23, "test_freq_mhz": 250, "srf_mhz": "4800 min"},
        {"model": "0402AS-5N6J-YY", "inductance_nh": 5.6, "tolerance": "5%", "current_ma": 760, "dcr_ohms": 0.110, "q_min": 22, "test_freq_mhz": 250, "srf_mhz": "4800 min"},
        {"model": "0402AS-6N2J-YY", "inductance_nh": 6.2, "tolerance": "5%", "current_ma": 760, "dcr_ohms": 0.110, "q_min": 20, "test_freq_mhz": 250, "srf_mhz": "4800 min"},
        {"model": "0402AS-6N8J-YY", "inductance_nh": 6.8, "tolerance": "5%", "current_ma": 680, "dcr_ohms": 0.100, "q_min": 21, "test_freq_mhz": 250, "srf_mhz": "4800 min"},
        {"model": "0402AS-7N5J-YY", "inductance_nh": 7.5, "tolerance": "5%", "current_ma": 680, "dcr_ohms": 0.100, "q_min": 24, "test_freq_mhz": 250, "srf_mhz": "4800 min"},
        {"model": "0402AS-8N2J-YY", "inductance_nh": 8.2, "tolerance": "5%", "current_ma": 680, "dcr_ohms": 0.100, "q_min": 24, "test_freq_mhz": 250, "srf_mhz": "4400 min"},
        {"model": "0402AS-8N7J-YY", "inductance_nh": 8.7, "tolerance": "5%", "current_ma": 681, "dcr_ohms": 0.160, "q_min": 22, "test_freq_mhz": 250, "srf_mhz": "4160 min"},
        {"model": "0402AS-9N0J-YY", "inductance_nh": 9.0, "tolerance": "5%", "current_ma": 681, "dcr_ohms": 0.160, "q_min": 22, "test_freq_mhz": 250, "srf_mhz": "4160 min"},
        {"model": "0402AS-9N1J-YY", "inductance_nh": 9.1, "tolerance": "5%", "current_ma": 480, "dcr_ohms": 0.200, "q_min": 22, "test_freq_mhz": 250, "srf_mhz": "4000 min"},
        {"model": "0402AS-9N5J-YY", "inductance_nh": 9.5, "tolerance": "5%", "current_ma": 480, "dcr_ohms": 0.200, "q_min": 22, "test_freq_mhz": 250, "srf_mhz": "4000 min"},
        {"model": "0402AS-010J-YY", "inductance_nh": 10, "tolerance": "5%", "current_ma": 480, "dcr_ohms": 0.200, "q_min": 21, "test_freq_mhz": 250, "srf_mhz": "3900 min"},
        {"model": "0402AS-011J-YY", "inductance_nh": 11, "tolerance": "5%", "current_ma": 640, "dcr_ohms": 0.170, "q_min": 24, "test_freq_mhz": 250, "srf_mhz": "3680 min"},
        {"model": "0402AS-012J-YY", "inductance_nh": 12, "tolerance": "5%", "current_ma": 640, "dcr_ohms": 0.170, "q_min": 24, "test_freq_mhz": 250, "srf_mhz": "3600 min"},
        {"model": "0402AS-013J-YY", "inductance_nh": 13, "tolerance": "5%", "current_ma": 640, "dcr_ohms": 0.170, "q_min": 24, "test_freq_mhz": 250, "srf_mhz": "3600 min"},
        {"model": "0402AS-015J-YY", "inductance_nh": 15, "tolerance": "5%", "current_ma": 560, "dcr_ohms": 0.170, "q_min": 24, "test_freq_mhz": 250, "srf_mhz": "3280 min"},
        {"model": "0402AS-016J-YY", "inductance_nh": 16, "tolerance": "5%", "current_ma": 560, "dcr_ohms": 0.220, "q_min": 24, "test_freq_mhz": 250, "srf_mhz": "3100 min"},
        {"model": "0402AS-018J-YY", "inductance_nh": 18, "tolerance": "5%", "current_ma": 420, "dcr_ohms": 0.23, "q_min": 25, "test_freq_mhz": 250, "srf_mhz": "3100 min"},
        {"model": "0402AS-019J-YY", "inductance_nh": 19, "tolerance": "5%", "current_ma": 480, "dcr_ohms": 0.24, "q_min": 24, "test_freq_mhz": 250, "srf_mhz": "3040 min"},
        {"model": "0402AS-020J-YY", "inductance_nh": 20, "tolerance": "5%", "current_ma": 420, "dcr_ohms": 0.25, "q_min": 25, "test_freq_mhz": 250, "srf_mhz": "3000 min"},
        {"model": "0402AS-022J-YY", "inductance_nh": 22, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.30, "q_min": 25, "test_freq_mhz": 250, "srf_mhz": "2800 min"},
        {"model": "0402AS-023J-YY", "inductance_nh": 23, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.30, "q_min": 22, "test_freq_mhz": 250, "srf_mhz": "2720 min"},
        {"model": "0402AS-024J-YY", "inductance_nh": 24, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.30, "q_min": 22, "test_freq_mhz": 250, "srf_mhz": "2480 min"},
        {"model": "0402AS-027J-YY", "inductance_nh": 27, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.30, "q_min": 24, "test_freq_mhz": 250, "srf_mhz": "2480 min"},
        {"model": "0402AS-030J-YY", "inductance_nh": 30, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.30, "q_min": 24, "test_freq_mhz": 250, "srf_mhz": "2350 min"},
        {"model": "0402AS-033J-YY", "inductance_nh": 33, "tolerance": "5%", "current_ma": 320, "dcr_ohms": 0.30, "q_min": 24, "test_freq_mhz": 250, "srf_mhz": "2350 min"},
        {"model": "0402AS-036J-YY", "inductance_nh": 36, "tolerance": "5%", "current_ma": 320, "dcr_ohms": 0.44, "q_min": 24, "test_freq_mhz": 250, "srf_mhz": "2320 min"},
        {"model": "0402AS-039J-YY", "inductance_nh": 39, "tolerance": "5%", "current_ma": 200, "dcr_ohms": 0.55, "q_min": 25, "test_freq_mhz": 250, "srf_mhz": "2100 min"},
        {"model": "0402AS-040J-YY", "inductance_nh": 40, "tolerance": "5%", "current_ma": 150, "dcr_ohms": 0.83, "q_min": 25, "test_freq_mhz": 250, "srf_mhz": "2100 min"},
        {"model": "0402AS-043J-YY", "inductance_nh": 43, "tolerance": "5%", "current_ma": 150, "dcr_ohms": 0.70, "q_min": 25, "test_freq_mhz": 250, "srf_mhz": "2100 min"},
        {"model": "0402AS-047J-YY", "inductance_nh": 47, "tolerance": "5%", "current_ma": 150, "dcr_ohms": 0.83, "q_min": 25, "test_freq_mhz": 250, "srf_mhz": "2100 min"},
        {"model": "0402AS-051J-YY", "inductance_nh": 51, "tolerance": "5%", "current_ma": 100, "dcr_ohms": 0.97, "q_min": 25, "test_freq_mhz": 250, "srf_mhz": "1760 min"},
        {"model": "0402AS-056J-YY", "inductance_nh": 56, "tolerance": "5%", "current_ma": 100, "dcr_ohms": 0.97, "q_min": 25, "test_freq_mhz": 250, "srf_mhz": "1760 min"},
        {"model": "0402AS-068J-YY", "inductance_nh": 68, "tolerance": "5%", "current_ma": 100, "dcr_ohms": 0.97, "q_min": 25, "test_freq_mhz": 250, "srf_mhz": "1620 min"},
        {"model": "0402AS-072J-YY", "inductance_nh": 72, "tolerance": "5%", "current_ma": 80, "dcr_ohms": 1.20, "q_min": 15, "test_freq_mhz": 100, "srf_mhz": "1070 min"},
        {"model": "0402AS-R10K-YY", "inductance_nh": 100, "tolerance": "10%", "current_ma": 80, "dcr_ohms": 1.20, "q_min": 15, "test_freq_mhz": 100, "srf_mhz": "1070 min"},
        {"model": "0402AS-R12K-YY", "inductance_nh": 120, "tolerance": "10%", "current_ma": 75, "dcr_ohms": 1.30, "q_min": 12, "test_freq_mhz": 100, "srf_mhz": "580 min"},
        {"model": "0402AS-R15K-YY", "inductance_nh": 150, "tolerance": "10%", "current_ma": 70, "dcr_ohms": 1.30, "q_min": 10, "test_freq_mhz": 100, "srf_mhz": "450 typ"},
        {"model": "0402AS-R18K-YY", "inductance_nh": 180, "tolerance": "10%", "current_ma": 60, "dcr_ohms": 1.30, "q_min": 10, "test_freq_mhz": 100, "srf_mhz": "400 typ"},
        {"model": "0402AS-R20K-YY", "inductance_nh": 200, "tolerance": "10%", "current_ma": 65, "dcr_ohms": 1.50, "q_min": 10, "test_freq_mhz": 50, "srf_mhz": "380 typ"},
        {"model": "0402AS-R22K-YY", "inductance_nh": 220, "tolerance": "10%", "current_ma": 50, "dcr_ohms": 2.00, "q_min": 10, "test_freq_mhz": 50, "srf_mhz": "190 typ"},
    ],
    "0603": [
        {"model": "0603AS-1N2M-YY", "inductance_nh": 1.2, "tolerance": "20%", "current_ma": 850, "dcr_ohms": 0.030, "q_min": 30, "test_freq_mhz": 250, "srf_mhz": ">6000 min"},
        {"model": "0603AS-1N3M-YY", "inductance_nh": 1.3, "tolerance": "20%", "current_ma": 850, "dcr_ohms": 0.030, "q_min": 30, "test_freq_mhz": 250, "srf_mhz": ">6000 min"},
        {"model": "0603AS-1NSK-YY", "inductance_nh": 1.5, "tolerance": "10%", "current_ma": 850, "dcr_ohms": 0.030, "q_min": 20, "test_freq_mhz": 250, "srf_mhz": ">6000 min"},
        {"model": "0603AS-1NK-KY", "inductance_nh": 1.6, "tolerance": "10%", "current_ma": 850, "dcr_ohms": 0.030, "q_min": 20, "test_freq_mhz": 250, "srf_mhz": ">6000 min"},
        {"model": "0603AS-1NBK-YY", "inductance_nh": 1.8, "tolerance": "10%", "current_ma": 700, "dcr_ohms": 0.045, "q_min": 20, "test_freq_mhz": 250, "srf_mhz": ">6000 min"},
        {"model": "0603AS-2N0K-YY", "inductance_nh": 2.0, "tolerance": "10%", "current_ma": 170, "dcr_ohms": 0.17, "q_min": 20, "test_freq_mhz": 250, "srf_mhz": "5900 min"},
        {"model": "0603AS-2N2M-YY", "inductance_nh": 2.2, "tolerance": "20%", "current_ma": 170, "dcr_ohms": 0.17, "q_min": 20, "test_freq_mhz": 250, "srf_mhz": "5900 min"},
        {"model": "#0603AS-3N3K-YY", "inductance_nh": 3.3, "tolerance": "10%", "current_ma": 700, "dcr_ohms": 0.10, "q_min": 22, "test_freq_mhz": 250, "srf_mhz": "6000 min"},
        {"model": "0603AS-3N6K-YY", "inductance_nh": 3.6, "tolerance": "10%", "current_ma": 700, "dcr_ohms": 0.08, "q_min": 22, "test_freq_mhz": 250, "srf_mhz": ">6000 min"},
        {"model": "0603AS-3N9K-YY", "inductance_nh": 3.9, "tolerance": "10%", "current_ma": 700, "dcr_ohms": 0.08, "q_min": 22, "test_freq_mhz": 250, "srf_mhz": ">6000 min"},
        {"model": "0603AS-4N3K-YY", "inductance_nh": 4.3, "tolerance": "10%", "current_ma": 700, "dcr_ohms": 0.07, "q_min": 25, "test_freq_mhz": 250, "srf_mhz": ">6000 min"},
        {"model": "0603AS-4N7K-YY", "inductance_nh": 4.7, "tolerance": "10%", "current_ma": 700, "dcr_ohms": 0.07, "q_min": 25, "test_freq_mhz": 250, "srf_mhz": ">6000 min"},
        {"model": "0603AS-5N1K-YY", "inductance_nh": 5.1, "tolerance": "10%", "current_ma": 700, "dcr_ohms": 0.12, "q_min": 27, "test_freq_mhz": 250, "srf_mhz": "6000 min"},
        {"model": "#0603AS-5N6K-YY", "inductance_nh": 5.6, "tolerance": "10%", "current_ma": 700, "dcr_ohms": 0.12, "q_min": 27, "test_freq_mhz": 250, "srf_mhz": "6000 min"},
        {"model": "0603AS-6N2J-YY", "inductance_nh": 6.2, "tolerance": "5%", "current_ma": 700, "dcr_ohms": 0.11, "q_min": 25, "test_freq_mhz": 250, "srf_mhz": "5800 min"},
        {"model": "0603AS-6N8J-YY", "inductance_nh": 6.8, "tolerance": "5%", "current_ma": 700, "dcr_ohms": 0.11, "q_min": 25, "test_freq_mhz": 250, "srf_mhz": "5800 min"},
        {"model": "0603AS-7N5J-YY", "inductance_nh": 7.5, "tolerance": "5%", "current_ma": 700, "dcr_ohms": 0.12, "q_min": 30, "test_freq_mhz": 250, "srf_mhz": "5400 min"},
        {"model": "0603AS-7N6J-YY", "inductance_nh": 7.6, "tolerance": "5%", "current_ma": 700, "dcr_ohms": 0.12, "q_min": 30, "test_freq_mhz": 250, "srf_mhz": "5400 min"},
        {"model": "0603AS-8N0J-YY", "inductance_nh": 8.0, "tolerance": "5%", "current_ma": 700, "dcr_ohms": 0.12, "q_min": 30, "test_freq_mhz": 250, "srf_mhz": "5400 min"},
        {"model": "0603AS-8N2J-YY", "inductance_nh": 8.2, "tolerance": "5%", "current_ma": 700, "dcr_ohms": 0.12, "q_min": 30, "test_freq_mhz": 250, "srf_mhz": "5400 min"},
        {"model": "0603AS-8N7J-YY", "inductance_nh": 8.7, "tolerance": "5%", "current_ma": 700, "dcr_ohms": 0.109, "q_min": 28, "test_freq_mhz": 250, "srf_mhz": "4600 min"},
        {"model": "0603AS-8N8J-YY", "inductance_nh": 8.9, "tolerance": "5%", "current_ma": 700, "dcr_ohms": 0.109, "q_min": 28, "test_freq_mhz": 250, "srf_mhz": "4600 min"},
        {"model": "0603AS-9N5J-YY", "inductance_nh": 9.5, "tolerance": "5%", "current_ma": 700, "dcr_ohms": 0.19, "q_min": 25, "test_freq_mhz": 250, "srf_mhz": "5000 min"},
        {"model": "0603AS-010J-YY", "inductance_nh": 10, "tolerance": "5%", "current_ma": 700, "dcr_ohms": 0.13, "q_min": 31, "test_freq_mhz": 250, "srf_mhz": "4800 min"},
        {"model": "0603AS-011J-YY", "inductance_nh": 11, "tolerance": "5%", "current_ma": 700, "dcr_ohms": 0.13, "q_min": 35, "test_freq_mhz": 250, "srf_mhz": "4000 min"},
        {"model": "0603AS-012J-YY", "inductance_nh": 12, "tolerance": "5%", "current_ma": 700, "dcr_ohms": 0.13, "q_min": 35, "test_freq_mhz": 250, "srf_mhz": "4000 min"},
        {"model": "0603AS-015J-YY", "inductance_nh": 15, "tolerance": "5%", "current_ma": 700, "dcr_ohms": 0.17, "q_min": 35, "test_freq_mhz": 250, "srf_mhz": "4000 min"},
        {"model": "0603AS-016J-YY", "inductance_nh": 16, "tolerance": "5%", "current_ma": 700, "dcr_ohms": 0.17, "q_min": 35, "test_freq_mhz": 250, "srf_mhz": "3200 min"},
        {"model": "0603AS-018J-YY", "inductance_nh": 18, "tolerance": "5%", "current_ma": 700, "dcr_ohms": 0.17, "q_min": 35, "test_freq_mhz": 250, "srf_mhz": "3100 min"},
        {"model": "0603AS-022J-YY", "inductance_nh": 22, "tolerance": "5%", "current_ma": 700, "dcr_ohms": 0.19, "q_min": 38, "test_freq_mhz": 250, "srf_mhz": "3000 min"},
        {"model": "0603AS-024J-YY", "inductance_nh": 24, "tolerance": "5%", "current_ma": 600, "dcr_ohms": 0.22, "q_min": 38, "test_freq_mhz": 250, "srf_mhz": "2800 min"},
        {"model": "0603AS-027J-YY", "inductance_nh": 27, "tolerance": "5%", "current_ma": 600, "dcr_ohms": 0.22, "q_min": 40, "test_freq_mhz": 250, "srf_mhz": "2600 min"},
        {"model": "0603AS-030J-YY", "inductance_nh": 30, "tolerance": "5%", "current_ma": 600, "dcr_ohms": 0.22, "q_min": 40, "test_freq_mhz": 250, "srf_mhz": "2300 min"},
        {"model": "0603AS-033J-YY", "inductance_nh": 33, "tolerance": "5%", "current_ma": 600, "dcr_ohms": 0.22, "q_min": 40, "test_freq_mhz": 250, "srf_mhz": "2300 min"},
        {"model": "0603AS-036J-YY", "inductance_nh": 36, "tolerance": "5%", "current_ma": 600, "dcr_ohms": 0.25, "q_min": 40, "test_freq_mhz": 250, "srf_mhz": "2200 min"},
        {"model": "0603AS-039J-YY", "inductance_nh": 39, "tolerance": "5%", "current_ma": 600, "dcr_ohms": 0.25, "q_min": 40, "test_freq_mhz": 250, "srf_mhz": "2200 min"},
        {"model": "0603AS-043J-YY", "inductance_nh": 43, "tolerance": "5%", "current_ma": 600, "dcr_ohms": 0.28, "q_min": 40, "test_freq_mhz": 250, "srf_mhz": "2000 min"},
        {"model": "0603AS-047J-YY", "inductance_nh": 47, "tolerance": "5%", "current_ma": 600, "dcr_ohms": 0.28, "q_min": 38, "test_freq_mhz": 250, "srf_mhz": "2000 min"},
        {"model": "0603AS-051J-YY", "inductance_nh": 51, "tolerance": "5%", "current_ma": 600, "dcr_ohms": 0.28, "q_min": 38, "test_freq_mhz": 250, "srf_mhz": "1900 min"},
        {"model": "0603AS-056J-YY", "inductance_nh": 56, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.31, "q_min": 38, "test_freq_mhz": 250, "srf_mhz": "1900 min"},
        {"model": "0603AS-068J-YY", "inductance_nh": 68, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.34, "q_min": 37, "test_freq_mhz": 250, "srf_mhz": "1700 min"},
        {"model": "0603AS-072J-YY", "inductance_nh": 72, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.49, "q_min": 34, "test_freq_mhz": 150, "srf_mhz": "1700 min"},
        {"model": "0603AS-082J-YY", "inductance_nh": 82, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.54, "q_min": 34, "test_freq_mhz": 150, "srf_mhz": "1700 min"},
        {"model": "0603AS-090J-YY", "inductance_nh": 90, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.54, "q_min": 34, "test_freq_mhz": 150, "srf_mhz": "1700 min"},
        {"model": "0603AS-R10J-YY", "inductance_nh": 100, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.58, "q_min": 34, "test_freq_mhz": 150, "srf_mhz": "1400 min"},
        {"model": "0603AS-R11J-YY", "inductance_nh": 110, "tolerance": "5%", "current_ma": 300, "dcr_ohms": 0.61, "q_min": 34, "test_freq_mhz": 150, "srf_mhz": "1350 min"},
        {"model": "0603AS-R12J-YY", "inductance_nh": 120, "tolerance": "5%", "current_ma": 300, "dcr_ohms": 0.65, "q_min": 34, "test_freq_mhz": 150, "srf_mhz": "1300 min"},
        {"model": "0603AS-R13J-YY", "inductance_nh": 130, "tolerance": "5%", "current_ma": 200, "dcr_ohms": 0.90, "q_min": 32, "test_freq_mhz": 150, "srf_mhz": "1200 min"},
        {"model": "0603AS-R15J-YY", "inductance_nh": 150, "tolerance": "5%", "current_ma": 200, "dcr_ohms": 0.90, "q_min": 32, "test_freq_mhz": 150, "srf_mhz": "1200 min"},
        {"model": "0603AS-R18J-YY", "inductance_nh": 180, "tolerance": "5%", "current_ma": 200, "dcr_ohms": 1.20, "q_min": 32, "test_freq_mhz": 150, "srf_mhz": "1100 min"},
        {"model": "0603AS-R20J-YY", "inductance_nh": 200, "tolerance": "5%", "current_ma": 200, "dcr_ohms": 1.55, "q_min": 30, "test_freq_mhz": 150, "srf_mhz": "1100 min"},
        {"model": "0603AS-R22J-YY", "inductance_nh": 220, "tolerance": "5%", "current_ma": 150, "dcr_ohms": 1.60, "q_min": 30, "test_freq_mhz": 150, "srf_mhz": "1000 min"},
        {"model": "0603AS-R25J-YY", "inductance_nh": 250, "tolerance": "5%", "current_ma": 150, "dcr_ohms": 2.30, "q_min": 25, "test_freq_mhz": 150, "srf_mhz": "950 min"},
        {"model": "0603AS-R27J-YY", "inductance_nh": 270, "tolerance": "5%", "current_ma": 150, "dcr_ohms": 2.30, "q_min": 25, "test_freq_mhz": 150, "srf_mhz": "950 min"},
        {"model": "0603AS-R30J-YY", "inductance_nh": 300, "tolerance": "5%", "current_ma": 150, "dcr_ohms": 2.40, "q_min": 25, "test_freq_mhz": 150, "srf_mhz": "900 min"},
        {"model": "0603AS-R33J-YY", "inductance_nh": 330, "tolerance": "5%", "current_ma": 150, "dcr_ohms": 2.50, "q_min": 25, "test_freq_mhz": 150, "srf_mhz": "800 min"},
        {"model": "0603AS-R39K-YY", "inductance_nh": 390, "tolerance": "5%", "current_ma": 150, "dcr_ohms": 2.80, "q_min": 25, "test_freq_mhz": 150, "srf_mhz": "750 min"},
        {"model": "0603AS-R47K-YY", "inductance_nh": 470, "tolerance": "5%", "current_ma": 150, "dcr_ohms": 3.00, "q_min": 25, "test_freq_mhz": 150, "srf_mhz": "650 min"},
        {"model": "0603AS-R51K-YY", "inductance_nh": 510, "tolerance": "5%", "current_ma": 150, "dcr_ohms": 3.20, "q_min": 25, "test_freq_mhz": 150, "srf_mhz": "550 min"},
        {"model": "0603AS-R56K-YY", "inductance_nh": 560, "tolerance": "5%", "current_ma": 150, "dcr_ohms": 3.40, "q_min": 25, "test_freq_mhz": 150, "srf_mhz": "450 min"},
        {"model": "0603AS-R68K-YY", "inductance_nh": 680, "tolerance": "5%", "current_ma": 150, "dcr_ohms": 3.60, "q_min": 25, "test_freq_mhz": 150, "srf_mhz": "350 min"},
    ],
    "0805": [
        {"model": "0805AS-2N7K-YY", "inductance_nh": 2.7, "tolerance": "10%", "current_ma": 600, "dcr_ohms": 0.08, "q_min": 80, "test_freq_mhz": 1500, "srf_mhz": "6000 min"},
        {"model": "0805AS-3N3K-YY", "inductance_nh": 3.3, "tolerance": "10%", "current_ma": 600, "dcr_ohms": 0.08, "q_min": 50, "test_freq_mhz": 1500, "srf_mhz": "6000 min"},
        {"model": "0805AS-3N6K-YY", "inductance_nh": 3.6, "tolerance": "10%", "current_ma": 600, "dcr_ohms": 0.18, "q_min": 25, "test_freq_mhz": 1500, "srf_mhz": "6000 min"},
        {"model": "0805AS-3N9K-YY", "inductance_nh": 3.9, "tolerance": "10%", "current_ma": 600, "dcr_ohms": 0.20, "q_min": 25, "test_freq_mhz": 1000, "srf_mhz": "6500 min"},
        {"model": "0805AS-5N6K-YY", "inductance_nh": 5.6, "tolerance": "10%", "current_ma": 600, "dcr_ohms": 0.11, "q_min": 53, "test_freq_mhz": 1000, "srf_mhz": "5500 min"},
        {"model": "0805AS-5N8K-YY", "inductance_nh": 5.8, "tolerance": "10%", "current_ma": 600, "dcr_ohms": 0.11, "q_min": 50, "test_freq_mhz": 1000, "srf_mhz": "5500 min"},
        {"model": "0805AS-6N8K-YY", "inductance_nh": 6.8, "tolerance": "10%", "current_ma": 600, "dcr_ohms": 0.11, "q_min": 50, "test_freq_mhz": 500, "srf_mhz": "4500 min"},
        {"model": "0805AS-8N0K-YY", "inductance_nh": 8.0, "tolerance": "10%", "current_ma": 600, "dcr_ohms": 0.12, "q_min": 51, "test_freq_mhz": 1000, "srf_mhz": "4700 min"},
        {"model": "0805AS-8N2K-YY", "inductance_nh": 8.2, "tolerance": "10%", "current_ma": 600, "dcr_ohms": 0.12, "q_min": 50, "test_freq_mhz": 1000, "srf_mhz": "4700 min"},
        {"model": "0805AS-010J-YY", "inductance_nh": 10, "tolerance": "5%", "current_ma": 600, "dcr_ohms": 0.13, "q_min": 43, "test_freq_mhz": 1000, "srf_mhz": "4300 min"},
        {"model": "0805AS-011J-YY", "inductance_nh": 11, "tolerance": "5%", "current_ma": 600, "dcr_ohms": 0.13, "q_min": 65, "test_freq_mhz": 1000, "srf_mhz": "4000 min"},
        {"model": "0805AS-012J-YY", "inductance_nh": 12, "tolerance": "5%", "current_ma": 600, "dcr_ohms": 0.15, "q_min": 50, "test_freq_mhz": 500, "srf_mhz": "3400 min"},
        {"model": "0805AS-015J-YY", "inductance_nh": 15, "tolerance": "5%", "current_ma": 600, "dcr_ohms": 0.17, "q_min": 50, "test_freq_mhz": 500, "srf_mhz": "3400 min"},
        {"model": "0805AS-018J-YY", "inductance_nh": 18, "tolerance": "5%", "current_ma": 500, "dcr_ohms": 0.20, "q_min": 53, "test_freq_mhz": 500, "srf_mhz": "3300 min"},
        {"model": "0805AS-022J-YY", "inductance_nh": 22, "tolerance": "5%", "current_ma": 500, "dcr_ohms": 0.22, "q_min": 57, "test_freq_mhz": 500, "srf_mhz": "2600 min"},
        {"model": "0805AS-027J-YY", "inductance_nh": 27, "tolerance": "5%", "current_ma": 500, "dcr_ohms": 0.25, "q_min": 55, "test_freq_mhz": 500, "srf_mhz": "2500 min"},
        {"model": "0805AS-033J-YY", "inductance_nh": 33, "tolerance": "5%", "current_ma": 500, "dcr_ohms": 0.27, "q_min": 60, "test_freq_mhz": 500, "srf_mhz": "2050 min"},
        {"model": "0805AS-036J-YY", "inductance_nh": 36, "tolerance": "5%", "current_ma": 600, "dcr_ohms": 0.27, "q_min": 60, "test_freq_mhz": 500, "srf_mhz": "2050 min"},
        {"model": "0805AS-047J-YY", "inductance_nh": 47, "tolerance": "5%", "current_ma": 500, "dcr_ohms": 0.31, "q_min": 65, "test_freq_mhz": 500, "srf_mhz": "1650 min"},
        {"model": "0805AS-048J-YY", "inductance_nh": 48, "tolerance": "5%", "current_ma": 500, "dcr_ohms": 0.30, "q_min": 65, "test_freq_mhz": 500, "srf_mhz": "1580 min"},
        {"model": "0805AS-056J-YY", "inductance_nh": 56, "tolerance": "5%", "current_ma": 500, "dcr_ohms": 0.34, "q_min": 64, "test_freq_mhz": 500, "srf_mhz": "1550 min"},
        {"model": "0805AS-068J-YY", "inductance_nh": 68, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.38, "q_min": 65, "test_freq_mhz": 500, "srf_mhz": "1450 min"},
        {"model": "0805AS-075J-YY", "inductance_nh": 75, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.42, "q_min": 65, "test_freq_mhz": 500, "srf_mhz": "1300 min"},
        {"model": "0805AS-082J-YY", "inductance_nh": 82, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.42, "q_min": 67, "test_freq_mhz": 500, "srf_mhz": "1300 min"},
        {"model": "0805AS-R10J-YY", "inductance_nh": 100, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.46, "q_min": 65, "test_freq_mhz": 500, "srf_mhz": "1200 min"},
        {"model": "0805AS-R12J-YY", "inductance_nh": 120, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.51, "q_min": 52, "test_freq_mhz": 250, "srf_mhz": "1100 min"},
        {"model": "0805AS-R13J-YY", "inductance_nh": 130, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.56, "q_min": 53, "test_freq_mhz": 250, "srf_mhz": "920 min"},
        {"model": "0805AS-R15J-YY", "inductance_nh": 150, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.56, "q_min": 60, "test_freq_mhz": 250, "srf_mhz": "920 min"},
        {"model": "0805AS-R18J-YY", "inductance_nh": 180, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.64, "q_min": 50, "test_freq_mhz": 250, "srf_mhz": "870 min"},
        {"model": "0805AS-R20J-YY", "inductance_nh": 200, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.70, "q_min": 54, "test_freq_mhz": 250, "srf_mhz": "850 min"},
        {"model": "0805AS-R22J-YY", "inductance_nh": 220, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.70, "q_min": 59, "test_freq_mhz": 250, "srf_mhz": "850 min"},
        {"model": "0805AS-R24J-YY", "inductance_nh": 240, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.80, "q_min": 52, "test_freq_mhz": 250, "srf_mhz": "850 min"},
        {"model": "0805AS-R25J-YY", "inductance_nh": 250, "tolerance": "5%", "current_ma": 400, "dcr_ohms": 0.80, "q_min": 52, "test_freq_mhz": 250, "srf_mhz": "850 min"},
        {"model": "0805AS-R27J-YY", "inductance_nh": 270, "tolerance": "5%", "current_ma": 280, "dcr_ohms": 1.00, "q_min": 40, "test_freq_mhz": 100, "srf_mhz": "820 min"},
        {"model": "0805AS-R29J-YY", "inductance_nh": 290, "tolerance": "5%", "current_ma": 260, "dcr_ohms": 1.00, "q_min": 40, "test_freq_mhz": 100, "srf_mhz": "795 min"},
        {"model": "0805AS-R30J-YY", "inductance_nh": 300, "tolerance": "5%", "current_ma": 260, "dcr_ohms": 1.00, "q_min": 40, "test_freq_mhz": 100, "srf_mhz": "795 min"},
        {"model": "0805AS-R31J-YY", "inductance_nh": 310, "tolerance": "5%", "current_ma": 260, "dcr_ohms": 1.00, "q_min": 40, "test_freq_mhz": 100, "srf_mhz": "795 min"},
        {"model": "0805AS-R32J-YY", "inductance_nh": 320, "tolerance": "5%", "current_ma": 260, "dcr_ohms": 1.00, "q_min": 40, "test_freq_mhz": 100, "srf_mhz": "790 min"},
        {"model": "0805AS-R33J-YY", "inductance_nh": 330, "tolerance": "5%", "current_ma": 260, "dcr_ohms": 1.00, "q_min": 40, "test_freq_mhz": 100, "srf_mhz": "790 min"},
        {"model": "0805AS-R34J-YY", "inductance_nh": 340, "tolerance": "5%", "current_ma": 260, "dcr_ohms": 1.00, "q_min": 40, "test_freq_mhz": 100, "srf_mhz": "790 min"},
        {"model": "0805AS-R35J-YY", "inductance_nh": 350, "tolerance": "5%", "current_ma": 200, "dcr_ohms": 2.00, "q_min": 40, "test_freq_mhz": 100, "srf_mhz": "750 min"},
        {"model": "0805AS-R39J-YY", "inductance_nh": 390, "tolerance": "5%", "current_ma": 200, "dcr_ohms": 2.00, "q_min": 42, "test_freq_mhz": 100, "srf_mhz": "750 min"},
        {"model": "0805AS-R45J-YY", "inductance_nh": 450, "tolerance": "5%", "current_ma": 170, "dcr_ohms": 2.50, "q_min": 40, "test_freq_mhz": 100, "srf_mhz": "720 min"},
        {"model": "0805AS-R47J-YY", "inductance_nh": 470, "tolerance": "5%", "current_ma": 170, "dcr_ohms": 2.50, "q_min": 40, "test_freq_mhz": 100, "srf_mhz": "720 min"},
        {"model": "0805AS-R51J-YY", "inductance_nh": 510, "tolerance": "5%", "current_ma": 170, "dcr_ohms": 3.50, "q_min": 40, "test_freq_mhz": 100, "srf_mhz": "650 min"},
        {"model": "0805AS-R56J-YY", "inductance_nh": 560, "tolerance": "5%", "current_ma": 170, "dcr_ohms": 3.50, "q_min": 40, "test_freq_mhz": 100, "srf_mhz": "650 min"},
        {"model": "0805AS-R62J-YY", "inductance_nh": 620, "tolerance": "5%", "current_ma": 170, "dcr_ohms": 3.50, "q_min": 40, "test_freq_mhz": 100, "srf_mhz": "630 min"},
        {"model": "0805AS-R68J-YY", "inductance_nh": 680, "tolerance": "5%", "current_ma": 170, "dcr_ohms": 3.50, "q_min": 37, "test_freq_mhz": 75, "srf_mhz": "400 min"},
        {"model": "0805AS-R75K-YY", "inductance_nh": 750, "tolerance": "10%", "current_ma": 180, "dcr_ohms": 2.35, "q_min": 23, "test_freq_mhz": 50, "srf_mhz": "215 typ"},
        {"model": "0805AS-R80K-YY", "inductance_nh": 800, "tolerance": "10%", "current_ma": 180, "dcr_ohms": 2.35, "q_min": 23, "test_freq_mhz": 50, "srf_mhz": "215 typ"},
        {"model": "0805AS-R82K-YY", "inductance_nh": 820, "tolerance": "10%", "current_ma": 180, "dcr_ohms": 2.35, "q_min": 23, "test_freq_mhz": 50, "srf_mhz": "215 typ"},
        {"model": "0805AS-R91K-YY", "inductance_nh": 910, "tolerance": "10%", "current_ma": 180, "dcr_ohms": 2.35, "q_min": 23, "test_freq_mhz": 50, "srf_mhz": "215 typ"},
        {"model": "0805AS-I10K-YY", "inductance_nh": 1000, "tolerance": "10%", "current_ma": 180, "dcr_ohms": 2.35, "q_min": 23, "test_freq_mhz": 50, "srf_mhz": "215 typ"},
        {"model": "0805AS-I12K-YY", "inductance_nh": 1200, "tolerance": "10%", "current_ma": 200, "dcr_ohms": 2.80, "q_min": 15, "test_freq_mhz": 50, "srf_mhz": "150 typ"},
        {"model": "0805AS-I15K-YY", "inductance_nh": 1500, "tolerance": "10%", "current_ma": 200, "dcr_ohms": 3.00, "q_min": 15, "test_freq_mhz": 50, "srf_mhz": "150 typ"},
        {"model": "0805AS-I18K-YY", "inductance_nh": 1800, "tolerance": "10%", "current_ma": 200, "dcr_ohms": 3.00, "q_min": 15, "test_freq_mhz": 50, "srf_mhz": "80 typ"},
        {"model": "0805AS-ZR0K-YY", "inductance_nh": 2000, "tolerance": "10%", "current_ma": 200, "dcr_ohms": 3.00, "q_min": 15, "test_freq_mhz": 50, "srf_mhz": "80 typ"},
        {"model": "0805AS-ZR2K-YY", "inductance_nh": 2200, "tolerance": "10%", "current_ma": 200, "dcr_ohms": 3.00, "q_min": 15, "test_freq_mhz": 50, "srf_mhz": "80 typ"},
        {"model": "0805AS-ZR4K-YY", "inductance_nh": 2400, "tolerance": "10%", "current_ma": 200, "dcr_ohms": 3.00, "q_min": 15, "test_freq_mhz": 50, "srf_mhz": "80 typ"},
        {"model": "0805AS-ZR7K-YY", "inductance_nh": 2700, "tolerance": "10%", "current_ma": 200, "dcr_ohms": 3.00, "q_min": 15, "test_freq_mhz": 50, "srf_mhz": "80 typ"},
        {"model": "0805AS-ZR9K-YY", "inductance_nh": 3000, "tolerance": "10%", "current_ma": 200, "dcr_ohms": 3.00, "q_min": 15, "test_freq_mhz": 50, "srf_mhz": "80 typ"},
        {"model": "0805AS-ZR3K-YY", "inductance_nh": 3300, "tolerance": "10%", "current_ma": 200, "dcr_ohms": 3.00, "q_min": 15, "test_freq_mhz": 50, "srf_mhz": "80 typ"},
        {"model": "0805AS-ZR6K-YY", "inductance_nh": 3600, "tolerance": "10%", "current_ma": 200, "dcr_ohms": 3.00, "q_min": 15, "test_freq_mhz": 50, "srf_mhz": "80 typ"},
        {"model": "0805AS-ZR5K-YY", "inductance_nh": 3900, "tolerance": "10%", "current_ma": 200, "dcr_ohms": 3.00, "q_min": 15, "test_freq_mhz": 50, "srf_mhz": "80 typ"},
        {"model": "0805AS-ZR4K-YY", "inductance_nh": 4200, "tolerance": "10%", "current_ma": 200, "dcr_ohms": 3.00, "q_min": 15, "test_freq_mhz": 50, "srf_mhz": "80 typ"},
        {"model": "0805AS-ZR7K-YY", "inductance_nh": 4700, "tolerance": "10%", "current_ma": 200, "dcr_ohms": 3.00, "q_min": 15, "test_freq_mhz": 50, "srf_mhz": "80 typ"},
    ],
    "1206": [
        {"model": "1206AS-3N3M-YY", "inductance_nh": 3.3, "tolerance": "20%", "current_ma": 1000, "dcr_ohms": 0.05, "q_min": 30, "test_freq_mhz": 300, "srf_mhz": "6000 min"},
        {"model": "1206AS-6N8K-YY", "inductance_nh": 6.8, "tolerance": "10%", "current_ma": 1000, "dcr_ohms": 0.07, "q_min": 37, "test_freq_mhz": 300, "srf_mhz": "5500 min"},
        {"model": "1206AS-010J-YY", "inductance_nh": 10, "tolerance": "5%", "current_ma": 1000, "dcr_ohms": 0.08, "q_min": 40, "test_freq_mhz": 300, "srf_mhz": "4000 min"},
        {"model": "1206AS-012J-YY", "inductance_nh": 12, "tolerance": "5%", "current_ma": 1000, "dcr_ohms": 0.08, "q_min": 51, "test_freq_mhz": 300, "srf_mhz": "3200 min"},
        {"model": "1206AS-015J-YY", "inductance_nh": 15, "tolerance": "5%", "current_ma": 1000, "dcr_ohms": 0.10, "q_min": 51, "test_freq_mhz": 300, "srf_mhz": "3200 min"},
        {"model": "1206AS-018J-YY", "inductance_nh": 18, "tolerance": "5%", "current_ma": 1000, "dcr_ohms": 0.10, "q_min": 51, "test_freq_mhz": 300, "srf_mhz": "2800 min"},
        {"model": "1206AS-022J-YY", "inductance_nh": 22, "tolerance": "5%", "current_ma": 1000, "dcr_ohms": 0.10, "q_min": 52, "test_freq_mhz": 300, "srf_mhz": "2200 min"},
        {"model": "1206AS-027J-YY", "inductance_nh": 27, "tolerance": "5%", "current_ma": 1000, "dcr_ohms": 0.11, "q_min": 52, "test_freq_mhz": 300, "srf_mhz": "1800 min"},
        {"model": "1206AS-030J-YY", "inductance_nh": 30, "tolerance": "5%", "current_ma": 1000, "dcr_ohms": 0.11, "q_min": 52, "test_freq_mhz": 300, "srf_mhz": "1800 min"},
        {"model": "1206AS-033J-YY", "inductance_nh": 33, "tolerance": "5%", "current_ma": 1000, "dcr_ohms": 0.11, "q_min": 56, "test_freq_mhz": 300, "srf_mhz": "1800 min"},
        {"model": "1206AS-039J-YY", "inductance_nh": 39, "tolerance": "5%", "current_ma": 1000, "dcr_ohms": 0.12, "q_min": 64, "test_freq_mhz": 300, "srf_mhz": "1800 min"},
        {"model": "1206AS-047J-YY", "inductance_nh": 47, "tolerance": "5%", "current_ma": 1000, "dcr_ohms": 0.13, "q_min": 64, "test_freq_mhz": 300, "srf_mhz": "1500 min"},
        {"model": "1206AS-056J-YY", "inductance_nh": 56, "tolerance": "5%", "current_ma": 1000, "dcr_ohms": 0.14, "q_min": 64, "test_freq_mhz": 300, "srf_mhz": "1450 min"},
        {"model": "1206AS-068J-YY", "inductance_nh": 68, "tolerance": "5%", "current_ma": 900, "dcr_ohms": 0.26, "q_min": 61, "test_freq_mhz": 300, "srf_mhz": "1200 min"},
        {"model": "1206AS-082J-YY", "inductance_nh": 82, "tolerance": "5%", "current_ma": 900, "dcr_ohms": 0.21, "q_min": 66, "test_freq_mhz": 300, "srf_mhz": "1200 min"},
        {"model": "1206AS-R10J-YY", "inductance_nh": 100, "tolerance": "5%", "current_ma": 850, "dcr_ohms": 0.26, "q_min": 55, "test_freq_mhz": 300, "srf_mhz": "1100 min"},
        {"model": "1206AS-R12J-YY", "inductance_nh": 120, "tolerance": "5%", "current_ma": 800, "dcr_ohms": 0.26, "q_min": 75, "test_freq_mhz": 300, "srf_mhz": "1100 min"},
        {"model": "1206AS-R13J-YY", "inductance_nh": 130, "tolerance": "5%", "current_ma": 750, "dcr_ohms": 0.31, "q_min": 75, "test_freq_mhz": 300, "srf_mhz": "950 min"},
        {"model": "1206AS-R15J-YY", "inductance_nh": 150, "tolerance": "5%", "current_ma": 750, "dcr_ohms": 0.31, "q_min": 65, "test_freq_mhz": 300, "srf_mhz": "950 min"},
        {"model": "1206AS-R18J-YY", "inductance_nh": 180, "tolerance": "5%", "current_ma": 700, "dcr_ohms": 0.43, "q_min": 75, "test_freq_mhz": 300, "srf_mhz": "900 min"},
        {"model": "1206AS-R21J-YY", "inductance_nh": 210, "tolerance": "5%", "current_ma": 670, "dcr_ohms": 0.50, "q_min": 75, "test_freq_mhz": 300, "srf_mhz": "760 min"},
        {"model": "1206AS-R22J-YY", "inductance_nh": 220, "tolerance": "5%", "current_ma": 670, "dcr_ohms": 0.50, "q_min": 75, "test_freq_mhz": 300, "srf_mhz": "760 min"},
        {"model": "1206AS-R24J-YY", "inductance_nh": 240, "tolerance": "5%", "current_ma": 630, "dcr_ohms": 0.56, "q_min": 57, "test_freq_mhz": 300, "srf_mhz": "730 min"},
        {"model": "1206AS-R27J-YY", "inductance_nh": 270, "tolerance": "5%", "current_ma": 630, "dcr_ohms": 0.56, "q_min": 57, "test_freq_mhz": 300, "srf_mhz": "730 min"},
        {"model": "1206AS-R29J-YY", "inductance_nh": 290, "tolerance": "5%", "current_ma": 590, "dcr_ohms": 0.62, "q_min": 57, "test_freq_mhz": 150, "srf_mhz": "650 min"},
        {"model": "1206AS-R33J-YY", "inductance_nh": 330, "tolerance": "5%", "current_ma": 590, "dcr_ohms": 0.62, "q_min": 55, "test_freq_mhz": 150, "srf_mhz": "650 min"},
        {"model": "1206AS-R39J-YY", "inductance_nh": 390, "tolerance": "5%", "current_ma": 530, "dcr_ohms": 0.75, "q_min": 55, "test_freq_mhz": 150, "srf_mhz": "600 min"},
        {"model": "1206AS-R47J-YY", "inductance_nh": 470, "tolerance": "5%", "current_ma": 490, "dcr_ohms": 1.30, "q_min": 52, "test_freq_mhz": 150, "srf_mhz": "550 min"},
        {"model": "1206AS-R50K-YY", "inductance_nh": 500, "tolerance": "10%", "current_ma": 460, "dcr_ohms": 1.30, "q_min": 45, "test_freq_mhz": 150, "srf_mhz": "470 typ"},
        {"model": "1206AS-R56K-YY", "inductance_nh": 560, "tolerance": "10%", "current_ma": 460, "dcr_ohms": 1.34, "q_min": 45, "test_freq_mhz": 150, "srf_mhz": "470 typ"},
        {"model": "1206AS-R68K-YY", "inductance_nh": 680, "tolerance": "10%", "current_ma": 430, "dcr_ohms": 1.58, "q_min": 45, "test_freq_mhz": 150, "srf_mhz": "450 typ"},
        {"model": "1206AS-R82K-YY", "inductance_nh": 820, "tolerance": "10%", "current_ma": 400, "dcr_ohms": 1.82, "q_min": 45, "test_freq_mhz": 150, "srf_mhz": "420 typ"},
        {"model": "1206AS-R91K-YY", "inductance_nh": 910, "tolerance": "10%", "current_ma": 300, "dcr_ohms": 1.87, "q_min": 45, "test_freq_mhz": 150, "srf_mhz": "416 typ"},
        {"model": "1206AS-I10K-YY", "inductance_nh": 1000, "tolerance": "10%", "current_ma": 320, "dcr_ohms": 2.80, "q_min": 45, "test_freq_mhz": 150, "srf_mhz": "400 typ"},
        {"model": "1206AS-I12K-YY", "inductance_nh": 1200, "tolerance": "10%", "current_ma": 300, "dcr_ohms": 3.20, "q_min": 45, "test_freq_mhz": 150, "srf_mhz": "380 typ"},
        {"model": "1206AS-I22K-YY", "inductance_nh": 2200, "tolerance": "10%", "current_ma": 280, "dcr_ohms": 4.50, "q_min": 32, "test_freq_mhz": 150, "srf_mhz": "160 typ"},
        {"model": "1206AS-I27K-YY", "inductance_nh": 2700, "tolerance": "10%", "current_ma": 145, "dcr_ohms": 5.50, "q_min": 25, "test_freq_mhz": 50, "srf_mhz": "160 typ"},
        {"model": "1206AS-I33K-YY", "inductance_nh": 3300, "tolerance": "10%", "current_ma": 130, "dcr_ohms": 6.50, "q_min": 20, "test_freq_mhz": 50, "srf_mhz": "140 typ"},
        {"model": "1206AS-I47K-YY", "inductance_nh": 4700, "tolerance": "10%", "current_ma": 120, "dcr_ohms": 7.20, "q_min": 20, "test_freq_mhz": 50, "srf_mhz": "120 typ"},
    ],
    "1210": [
        {"model": "1210AS-010K-YY", "inductance_nh": 10, "tolerance": "10%", "current_ma": 1000, "dcr_ohms": 0.08, "q_min": 50, "test_freq_mhz": 500, "srf_mhz": "4100 min"},
        {"model": "1210AS-012K-YY", "inductance_nh": 12, "tolerance": "10%", "current_ma": 1000, "dcr_ohms": 0.09, "q_min": 50, "test_freq_mhz": 500, "srf_mhz": "2400 min"},
        {"model": "1210AS-015K-YY", "inductance_nh": 15, "tolerance": "10%", "current_ma": 1000, "dcr_ohms": 0.10, "q_min": 50, "test_freq_mhz": 500, "srf_mhz": "2400 min"},
        {"model": "1210AS-018K-YY", "inductance_nh": 18, "tolerance": "10%", "current_ma": 1000, "dcr_ohms": 0.11, "q_min": 50, "test_freq_mhz": 350, "srf_mhz": "2400 min"},
        {"model": "1210AS-022K-YY", "inductance_nh": 22, "tolerance": "10%", "current_ma": 1000, "dcr_ohms": 0.12, "q_min": 55, "test_freq_mhz": 350, "srf_mhz": "2400 min"},
        {"model": "1210AS-027J-YY", "inductance_nh": 27, "tolerance": "5%", "current_ma": 1000, "dcr_ohms": 0.13, "q_min": 55, "test_freq_mhz": 350, "srf_mhz": "1800 min"},
        {"model": "1210AS-033J-YY", "inductance_nh": 33, "tolerance": "5%", "current_ma": 1000, "dcr_ohms": 0.14, "q_min": 60, "test_freq_mhz": 350, "srf_mhz": "1600 min"},
        {"model": "1210AS-039J-YY", "inductance_nh": 39, "tolerance": "5%", "current_ma": 1000, "dcr_ohms": 0.15, "q_min": 60, "test_freq_mhz": 350, "srf_mhz": "1500 min"},
        {"model": "1210AS-047J-YY", "inductance_nh": 47, "tolerance": "5%", "current_ma": 1000, "dcr_ohms": 0.16, "q_min": 65, "test_freq_mhz": 350, "srf_mhz": "1200 min"},
        {"model": "1210AS-056J-YY", "inductance_nh": 56, "tolerance": "5%", "current_ma": 1000, "dcr_ohms": 0.16, "q_min": 65, "test_freq_mhz": 350, "srf_mhz": "1200 min"},
        {"model": "1210AS-068J-YY", "inductance_nh": 68, "tolerance": "5%", "current_ma": 1000, "dcr_ohms": 0.20, "q_min": 65, "test_freq_mhz": 350, "srf_mhz": "1000 min"},
        {"model": "1210AS-082J-YY", "inductance_nh": 82, "tolerance": "5%", "current_ma": 1000, "dcr_ohms": 0.22, "q_min": 65, "test_freq_mhz": 350, "srf_mhz": "1000 min"},
        {"model": "1210AS-R10J-YY", "inductance_nh": 100, "tolerance": "5%", "current_ma": 980, "dcr_ohms": 0.24, "q_min": 60, "test_freq_mhz": 350, "srf_mhz": "1000 min"},
        {"model": "1210AS-R12J-YY", "inductance_nh": 120, "tolerance": "5%", "current_ma": 920, "dcr_ohms": 0.26, "q_min": 60, "test_freq_mhz": 350, "srf_mhz": "850 min"},
        {"model": "1210AS-R15J-YY", "inductance_nh": 150, "tolerance": "5%", "current_ma": 870, "dcr_ohms": 0.29, "q_min": 60, "test_freq_mhz": 750, "srf_mhz": "750 min"},
        {"model": "1210AS-R18J-YY", "inductance_nh": 180, "tolerance": "5%", "current_ma": 830, "dcr_ohms": 0.31, "q_min": 60, "test_freq_mhz": 700, "srf_mhz": "700 min"},
        {"model": "1210AS-R22J-YY", "inductance_nh": 220, "tolerance": "5%", "current_ma": 790, "dcr_ohms": 0.35, "q_min": 60, "test_freq_mhz": 650, "srf_mhz": "650 min"},
        {"model": "1210AS-R27J-YY", "inductance_nh": 270, "tolerance": "5%", "current_ma": 730, "dcr_ohms": 0.42, "q_min": 45, "test_freq_mhz": 600, "srf_mhz": "600 min"},
        {"model": "1210AS-R33J-YY", "inductance_nh": 330, "tolerance": "5%", "current_ma": 680, "dcr_ohms": 0.49, "q_min": 45, "test_freq_mhz": 500, "srf_mhz": "500 min"},
        {"model": "1210AS-R37J-YY", "inductance_nh": 370, "tolerance": "5%", "current_ma": 610, "dcr_ohms": 0.52, "q_min": 45, "test_freq_mhz": 400, "srf_mhz": "400 min"},
        {"model": "1210AS-R39J-YY", "inductance_nh": 390, "tolerance": "5%", "current_ma": 640, "dcr_ohms": 0.54, "q_min": 45, "test_freq_mhz": 450, "srf_mhz": "450 min"},
        {"model": "1210AS-R47J-YY", "inductance_nh": 470, "tolerance": "5%", "current_ma": 610, "dcr_ohms": 0.60, "q_min": 45, "test_freq_mhz": 450, "srf_mhz": "450 min"},
        {"model": "1210AS-R56J-YY", "inductance_nh": 560, "tolerance": "5%", "current_ma": 460, "dcr_ohms": 1.00, "q_min": 45, "test_freq_mhz": 415, "srf_mhz": "415 min"},
        {"model": "1210AS-R68J-YY", "inductance_nh": 680, "tolerance": "5%", "current_ma": 420, "dcr_ohms": 1.15, "q_min": 45, "test_freq_mhz": 350, "srf_mhz": "350 min"},
        {"model": "1210AS-R82J-YY", "inductance_nh": 820, "tolerance": "5%", "current_ma": 350, "dcr_ohms": 1.93, "q_min": 45, "test_freq_mhz": 300, "srf_mhz": "300 min"},
        {"model": "1210AS-I10K-YY", "inductance_nh": 1000, "tolerance": "10%", "current_ma": 330, "dcr_ohms": 2.16, "q_min": 35, "test_freq_mhz": 50, "srf_mhz": "290 typ"},
        {"model": "1210AS-I12K-YY", "inductance_nh": 1200, "tolerance": "10%", "current_ma": 310, "dcr_ohms": 2.38, "q_min": 35, "test_freq_mhz": 50, "srf_mhz": "250 typ"},
        {"model": "1210AS-I15K-YY", "inductance_nh": 1500, "tolerance": "10%", "current_ma": 300, "dcr_ohms": 2.64, "q_min": 25, "test_freq_mhz": 50, "srf_mhz": "200 typ"},
        {"model": "1210AS-I18K-YY", "inductance_nh": 1800, "tolerance": "10%", "current_ma": 290, "dcr_ohms": 2.76, "q_min": 25, "test_freq_mhz": 50, "srf_mhz": "160 typ"},
        {"model": "1210AS-I22K-YY", "inductance_nh": 2200, "tolerance": "10%", "current_ma": 280, "dcr_ohms": 2.98, "q_min": 25, "test_freq_mhz": 50, "srf_mhz": "140 typ"},
        {"model": "1210AS-I27K-YY", "inductance_nh": 2700, "tolerance": "10%", "current_ma": 260, "dcr_ohms": 3.30, "q_min": 25, "test_freq_mhz": 25, "srf_mhz": "140 typ"},
        {"model": "1210AS-I33K-YY", "inductance_nh": 3300, "tolerance": "10%", "current_ma": 250, "dcr_ohms": 3.66, "q_min": 25, "test_freq_mhz": 25, "srf_mhz": "120 typ"},
        {"model": "1210AS-I39K-YY", "inductance_nh": 3900, "tolerance": "10%", "current_ma": 240, "dcr_ohms": 4.00, "q_min": 20, "test_freq_mhz": 25, "srf_mhz": "100 typ"},
        {"model": "1210AS-I47K-YY", "inductance_nh": 4700, "tolerance": "10%", "current_ma": 230, "dcr_ohms": 4.30, "q_min": 20, "test_freq_mhz": 25, "srf_mhz": "90 typ"},
        {"model": "1210AS-I56K-YY", "inductance_nh": 5600, "tolerance": "10%", "current_ma": 230, "dcr_ohms": 4.30, "q_min": 15, "test_freq_mhz": 25, "srf_mhz": "60 typ"},
        {"model": "1210AS-I68K-YY", "inductance_nh": 6800, "tolerance": "10%", "current_ma": 210, "dcr_ohms": 5.20, "q_min": 15, "test_freq_mhz": 25, "srf_mhz": "60 typ"},
        {"model": "1210AS-I82K-YY", "inductance_nh": 8200, "tolerance": "10%", "current_ma": 168, "dcr_ohms": 5.90, "q_min": 17, "test_freq_mhz": 7.9, "srf_mhz": "45 typ"},
        {"model": "1210AS-I100K-YY", "inductance_nh": 10000, "tolerance": "10%", "current_ma": 160, "dcr_ohms": 6.00, "q_min": 17, "test_freq_mhz": 7.9, "srf_mhz": "38 typ"},
        {"model": "1210AS-I150K-YY", "inductance_nh": 15000, "tolerance": "10%", "current_ma": 120, "dcr_ohms": 7.00, "q_min": 15, "test_freq_mhz": 7.9, "srf_mhz": "20 typ"},
    ],
    "1812": [
        # Valores originalmente em µH, convertidos para nH multiplicando por 1000
        {"model": "1812AS-015K-YY", "inductance_nh": 15, "tolerance": "10%", "current_ma": 1550, "dcr_ohms": 0.035, "q_min": 70, "test_freq_mhz": 500, "srf_mhz": "2400 min"},
        {"model": "1812AS-022K-YY", "inductance_nh": 22, "tolerance": "10%", "current_ma": 1550, "dcr_ohms": 0.050, "q_min": 70, "test_freq_mhz": 500, "srf_mhz": "2300 min"},
        {"model": "1812AS-033K-YY", "inductance_nh": 33, "tolerance": "10%", "current_ma": 1500, "dcr_ohms": 0.060, "q_min": 70, "test_freq_mhz": 500, "srf_mhz": "1850 min"},
        {"model": "1812AS-047K-YY", "inductance_nh": 47, "tolerance": "10%", "current_ma": 1500, "dcr_ohms": 0.060, "q_min": 70, "test_freq_mhz": 250, "srf_mhz": "1100 min"},
        {"model": "1812AS-056K-YY", "inductance_nh": 56, "tolerance": "10%", "current_ma": 1350, "dcr_ohms": 0.070, "q_min": 70, "test_freq_mhz": 250, "srf_mhz": "900 min"},
        {"model": "1812AS-068K-YY", "inductance_nh": 68, "tolerance": "10%", "current_ma": 1350, "dcr_ohms": 0.070, "q_min": 70, "test_freq_mhz": 250, "srf_mhz": "900 min"},
        {"model": "1812AS-082K-YY", "inductance_nh": 82, "tolerance": "10%", "current_ma": 1300, "dcr_ohms": 0.080, "q_min": 70, "test_freq_mhz": 250, "srf_mhz": "900 min"},
        {"model": "1812AS-R10K-YY", "inductance_nh": 100, "tolerance": "10%", "current_ma": 1300, "dcr_ohms": 0.080, "q_min": 70, "test_freq_mhz": 250, "srf_mhz": "650 min"},
        {"model": "1812AS-R12K-YY", "inductance_nh": 120, "tolerance": "10%", "current_ma": 1050, "dcr_ohms": 0.10, "q_min": 70, "test_freq_mhz": 100, "srf_mhz": "650 min"},
        {"model": "1812AS-R15K-YY", "inductance_nh": 150, "tolerance": "10%", "current_ma": 1000, "dcr_ohms": 0.13, "q_min": 68, "test_freq_mhz": 100, "srf_mhz": "600 min"},
        {"model": "1812AS-R22K-YY", "inductance_nh": 220, "tolerance": "10%", "current_ma": 800, "dcr_ohms": 0.17, "q_min": 68, "test_freq_mhz": 100, "srf_mhz": "500 min"},
        {"model": "1812AS-R27K-YY", "inductance_nh": 270, "tolerance": "10%", "current_ma": 800, "dcr_ohms": 0.19, "q_min": 68, "test_freq_mhz": 100, "srf_mhz": "500 min"},
        {"model": "1812AS-R33K-YY", "inductance_nh": 330, "tolerance": "10%", "current_ma": 700, "dcr_ohms": 0.20, "q_min": 64, "test_freq_mhz": 100, "srf_mhz": "400 min"},
        {"model": "1812AS-R37K-YY", "inductance_nh": 370, "tolerance": "10%", "current_ma": 650, "dcr_ohms": 0.22, "q_min": 64, "test_freq_mhz": 100, "srf_mhz": "400 min"},
        {"model": "1812AS-R47K-YY", "inductance_nh": 470, "tolerance": "10%", "current_ma": 500, "dcr_ohms": 0.30, "q_min": 64, "test_freq_mhz": 100, "srf_mhz": "400 min"},
        {"model": "1812AS-I10K-YY", "inductance_nh": 1000, "tolerance": "10%", "current_ma": 480, "dcr_ohms": 1.20, "q_min": 62, "test_freq_mhz": 50, "srf_mhz": "277 min"},
        {"model": "1812AS-I2R-YY", "inductance_nh": 1200, "tolerance": "10%", "current_ma": 480, "dcr_ohms": 1.20, "q_min": 60, "test_freq_mhz": 50, "srf_mhz": "240 min"},
        {"model": "1812AS-I5R-YY", "inductance_nh": 1500, "tolerance": "10%", "current_ma": 430, "dcr_ohms": 1.60, "q_min": 60, "test_freq_mhz": 50, "srf_mhz": "220 min"},
        {"model": "1812AS-I8R-YY", "inductance_nh": 1800, "tolerance": "10%", "current_ma": 380, "dcr_ohms": 2.00, "q_min": 60, "test_freq_mhz": 50, "srf_mhz": "200 min"},
        {"model": "1812AS-I2R2K-YY", "inductance_nh": 2200, "tolerance": "10%", "current_ma": 340, "dcr_ohms": 2.20, "q_min": 63, "test_freq_mhz": 50, "srf_mhz": "180 min"},
        {"model": "1812AS-I2R7K-YY", "inductance_nh": 2700, "tolerance": "10%", "current_ma": 300, "dcr_ohms": 3.20, "q_min": 63, "test_freq_mhz": 50, "srf_mhz": "160 min"},
        {"model": "1812AS-I3R3K-YY", "inductance_nh": 3300, "tolerance": "10%", "current_ma": 270, "dcr_ohms": 3.80, "q_min": 50, "test_freq_mhz": 50, "srf_mhz": "145 typ"},
        {"model": "1812AS-I3R9K-YY", "inductance_nh": 3900, "tolerance": "10%", "current_ma": 240, "dcr_ohms": 5.00, "q_min": 50, "test_freq_mhz": 50, "srf_mhz": "130 typ"},
        {"model": "1812AS-I4R7K-YY", "inductance_nh": 4700, "tolerance": "10%", "current_ma": 230, "dcr_ohms": 5.40, "q_min": 50, "test_freq_mhz": 50, "srf_mhz": "120 typ"},
        {"model": "1812AS-I5R6K-YY", "inductance_nh": 5600, "tolerance": "10%", "current_ma": 220, "dcr_ohms": 5.70, "q_min": 40, "test_freq_mhz": 50, "srf_mhz": "105 typ"},
        {"model": "1812AS-I6R8K-YY", "inductance_nh": 6800, "tolerance": "10%", "current_ma": 210, "dcr_ohms": 6.60, "q_min": 40, "test_freq_mhz": 50, "srf_mhz": "103 typ"},
        {"model": "1812AS-I8R2K-YY", "inductance_nh": 8200, "tolerance": "10%", "current_ma": 200, "dcr_ohms": 7.00, "q_min": 38, "test_freq_mhz": 50, "srf_mhz": "94 typ"},
        {"model": "1812AS-I10K-YY", "inductance_nh": 10000, "tolerance": "10%", "current_ma": 190, "dcr_ohms": 7.70, "q_min": 38, "test_freq_mhz": 50, "srf_mhz": "80 typ"},
        {"model": "1812AS-I20K-YY", "inductance_nh": 12000, "tolerance": "10%", "current_ma": 180, "dcr_ohms": 8.70, "q_min": 38, "test_freq_mhz": 10, "srf_mhz": "74 typ"},
        {"model": "1812AS-I50K-YY", "inductance_nh": 15000, "tolerance": "10%", "current_ma": 170, "dcr_ohms": 9.60, "q_min": 37, "test_freq_mhz": 10, "srf_mhz": "59 typ"},
        {"model": "1812AS-I80K-YY", "inductance_nh": 18000, "tolerance": "10%", "current_ma": 160, "dcr_ohms": 10.5, "q_min": 36, "test_freq_mhz": 10, "srf_mhz": "59 typ"},
        {"model": "1812AS-I220K-YY", "inductance_nh": 22000, "tolerance": "10%", "current_ma": 155, "dcr_ohms": 13.0, "q_min": 36, "test_freq_mhz": 10, "srf_mhz": "45 typ"},
        {"model": "1812AS-I270K-YY", "inductance_nh": 27000, "tolerance": "10%", "current_ma": 150, "dcr_ohms": 14.0, "q_min": 36, "test_freq_mhz": 10, "srf_mhz": "35 typ"},
        {"model": "1812AS-I330K-YY", "inductance_nh": 33000, "tolerance": "10%", "current_ma": 145, "dcr_ohms": 16.5, "q_min": 36, "test_freq_mhz": 10, "srf_mhz": "35 typ"},
        {"model": "1812AS-I390K-YY", "inductance_nh": 39000, "tolerance": "10%", "current_ma": 80, "dcr_ohms": 23.5, "q_min": 32, "test_freq_mhz": 10, "srf_mhz": "25 typ"},
        {"model": "1812AS-I470K-YY", "inductance_nh": 47000, "tolerance": "10%", "current_ma": 80, "dcr_ohms": 39.0, "q_min": 32, "test_freq_mhz": 10, "srf_mhz": "20 typ"},
        {"model": "1812AS-I560K-YY", "inductance_nh": 56000, "tolerance": "10%", "current_ma": 60, "dcr_ohms": 41.0, "q_min": 32, "test_freq_mhz": 10, "srf_mhz": "20 typ"},
        {"model": "1812AS-I680K-YY", "inductance_nh": 68000, "tolerance": "10%", "current_ma": 58, "dcr_ohms": 54.0, "q_min": 32, "test_freq_mhz": 10, "srf_mhz": "18 typ"},
        {"model": "1812AS-I820K-YY", "inductance_nh": 82000, "tolerance": "10%", "current_ma": 55, "dcr_ohms": 59.0, "q_min": 32, "test_freq_mhz": 10, "srf_mhz": "15 typ"},
    ],
}

# =============================================================================
# GERAÇÃO PRINCIPAL
# =============================================================================
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mypn_counter = 1
    base_counter_per_package = 0

    for size, components in INDUCTOR_SPECS.items():
        if not components:
            print(f"Aviso: Nenhum dado encontrado para {size}. Pulando...")
            base_counter_per_package += 100000
            continue

        mypn_counter = base_counter_per_package + 1

        # Ordenar componentes por indutância (crescente)
        sorted_components = sorted(components, key=lambda x: x['inductance_nh'])

        columns = [
            "MyPN", "Name", "Description", "Value", "Info1", "Info2",
            "Symbol", "Footprint", "Footprint_Filter", "Datasheet",
            "Manufacturer", "Manufacturer_PN",
            "Category", "Subcategory", "Package", "Mount",
            "Temperature_Range", "REACH_Compliant", "RoHS_Compliant",
            "Unit", "Tolerance", "Current_Rating", "DC_Resistance",
            "Inductance", "Technology_Material", "Quality_Factor_Q", "Self_Resonant_Frequency",
            "Created_At", "Created_By"
        ]

        values_lines = []

        for comp in sorted_components:
            ind_nh = comp['inductance_nh']
            ind_str = format_inductance_value(ind_nh)
            tolerance = comp['tolerance']
            current_ma = comp.get('current_ma')
            dcr = comp.get('dcr_ohms')
            q_min = comp.get('q_min')
            srf_mhz = comp.get('srf_mhz')
            model = comp['model']

            # Tecnologia/material: Ceramic para todos os AS series
            tech_material = "Ceramic"

            # Formata a corrente para exibição no nome e nos campos
            current_str = format_current(current_ma) if current_ma else ""

            # Construir nome com corrente formatada (se disponível)
            if current_str:
                name = f"IND_{size}_{ind_str}H_{current_str}_{tolerance}"
            else:
                name = f"IND_{size}_{ind_str}H_{tolerance}"

            description = f"Inductor {model} {size} {ind_str}H {tolerance}"
            if current_ma:
                description += f" {current_str}"
            if dcr:
                description += f" {dcr}Ω"
            if q_min:
                description += f" Q{q_min}"

            value = ind_str
            info1 = f" {current_str}"
            info2 = f" {dcr}Ω"

            mypn = f"EL-IND-{mypn_counter:06d}"
            mypn_counter += 1

            mfg_pn = generate_part_number(model)

            # Valores padrão para campos não preenchidos
            current_val = current_str if current_str else "NULL"
            dcr_val = f"{dcr}Ω" if dcr else "NULL"
            q_val = str(int(q_min)) if q_min else "NULL"
            srf_val = str(srf_mhz) if srf_mhz else "NULL"
            tolerance_val = tolerance if tolerance else "NULL"
            metric = METRIC_CODES[size]
            symbol = "MyLib_Inductor:L"
            footprint = f"MyLib_Capacitor_SMD:L_{size}_{metric}Metric"

            values = [
                mypn, name, description, value, info1, info2,
                symbol,
                footprint,
                f"L_{size}*",
                f"{DATASHEET_BASE_URL}{model}.pdf",
                MANUFACTURER,
                mfg_pn,
                CATEGORY,
                SUBCATEGORY,
                size,
                MOUNT,
                TEMP_RANGE,
                REACH,
                ROHS,
                UNIT,
                tolerance_val,
                current_val,
                dcr_val,
                ind_str,
                tech_material,
                q_val,
                srf_val,
                "datetime('now')",
                CREATED_BY
            ]

            # Formatação para SQL
            formatted = []
            for v in values:
                if v is None or v == "NULL":
                    formatted.append("NULL")
                elif isinstance(v, int):
                    formatted.append(str(v))
                elif v == "datetime('now')":
                    formatted.append(v)
                else:
                    v_escaped = str(v).replace("'", "''")
                    formatted.append(f"'{v_escaped}'")
            values_lines.append("(" + ", ".join(formatted) + ")")

        if values_lines:
            output_file = os.path.join(script_dir, f"insert_inductor_{size}.sql")
            header = f"INSERT INTO Inductor_{size} ({', '.join(columns)}) VALUES\n"
            body = ",\n".join(values_lines) + ";"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"-- Script de inserção para Inductor_{size}\n")
                f.write(f"-- Baseado em componentes reais da FASTRON\n")
                f.write(f"-- Fonte: {size}AS.pdf\n\n")
                f.write(header)
                f.write(body)
                f.write("\n")
            print(f"Arquivo gerado: {output_file} com {len(values_lines)} inserts")

        base_counter_per_package += 100000

if __name__ == "__main__":
    main()