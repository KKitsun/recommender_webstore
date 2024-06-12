function slider(direction) {
    const recommendation_container_prev = document.getElementById('recommendation_container_prev-btn')
    const recommendation_container_next = document.getElementById('recommendation_container_next-btn')
    const recommendation_container_list = document.getElementById('recommendation_container_item-list')

    const itemWidth = 219
    const padding = 15

    if (direction==='prev') {
        recommendation_container_list.scrollLeft -= itemWidth + padding
    }
    else if ((direction==='next')) {
        recommendation_container_list.scrollLeft += itemWidth + padding
    }
}

function slider2(direction) {
    const recommendation_container_prev = document.getElementById('recommendation_container_prev-btn2')
    const recommendation_container_next = document.getElementById('recommendation_container_next-btn2')
    const recommendation_container_list = document.getElementById('recommendation_container_item-list2')

    const itemWidth = 219
    const padding = 15

    if (direction==='prev') {
        recommendation_container_list.scrollLeft -= itemWidth + padding
    }
    else if ((direction==='next')) {
        recommendation_container_list.scrollLeft += itemWidth + padding
    }
}