from dataclasses import dataclass

@dataclass
class Product:
    name: str
    price: float
    index: int = 0

class ProductFactory:

    @staticmethod
    def first() -> Product:
        return Product(
            name="Sauce Labs Backpack",
            price=29.99,
            index=0
        )

    @staticmethod
    def build(name: str = "Sauce Labs Backpack",
              price: float = 29.99,
              index: int = 0) -> Product:
        return Product(name=name, price=price, index=index)