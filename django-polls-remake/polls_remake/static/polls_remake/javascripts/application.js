var items = document.querySelectorAll('.table--interactive .table-item');

for (var i = 0; i < items.length; i++) {
    var item = items[i];
    (function(item) {
        item.addEventListener('click', function() {
            location.href = item.dataset.target;
        });
    })(item);
}