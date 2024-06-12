let classNameActive = 'shop_container_products_item_button_active';
let buttonLabelAdd = 'Додати в кошик';
let buttonLabelRemove = 'Вилучити з кошика';

function updateCartCounter() {
    const cartCounter = document.getElementById('header_cart_counter');
    if (user === 'AnonymousUser') {
        let counter = 0;
        for (const [key, value] of Object.entries(cart)) {
            counter += value.quantity;
        }
        cartCounter.innerHTML = counter;
    }
    if (parseInt(cartCounter.innerHTML) > 0) {
        cartCounter.style.opacity = 1;
    } else {
        cartCounter.style.opacity = 0;
    }
}
updateCartCounter();

function addItemToCart(element, productId){

    if (user === 'AnonymousUser') {
        addCookieItem(element, productId)
    }
    else {
        addItemToUserOrder(element, productId)
    }

    updateCartCounter();
}

function addItemToUserOrder(element, productId){
    var url = '/add-to-cart/'
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type' : 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body:JSON.stringify({'productId':productId})
    })
    .then((response)=> {
        return response.json();
    })
    .then((data)=> {
        location.reload()
    })
}

function addItemToWishlist(productId){
    var url = '/add-to-wishlist/'
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type' : 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body:JSON.stringify({'productId':productId})
    })
    .then((response)=> {
        return response.json();
    })
    .then((data)=> {
        location.reload()
    })
}

function removeItemFromWishlist(productId){
    var url = '/remove-from-wishlist/'
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type' : 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body:JSON.stringify({'productId':productId})
    })
    .then((response)=> {
        return response.json();
    })
    .then((data)=> {
        location.reload()
    })
}

function cartChangeQuantityUserOrder(productId, action) {
    var url = '/change_quantity/'
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type' : 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body:JSON.stringify({'productId':productId, 'action':action})
    })
    .then((response)=> {
        return response.json();
    })
    .then((data)=> {
        location.reload()
        // updateCartCounter();
    })
    
}

function removeItemUserOrder(productId){
    var url = '/delete_cart_item/'
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type' : 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body:JSON.stringify({'productId':productId})
    })
    .then((response)=> {
        return response.json();
    })
    .then((data)=> {
        location.reload()
    })
}

function addCookieItem(element, productId){

    if (cart[productId] == undefined){
		cart[productId] = {'quantity':1};

        element.classList.add(classNameActive);
        element.innerHTML = buttonLabelRemove;
    } else {
		delete cart[productId];

        element.classList.remove(classNameActive);
        element.innerHTML = buttonLabelAdd;
	}

    document.cookie ='cart=' + JSON.stringify(cart) + ";domain=;path=/"
}

function cartChangeQuantity(productId, action) {

    if (cart[productId] !== undefined) {

        if (action == 'plus' && cart[productId]['quantity'] < 10){
            cart[productId]['quantity'] += 1
        }

        if (action == 'minus'){
            cart[productId]['quantity'] -= 1
            if (cart[productId]['quantity'] <= 0){
                delete cart[productId];
            }
        }

    }

    document.cookie ='cart=' + JSON.stringify(cart) + ";domain=;path=/"
    updateCartCounter();
    location.reload()
    
}

function removeCookieItem(productId){

    if (cart[productId] !== undefined){
		delete cart[productId];
    }

    document.cookie ='cart=' + JSON.stringify(cart) + ";domain=;path=/"
    updateCartCounter();
    location.reload()
}

function addQueryStringParameter(url, key, value) {
    if (value === null || value === undefined) {
        window.location.replace(url);
    }

    value = encodeURIComponent(value);

    var re = new RegExp('([?&])' + key + '=.*?(&|$)', 'i'),
        separator = url.indexOf('?') !== -1 ? '&' : '?';
    if (url.match(re)) {
        window.location.replace(url.replace(re, '$1' + key + '=' + value + '$2'));
    } else {
        window.location.replace(url + separator + key + '=' + value);
    }
}

function rateGame(productId, points) {
    var url = '/rate_game/'
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type' : 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body:JSON.stringify({'productId':productId, 'points':points})
    })
    .then((response)=> {
        return response.json();
    })
    .then((data)=> {
        location.reload()
    })
}