// ui.js

exports.createButton = function(label) {
    // Create and return a new button with the given label
    const button = document.createElement('button')
    button.innerHTML = label
    return button
  }
  