from faker.providers import BaseProvider
import random

SHOE_BRANDS =  [
    "Nike",
    "Adidas",
    "Puma",
    "Reebok",
    "New Balance",
    "ASICS",
    "Under Armour",
    "Converse",
    "Vans",
    "Skechers",
    "Timberland",
    "Dr. Martens",
    "Birkenstock",
    "Clarks",
    "Salomon",
    "Brooks",
    "Merrell",
    "HOKA ONE ONE",
    "Balenciaga",
    "Gucci"
]


def generate_shoe_name():
    adjectives = [
        "Ultra", "Max", "Pro", "Elite", "Hyper", "Speed", "Light", "Power", "Fusion", "Quantum",
        "Prime", "Active", "Core", "Swift", "Nova", "Dynamic", "Flex", "Storm", "True", "Aero"
    ]

    nouns = [
        "Runner", "Step", "Zoom", "Trail", "Ride", "Pulse", "Force", "Edge", "Drive", "Boost",
        "Flow", "Grip", "Blaze", "Stride", "Blast", "Dash", "Track", "Form", "Wing", "Lift"
    ]

    model_codes = [
        "X", "Z", "V", "GT", "TX", "XR", "M", "LT", "FX", "HD"
    ]

    numbers = [str(n) for n in range(100, 200)]

    name = f"{random.choice(adjectives)} {random.choice(nouns)} {random.choice(model_codes)}{random.choice(numbers)}"
    return name





