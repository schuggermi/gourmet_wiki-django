window.initializeSortable = function initializeSortable() {
    const sortable = document.querySelector("#steps");

    if (sortable && !sortable.sortableInstance) {
        console.log("Initializing Sortable");

        sortable.sortableInstance = new Sortable(sortable, {
            animation: 150,
            dragClass: 'text-secondary!',
            handle: '.drag-handle',
            onEnd: function(evt) {
                console.log("Sort ended");

                const items = sortable.querySelectorAll('li[data-step-id]');
                console.log("Found items:", items.length);

                const orderData = Array.from(items).map((item, index) => {
                    console.log("Item:", item.dataset.stepId, "Order:", index + 1);
                    return {
                        id: item.dataset.stepId,
                        order: index + 1
                    };
                });

                console.log("Order data:", orderData);

                if (orderData.length === 0) {
                    console.warn("No items to reorder!");
                    return;
                }

                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                fetch(sortable.getAttribute('hx-post'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken
                    },
                    body: new URLSearchParams({
                        'order': JSON.stringify(orderData)
                    })
                })
                .then(response => {
                    console.log("Response status:", response.status);
                    if (response.ok) {
                        console.log("Reorder successful");
                    } else {
                        console.error("Reorder failed");
                    }
                })
                .catch(error => {
                    console.error("Error:", error);
                });
            }
        });
    }
}

window.addEventListener('load', window.initializeSortable);
