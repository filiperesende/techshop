"""Testes unitários para a classe ShoppingCart."""

import pytest

from src.cart import ShoppingCart
from src.models import Product


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def cart() -> ShoppingCart:
    """Retorna um carrinho de compras vazio."""
    return ShoppingCart()


@pytest.fixture
def product_a() -> Product:
    """Produto genérico A com preço R$ 100."""
    return Product(id=1, name="Teclado Mecânico", price=100.0)


@pytest.fixture
def product_b() -> Product:
    """Produto genérico B com preço R$ 250."""
    return Product(id=2, name="Mouse Gamer", price=250.0)


# ============================================================
# Caminhos Felizes (Happy Path)
# ============================================================


class TestAddItem:
    """Testes para o método add_item."""

    def test_add_single_item(self, cart: ShoppingCart, product_a: Product) -> None:
        """Deve adicionar um item ao carrinho vazio."""
        # Arrange
        quantity = 2

        # Act
        cart.add_item(product_a, quantity)

        # Assert
        assert len(cart.items) == 1
        assert cart.items[0].product.id == product_a.id
        assert cart.items[0].quantity == 2

    def test_add_multiple_different_items(
        self, cart: ShoppingCart, product_a: Product, product_b: Product
    ) -> None:
        """Deve adicionar produtos distintos como itens separados."""
        # Arrange
        quantity_a = 1
        quantity_b = 3

        # Act
        cart.add_item(product_a, quantity_a)
        cart.add_item(product_b, quantity_b)

        # Assert
        assert len(cart.items) == 2

    def test_add_existing_item_increments_quantity(
        self, cart: ShoppingCart, product_a: Product
    ) -> None:
        """Deve somar a quantidade quando o mesmo produto é adicionado novamente."""
        # Arrange
        cart.add_item(product_a, 2)

        # Act
        cart.add_item(product_a, 3)

        # Assert
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 5


class TestRemoveItem:
    """Testes para o método remove_item."""

    def test_remove_existing_item(
        self, cart: ShoppingCart, product_a: Product, product_b: Product
    ) -> None:
        """Deve remover o item correto pelo ID do produto."""
        # Arrange
        cart.add_item(product_a, 1)
        cart.add_item(product_b, 1)

        # Act
        cart.remove_item(product_a.id)

        # Assert
        assert len(cart.items) == 1
        assert cart.items[0].product.id == product_b.id


class TestCalculateTotal:
    """Testes para o método calculate_total."""

    def test_total_with_multiple_items(
        self, cart: ShoppingCart, product_a: Product, product_b: Product
    ) -> None:
        """Deve calcular o total corretamente com múltiplos itens."""
        # Arrange
        cart.add_item(product_a, 2)  # 2 * 100 = 200
        cart.add_item(product_b, 1)  # 1 * 250 = 250

        # Act
        total = cart.calculate_total()

        # Assert
        assert total == 450.0


class TestCalculateTotalWithDiscount:
    """Testes para o método calculate_total_with_discount."""

    def test_no_discount_below_500(self, cart: ShoppingCart, product_a: Product) -> None:
        """Não deve aplicar desconto para totais até R$ 500."""
        # Arrange
        cart.add_item(product_a, 4)  # 4 * 100 = 400

        # Act
        total = cart.calculate_total_with_discount()

        # Assert
        assert total == 400.0

    def test_10_percent_discount_above_500(
        self, cart: ShoppingCart, product_a: Product
    ) -> None:
        """Deve aplicar 10% de desconto para totais acima de R$ 500."""
        # Arrange
        cart.add_item(product_a, 6)  # 6 * 100 = 600

        # Act
        total = cart.calculate_total_with_discount()

        # Assert
        assert total == 540.0  # 600 * 0.90

    def test_20_percent_discount_above_1000(
        self, cart: ShoppingCart, product_b: Product
    ) -> None:
        """Deve aplicar 20% de desconto para totais acima de R$ 1000."""
        # Arrange
        cart.add_item(product_b, 5)  # 5 * 250 = 1250

        # Act
        total = cart.calculate_total_with_discount()

        # Assert
        assert total == 1000.0  # 1250 * 0.80


# ============================================================
# Casos de Borda (Edge Cases)
# ============================================================


class TestEdgeCases:
    """Testes para cenários de borda e limites."""

    def test_calculate_total_empty_cart(self, cart: ShoppingCart) -> None:
        """Deve retornar 0 para um carrinho vazio."""
        # Arrange
        # (carrinho já está vazio via fixture)

        # Act
        total = cart.calculate_total()

        # Assert
        assert total == 0.0

    def test_calculate_total_with_discount_empty_cart(
        self, cart: ShoppingCart,
    ) -> None:
        """Deve retornar 0 com desconto para um carrinho vazio."""
        # Arrange
        # (carrinho já está vazio via fixture)

        # Act
        total = cart.calculate_total_with_discount()

        # Assert
        assert total == 0.0

    def test_discount_threshold_exactly_500(self, cart: ShoppingCart) -> None:
        """Não deve aplicar desconto quando o total é exatamente R$ 500 (limiar)."""
        # Arrange
        product = Product(id=10, name="Produto Limiar", price=500.0)
        cart.add_item(product, 1)  # total = 500

        # Act
        total = cart.calculate_total_with_discount()

        # Assert
        assert total == 500.0  # sem desconto, pois a regra é > 500

    def test_discount_threshold_exactly_1000(self, cart: ShoppingCart) -> None:
        """Deve aplicar apenas 10% quando o total é exatamente R$ 1000 (limiar)."""
        # Arrange
        product = Product(id=11, name="Produto Limiar Alto", price=500.0)
        cart.add_item(product, 2)  # total = 1000

        # Act
        total = cart.calculate_total_with_discount()

        # Assert
        assert total == 900.0  # 1000 * 0.90 (10% desconto, pois não é > 1000)

    def test_remove_item_from_empty_cart(self, cart: ShoppingCart) -> None:
        """Deve não lançar erro ao remover item de carrinho vazio."""
        # Arrange
        # (carrinho vazio)

        # Act
        cart.remove_item(999)

        # Assert
        assert len(cart.items) == 0

    def test_remove_nonexistent_item(
        self, cart: ShoppingCart, product_a: Product
    ) -> None:
        """Deve manter o carrinho intacto ao remover ID inexistente."""
        # Arrange
        cart.add_item(product_a, 2)

        # Act
        cart.remove_item(999)

        # Assert
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 2
