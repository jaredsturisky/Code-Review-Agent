function calculateSubtotal(items) {
  var subtotal = 0;
  for (var i = 0; i < items.length; i++) {
    subtotal = subtotal + items[i].price * items[i].qty;
  }
  console.log('subtotal calculated: ' + subtotal);
  return subtotal;
}

function calculateTax(items) {
  var subtotal = 0;
  for (var i = 0; i < items.length; i++) {
    subtotal = subtotal + items[i].price * items[i].qty;
  }
  return subtotal * 0.0825;
}

function calculateOrderTotal(items) {
  const subtotal = calculateSubtotal(items);
  const tax = calculateTax(items);
  return subtotal + tax + 4.99;
}

module.exports = { calculateSubtotal, calculateTax, calculateOrderTotal };
