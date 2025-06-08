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

SHOE_CATEGORY = [
    "Athletic",
    "Running",
    "Walking",
    "Basketball",
    "Soccer",
    "Tennis",
    "Training",
    "Casual",
    "Skate",
    "Sandals",
    "Boots",
    "Formal",
    "Loafers",
    "Slippers",
    "Outdoor",
    "Hiking",
    "Trail",
    "Work",
    "Golf",
    "Fashion",
    "Slip-On",
    "High Tops",
    "Low Tops",
    "Flip Flops",
    "Clogs"
]

def generate_price_normal_dist(mean=300.0, std=75.0, min_price=100.0, max_price=2000.0):
    """
    Generate a list of float prices from a normal distribution using the random module.

    Parameters:
        mean (float): Mean of the normal distribution.
        std (float): Standard deviation.
        count (int): Number of prices to generate.
        min_price (float): Minimum allowable price.
        max_price (float): Maximum allowable price.

    Returns:
        List[float]: List of normally-distributed float prices.
    """
    
    
    price = random.gauss(mean, std)
    price = max(min(price, max_price), min_price)
    return round(price) - 0.01

class ShoeProvider(BaseProvider):
    
    
    def _generate_shoe_name(self):
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
    
    
    def shoe_brand(self):
        return self.random_element(SHOE_BRANDS)
    
    def shoe_name(self):
        return self._generate_shoe_name()
    
    def shoe_category(self):
        return self.random_element(SHOE_CATEGORY)
    
    def shoe_price(self):
        return generate_price_normal_dist()


def client_gender() -> str:
    genders = ['M', 'F', 'X']
    return random.choices(genders, [0.3, 0.6, 0.1])[0]
        
    
        
        
    
    





