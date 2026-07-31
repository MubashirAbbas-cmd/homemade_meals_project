function getCookie(name) {
    const cookieValue = document.cookie
        .split('; ')
        .find((row) => row.startsWith(name + '='));
    return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : null;
}

function updateCartBadge(totalQty) {
    const badge = document.getElementById('cart-badge');
    if (badge) {
        badge.textContent = totalQty;
    }
}

function updateCartSummary(cart) {
    const totalItems = document.getElementById('cart-total-items');
    const subtotal = document.getElementById('cart-subtotal');
    const total = document.getElementById('cart-total');

    if (totalItems) {
        totalItems.textContent = cart.total_qty;
    }
    if (subtotal) {
        subtotal.textContent = `$${cart.subtotal}`;
    }
    if (total) {
        total.textContent = `$${cart.subtotal}`;
    }
}

function updateCartItemRow(item) {
    const row = document.querySelector(`.cart-item[data-item-id='${item.id}']`);
    if (!row) {
        return;
    }

    const quantityInput = row.querySelector(`.quantity-input[data-item-id='${item.id}']`);
    const lineTotal = row.querySelector(`.item-line-total[data-item-id='${item.id}']`);
    const unitPriceElement = row.querySelector('.unit-price');

    if (quantityInput) {
        quantityInput.value = item.quantity;
    }
    if (lineTotal) {
        lineTotal.textContent = `$${item.line_total}`;
    }
    if (unitPriceElement) {
        unitPriceElement.textContent = `$${item.unit_price}`;
    }
}

function rebuildCartList(items) {
    const cartList = document.getElementById('cart-list');
    if (!cartList) {
        return;
    }

    cartList.innerHTML = items
        .map((item) => `
            <article class="cart-item" data-item-id="${item.id}">
                <img src="" alt="${item.name}">
                <div class="cart-item-info">
                    <h3>${item.name}</h3>
                    <p></p>
                    <div class="cart-item-actions">
                        <div class="quantity-control" data-item-id="${item.id}">
                            <button type="button" class="qty-btn qty-decrease" aria-label="Decrease quantity">-</button>
                            <input type="number" class="quantity-input" data-item-id="${item.id}" value="${item.quantity}" min="0">
                            <button type="button" class="qty-btn qty-increase" aria-label="Increase quantity">+</button>
                        </div>
                        <button type="button" class="btn btn-secondary btn-sm remove-item" data-item-id="${item.id}">Remove</button>
                    </div>
                </div>
                <div class="cart-item-price">
                    <span class="unit-price" data-unit-price="${item.unit_price}">$${item.unit_price}</span>
                    <strong class="item-line-total" data-item-id="${item.id}">$${item.line_total}</strong>
                </div>
            </article>
        `)
        .join('');

    bindCartEventHandlers();
}

function updateCartUI(response) {
    if (!response.success) {
        return;
    }

    updateCartBadge(response.cart.total_qty);
    updateCartSummary(response.cart);

    const cartList = document.getElementById('cart-list');
    if (!cartList) {
        return;
    }

    if (response.cart.items.length === 0) {
        const cartSection = document.querySelector('.cart-section');
        if (cartSection) {
            cartSection.innerHTML = `
                <div class="empty-state" id="cart-empty-state">
                    <h3>Your cart is empty</h3>
                    <p>Add some delicious meals from the menu to start your order.</p>
                    <a href="/" class="btn btn-primary">Browse menu</a>
                </div>
            `;
        }
        return;
    }

    const currentRows = Array.from(cartList.querySelectorAll('.cart-item'));
    const itemIds = response.cart.items.map((item) => String(item.id));

    currentRows.forEach((row) => {
        const rowId = row.dataset.itemId;
        if (!itemIds.includes(rowId)) {
            row.remove();
        }
    });

    response.cart.items.forEach((item) => {
        const row = document.querySelector(`.cart-item[data-item-id='${item.id}']`);
        if (row) {
            updateCartItemRow(item);
        }
    });
}

function sendCartRequest(url, data, callback) {
    const csrftoken = getCookie('csrftoken');
    fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken,
        },
        body: data,
    })
        .then((response) => response.json())
        .then((json) => {
            if (callback) {
                callback(json);
            }
        })
        .catch((error) => {
            console.error('Cart request failed:', error);
        });
}

function bindCartEventHandlers() {
    const addToCartForms = document.querySelectorAll('form.ajax-add-to-cart');
    addToCartForms.forEach((form) => {
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            const url = form.action;
            const formData = new FormData(form);
            sendCartRequest(url, formData, (response) => {
                updateCartUI(response);
            });
        });
    });

    const increaseButtons = document.querySelectorAll('.qty-increase');
    increaseButtons.forEach((button) => {
        button.addEventListener('click', function () {
            const itemId = this.closest('[data-item-id]').dataset.itemId;
            const input = document.querySelector(`.quantity-input[data-item-id='${itemId}']`);
            if (!input) {
                return;
            }
            const nextValue = Math.max(0, parseInt(input.value, 10) + 1);
            input.value = nextValue;
            const formData = new FormData();
            formData.append('quantity', nextValue);
            sendCartRequest(`/cart/update/${itemId}/`, formData, updateCartUI);
        });
    });

    const decreaseButtons = document.querySelectorAll('.qty-decrease');
    decreaseButtons.forEach((button) => {
        button.addEventListener('click', function () {
            const itemId = this.closest('[data-item-id]').dataset.itemId;
            const input = document.querySelector(`.quantity-input[data-item-id='${itemId}']`);
            if (!input) {
                return;
            }
            const nextValue = Math.max(0, parseInt(input.value, 10) - 1);
            input.value = nextValue;
            const formData = new FormData();
            formData.append('quantity', nextValue);
            sendCartRequest(`/cart/update/${itemId}/`, formData, updateCartUI);
        });
    });

    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach((input) => {
        input.addEventListener('change', function () {
            const itemId = this.dataset.itemId;
            const nextValue = Math.max(0, parseInt(this.value, 10) || 0);
            this.value = nextValue;
            const formData = new FormData();
            formData.append('quantity', nextValue);
            sendCartRequest(`/cart/update/${itemId}/`, formData, updateCartUI);
        });
    });

    const removeButtons = document.querySelectorAll('.remove-item');
    removeButtons.forEach((button) => {
        button.addEventListener('click', function () {
            const itemId = this.dataset.itemId;
            const formData = new FormData();
            sendCartRequest(`/cart/remove/${itemId}/`, formData, updateCartUI);
        });
    });
}

window.addEventListener('DOMContentLoaded', function () {
    bindCartEventHandlers();
});
