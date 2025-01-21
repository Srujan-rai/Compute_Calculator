function setInputValue(selector, value) {
    const inputField = document.querySelector(selector); // Find the input field using the selector
    if (inputField) {
      inputField.value = value; // Set the desired value
      inputField.dispatchEvent(new Event('input', { bubbles: true })); // Trigger input event
      console.log(`Updated field (${selector}) to:`, value);
    } else {
      console.error(`Field not found for selector: ${selector}`);
    }
  }
  
  // Add your components here
  const components = [
    { selector: '#i6', value: 50 }, // Update "Number of Instances"
    { selector: '[aria-labelledby="ucj-5"]', value: 100 }, // Another example with aria-labelledby
    // Replace with actual selectors and values
  ];
  
  // Loop through components and update values
  components.forEach(component => {
    setInputValue(component.selector, component.value);
  });